import pandas as pd
from scipy.stats.stats import pearsonr


def calculate_correlations(df: pd.DataFrame, fix_col_name: str):
    metrics = ['BLEU', 'ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'CodeBERTScore', 'chrF']

    for m in metrics:
        corr = evaluate_significance(df[fix_col_name], df[m])
        print(f"Correlation between {fix_col_name} and {m} is {corr[1]} (p = {round(corr[2], 3)}) with r = {round(corr[0], 3)}")


def evaluate_significance(col1, col2) -> (float, str, float):
    res = pearsonr(col1, col2)
    if res[1] <= 0.05:
        return res[0], 'significant', res[1]
    else:
        return res[0], 'not significant', res[1]
