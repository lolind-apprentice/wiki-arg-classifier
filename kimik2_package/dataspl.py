import pandas as pd
from sklearn.model_selection import train_test_split
from label_nor import normalise_label
df = pd.read_csv("final_cleaned_file.csv")

print("Total rows:", len(df))
# clean whitespace and lower
df["Annotation"] = df["Annotation"].str.strip().str.lower().astype(str)

# drop any rows that have cont'd to be cont'd
df = df[~df["Annotation"].isin(["cont'd", "to be cont'd", "_"])]

df["Annotation"] = (
    df["Annotation"]
    .astype(str)
    .str.strip()
    .str.lower()
    .apply(normalise_label)
)

print(df['Annotation'].value_counts())

print("Normalized rows:", len(df))
# count how many times each label appears
counts = df["Annotation"].value_counts()

# build a True/False mask: True for every row whose label occurs exactly once
df = df[df["Annotation"].isin(counts[counts >= 7].index)].copy()


# 80 / 20 stratified split on the rows whose labels have ≥ 2 examples
train_df, test_df = train_test_split(
    df,
    test_size=0.20,
    random_state=42,
    stratify=df["Annotation"]
)

print(df['Annotation'].value_counts())

# save csvs and sanity check
df.to_csv("my_data.csv", index=False)
train_df.to_csv("train_80.csv", index=False)
test_df.to_csv("test_20.csv", index=False)
print("Train size:", len(train_df))
print("Test  size:", len(test_df))
