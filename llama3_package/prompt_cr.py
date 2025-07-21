# function helper: build few-shot prompt text
import pandas as pd
from label_nor import normalise_label
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

enc = SentenceTransformer("all-MiniLM-L6-v2")
train_df = pd.read_csv("train_80.csv")

def diverse_sample(df, label, k):
    rows = df[df.Annotation == label]
    if len(rows) <= k:
        return rows
    vecs = enc.encode(rows.Rationals.tolist())
    kmeans = KMeans(n_clusters=k, random_state=0).fit(vecs)
    # pick one row per cluster
    chosen_idx = [rows.index[i] for i in kmeans.labels_]
    return df.loc[chosen_idx].drop_duplicates()[:k]



LABELS = sorted(train_df["Annotation"].dropna().unique())
K_EXAMPLES   = 8               # rows per label for few-shot
RANDOM_STATE = 42            # None ⇒ fresh sample each run,  so we get different 

def build_prompt(train_df, k=K_EXAMPLES, seed=RANDOM_STATE): # seed is so it gets different examples every time
    """
    Build a perfectly balanced k-shot prompt:
    * normalise labels first
    * up-sample or down-sample every label to exactly k rows
    """
    # 1. normalise labels
    train_df = train_df.copy()

    LABELS = sorted(train_df["Annotation"].dropna().unique())

    cot_examples = []
    for lbl in LABELS:
        rows = train_df[train_df["Annotation"] == lbl]
        # 2. RE-SAMPLE to exactly k rows (with replacement if < k)
        n_needed = k
    
        chosen = diverse_sample(train_df, lbl, n_needed)



        for _, row in chosen.iterrows():
            reason = str(row["Notes"]).strip() or f"The sentence discusses {lbl}."
            cot_examples.append(
                f"Sentence: {row['Rationals']}\n"
                f"Reasoning: {reason}\n"
                f"Label: {lbl}\n"
            )
    prompt = (
        "You are a Wikipedia discussion analyst.\n"
        f"TASK: Classify the sentence into ONE of these labels: {', '.join(LABELS)}\n"
        "DEFINITIONS:\n"
        "- fact: verifiable statement that can be checked against sources\n"
        "- value: subjective opinion or judgement\n"
        "- policy: explicit citation of Wikipedia policy or guideline\n"
        "- editorial process: suggestion on improving or maintaining the article\n"
        "- other: anything else (agreement, off-topic, etc.)\n"
            "INSTRUCTIONS:\n"
        "1. Think step by step in at most two sentences.\n"
        "2. Output only a valid JSON object: {\"label\": \"<label>\"}"
        "Examples:\n" + "\n".join(cot_examples) 
    )
    return prompt
