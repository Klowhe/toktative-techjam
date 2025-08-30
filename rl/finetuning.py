
# train_lora_rlhf_aws.py
import os
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
from dotenv import load_dotenv
load_dotenv()

# ---------------------- CONFIG ----------------------
MODEL_ID = "meta-llama/LLaMA-3.1-8B"  # Hugging Face model
OUTPUT_DIR = "models/llama3.1-8b-lora-rlhf"
BATCH_SIZE = 4
EPOCHS = 3
LR = 1e-4
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# ---------------------- LOAD DATA ----------------------
df = pd.read_csv("/Users/zerongpeh/Desktop/Y4S1/hackathon_documents/rl_input.csv")

# Scale total_reward to [0,1] for stable training
df['reward_scaled'] = (df['total_reward'] - df['total_reward'].min()) / max(1e-5, df['total_reward'].max() - df['total_reward'].min())

# ---------------------- LOAD TOKENIZER & BASE MODEL ----------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HUGGINGFACE_API_KEY)
tokenizer.pad_token = tokenizer.eos_token  # LLaMA has no pad token

base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    token=HUGGINGFACE_API_KEY,
    device_map="auto",
    load_in_4bit=True,           # reduce VRAM usage
    torch_dtype=torch.float16
)
base_model.train()
base_model.to(DEVICE)

# ---------------------- APPLY LoRA ----------------------
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()

optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

# ---------------------- TRAINING LOOP ----------------------
for epoch in range(EPOCHS):
    df_shuffled = df.sample(frac=1).reset_index(drop=True)
    print(f"\nEpoch {epoch+1}/{EPOCHS}")

    for i in range(0, len(df_shuffled), BATCH_SIZE):
        batch = df_shuffled.iloc[i:i+BATCH_SIZE]
        batch_loss = 0.0

        # Batch tokenization for speed
        prompts = (batch['feature_description'] + "\nRelated regulation:\n" + batch['related_regulation']).tolist()
        outputs_texts = batch['ollama_reasoning'].tolist()
        rewards = torch.tensor(batch['reward_scaled'].values, dtype=torch.float32, device=DEVICE)

        inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True, max_length=512).to(DEVICE)
        targets = tokenizer(outputs_texts, return_tensors="pt", padding=True, truncation=True, max_length=512).to(DEVICE)

        outputs = model(input_ids=inputs.input_ids, attention_mask=inputs.attention_mask, labels=targets.input_ids)
        logits = outputs.logits

        # Compute policy gradient surrogate loss
        loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
        shift_logits = logits[:, :-1, :].contiguous()
        shift_labels = targets.input_ids[:, 1:].contiguous()
        loss_per_token = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        log_prob = -loss_per_token.mean()
        policy_loss = -log_prob * rewards.mean()  # scale by batch mean reward
        batch_loss += policy_loss

        # Backprop / update LoRA parameters only
        optimizer.zero_grad()
        batch_loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        print(f"Batch {i//BATCH_SIZE + 1}/{(len(df_shuffled)+BATCH_SIZE-1)//BATCH_SIZE}: loss={batch_loss.item():.4f}")

# ---------------------- SAVE MODEL ----------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"\nModel saved locally at {OUTPUT_DIR}")
