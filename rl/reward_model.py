import pandas as pd
import numpy as np

# ---------------------- Load Excel ----------------------
df_classification = pd.read_csv("/Users/zerongpeh/Desktop/Y4S1/hackathon_documents/features_analysis.csv")
df_reasoning = pd.read_excel("/Users/zerongpeh/Desktop/Y4S1/hackathon_documents/features_dataset_with_ollama_reasoning.xlsx",keep_default_na=False, na_values=[])
df = pd.read_excel("/Users/zerongpeh/Desktop/Y4S1/hackathon_documents/tiktok_dataset.xlsx")

# ---------------------- Compute total reward ----------------------
# Use human-provided reasoning score directly
# Combine with classification score to get total reward
alpha = 0.8  # weight for reasoning
beta = 0.2   # weight for classification

df['ollama_reasoning'] = df_reasoning['ollama_reasoning']
df['related_regulation'] = df_reasoning['related_regulation']

df_reasoning["Grade"] = pd.to_numeric(df_reasoning["Grade"], errors="coerce")
df_classification["reward"] = pd.to_numeric(df_classification["reward"], errors="coerce")

df['total_reward'] = alpha * df_reasoning['Grade'] + beta * df_classification['reward']

# ---------------------- Inspect ----------------------
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

df.to_csv("rl_input.csv", index=False)
