from scipy.stats import pearsonr, spearmanr


def calculate_correlations(model_name: str, fix_col_name: str, use_spearman=True):
    from inout import ResultReader
    from model import ResultColumnHeaders

    df = ResultReader.read_all_results()
    model_df = df[df[ResultColumnHeaders.model] == model_name]
    metrics = [ResultColumnHeaders.bleu, ResultColumnHeaders.r1, ResultColumnHeaders.r2, ResultColumnHeaders.rl, ResultColumnHeaders.cbs,
               ResultColumnHeaders.chrf, ResultColumnHeaders.loc, ResultColumnHeaders.comp]

    print(f"Calculating the correlation to the {fix_col_name} metric for the {model_name} model:")
    for m in metrics:
        corr = evaluate_significance(model_df[fix_col_name], model_df[m], use_spearman)
        print(f"Correlation to {m} is {corr[1]} (p = {round(corr[2], 5)}) with r = {round(corr[0], 3)}")
    print("\n")


def evaluate_significance(col1, col2, use_spearman: bool) -> (float, str, float):
    if use_spearman:
        res = spearmanr(col1, col2)
    else:
        res = pearsonr(col1, col2)

    if res[1] <= 0.05:
        return res[0], 'significant', res[1]
    else:
        return res[0], 'not significant', res[1]
