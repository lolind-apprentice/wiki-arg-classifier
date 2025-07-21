# viz_results.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import numpy as np
import os
import json

# ------------------------------------------------------------------
# 1. Accuracy per run
# ------------------------------------------------------------------
acc_df = pd.read_csv("run_accuracies.csv")
plt.figure(figsize=(4,3))
sns.barplot(x='run', y='accuracy', data=acc_df, palette='Blues_d')
plt.axhline(acc_df['accuracy'].mean(), color='red', linestyle='--', label=f"Mean: {acc_df['accuracy'].mean():.3f}")
plt.ylim(0, 1)
plt.title("Accuracy per Run")
plt.ylabel("Accuracy")
plt.xlabel("Run #")
plt.legend()
plt.tight_layout()
plt.savefig("runs_accuracy.png", dpi=300)
print("Saved runs_accuracy.png")

# ------------------------------------------------------------------
# 2. Confusion matrix (all 5 runs pooled)
# ------------------------------------------------------------------
# Re-create the pooled predictions/labels from main.py if needed
train_df = pd.read_csv("train_80.csv")
test_df  = pd.read_csv("test_20.csv")
from prompt_cr import build_prompt              # uses same normalisation
from calltogether import predict_one
from tqdm import tqdm

all_preds, all_refs = [], []

prompt = build_prompt(pd.read_csv("train_80.csv"), k=4, seed=42)  # deterministic sample
for _, row in tqdm(test_df.iterrows(), total=len(test_df), desc="Re-predicting"):
    all_preds.append(predict_one(row["Rationals"], prompt))
    all_refs.append(row["Annotation"])

labels = sorted(set(all_refs) | set(all_preds))
cm = confusion_matrix(all_refs, all_preds, labels=labels)

plt.figure(figsize=(4.5,3.5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=labels, yticklabels=labels)
plt.title("Pooled Confusion Matrix (5 runs)")
plt.ylabel("True")
plt.xlabel("Predicted")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=300)
print("Saved confusion_matrix.png")

# ------------------------------------------------------------------
# 3. Optional: per-label F1 bar chart
# ------------------------------------------------------------------
from sklearn.metrics import classification_report
report = classification_report(all_refs, all_preds, output_dict=True)
f1_scores = {k: v['f1-score'] for k, v in report.items() if k in labels}
plt.figure(figsize=(4,3))
sns.barplot(x=list(f1_scores.keys()), y=list(f1_scores.values()), palette='viridis')
plt.ylim(0, 1)
plt.title("F1-score per Label")
plt.ylabel("F1")
plt.xlabel("Label")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("f1_per_label.png", dpi=300)
print("Saved f1_per_label.png")

print("Visualization done.")