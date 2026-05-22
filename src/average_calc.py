import pandas as pd

# Load your data
df = pd.read_csv("../data/pycram_generation/llama-3.3-70b-instruct/results_target_ground_truth.csv")

# Select numeric metric columns (adjust if needed)
metric_cols = [
    "chrF",
    "CodeBERTScore",
    "CodeBLEU",
    "CrystalBLEU",
    "Edit Distance",
    "ROUGE-L",
    "LoC",
    "Compilation Success",
    "Run Success"
]

# Compute global averages
averages = df[metric_cols].mean()

print("Overall averages:")
print(averages)