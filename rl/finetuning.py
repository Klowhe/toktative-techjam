# train_lora_rlhf.py
import os
import torch
import pandas as pd
from transformers import LlamaForCausalLM, LlamaTokenizer
from peft import LoraConfig, get_peft_model


#df is the rl_input.csv

# Scale total_reward to [0,1] for stable training
df['reward_scaled'] = (df['total_reward'] - df['total_reward'].min()) / max(1e-5, df['total_reward'].max() - df['total_reward'].min())

# ---------------------- LOAD BASE LLaMA ----------------------
model_name = "llama3.1:8b"
tokenizer = LlamaTokenizer.from_pretrained(model_name)
base_model = LlamaForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.float16  # training in fp16
)
base_model.train()
device = "cuda" if torch.cuda.is_available() else "cpu"
base_model.to(device)

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
model.print_trainable_parameters()  # only LoRA adapters are trainable

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

# ---------------------- RLHF TRAINING LOOP ----------------------
batch_size = 4
epochs = 3

for epoch in range(epochs):
    df = df.sample(frac=1).reset_index(drop=True)  # shuffle
    print(f"Epoch {epoch+1}/{epochs}")

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        batch_loss = 0.0

        for _, row in batch.iterrows():
            # Prepare input and output
            prompt = row['feature_description'] + "\nRelated regulation:\n" + row['related_regulation']
            output_text = row['ollama_reasoning']
            reward = row['reward_scaled']

            input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
            target_ids = tokenizer(output_text, return_tensors="pt").input_ids.to(device)

            outputs = model(input_ids=input_ids, labels=target_ids)
            logits = outputs.logits

            # Negative log-likelihood per token
            loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = target_ids[:, 1:].contiguous()
            loss_per_token = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
            log_prob = -loss_per_token.mean()

            # Policy gradient surrogate
            policy_loss = -log_prob * reward
            batch_loss += policy_loss

        # Backprop / update LoRA parameters only
        optimizer.zero_grad()
        batch_loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        print(f"Batch {i//batch_size+1}: loss={batch_loss.item():.4f}")

# ---------------------- SAVE MODEL LOCALLY ----------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Model saved locally at {OUTPUT_DIR}")

# ---------------------- UPLOAD MODEL TO GCS ----------------------
client = storage.Client(project=PROJECT_ID)
bucket = client.bucket(GCS_BUCKET)

for root, _, files in os.walk(OUTPUT_DIR):
    for file in files:
        blob = bucket.blob(f"models/{file}")
        blob.upload_from_filename(os.path.join(root, file))

print(f"Model uploaded to gs://{GCS_BUCKET}/models/")
