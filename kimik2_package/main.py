import os, random, numpy as np, pandas as pd
from sklearn.metrics import classification_report, accuracy_score
from tqdm import tqdm
import time, random
from label_nor import normalise_label
from prompt_cr import build_prompt
from calltogether import predict_one 
from sklearn.model_selection import StratifiedKFold


# configuration
N_RUNS       = 5               # seeds → mean ± std. Model runs more times to get statistics
RANDOM_STATE = None            # None ⇒ fresh sample each run,  so we get different 
K_EXAMPLES = 4
# load data
# merge columns in train_df so we have a reasoning for the label chosen 
train_df = pd.read_csv("train_80.csv")
# skip NaNs, use period
train_df['Annotation merged'] = train_df[['Annotation', 'Notes']].astype(str).agg(lambda x: '. '.join(x.dropna()), axis=1)
# load data
test_df  = pd.read_csv("test_20.csv")
clean_labels = sorted({normalise_label(l) for l in test_df["Annotation"].dropna().unique()})

# run N_RUNS times
# lists to collect 
accuracies, all_preds, all_refs = [], [], []
for run_id in range(N_RUNS): # run 5 times to get accuracy
    # fresh prompt every run if seed=None, different rows per label
    seed_this_run = random.randint(0, 9999)
    prompt = build_prompt(train_df, k=K_EXAMPLES, seed=seed_this_run)
    print(prompt)
    # lists to save info
    preds, refs = [], []
    # tqdm is a bar progress to see what is going on
    for _, row in tqdm(test_df.iterrows(), total=len(test_df), desc=f"Run {run_id+1}"):
    # predicting the test 
        pred = predict_one(row["Rationals"], prompt)
        pred = normalise_label(pred)
        preds.append(pred)
        ref = normalise_label(str(row["Annotation"]))  # ← force clean
        refs.append(row["Annotation"])

    # accuracy 
    acc = accuracy_score(refs, preds)
    accuracies.append(acc)
    all_preds.extend(preds)
    all_refs.extend(refs)

clean_labels = sorted(set(refs)) 
acc_df = pd.DataFrame({"run": range(1, N_RUNS + 1),
                       "accuracy": accuracies})
acc_df.to_csv("run_accuracies.csv", index=False)

# 6. aggregate results
print("=== Per-run accuracies ===")
for i, acc in enumerate(accuracies, 1):
    print(f"Run {i}: {acc:.3f}")
print(f"\nMean accuracy: {np.mean(accuracies):.3f} ± {np.std(accuracies):.3f}")
clean_labels = sorted({normalise_label(l) for l in test_df["Annotation"].dropna().unique()})

print("\n=== Macro-averaged report over all runs ===")
print(classification_report(all_refs, all_preds, labels=clean_labels, digits=3))
