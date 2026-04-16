from typing import List

import pandas as pd
from scipy.stats import pearsonr, spearmanr

from src.cram_gen.utils.paths import CRAM_GEN_FOLDER


def calculate_correlations(models: List[str], use_spearman=True):
    from src.cram_gen.inout import ResultReader
    from src.cram_gen.model import ResultColumnHeaders

    df = ResultReader.read_all_results()
    sim_metrics = [ResultColumnHeaders.wup, ResultColumnHeaders.glove, ResultColumnHeaders.smd]
    gen_metrics = [ResultColumnHeaders.bleu, ResultColumnHeaders.r1, ResultColumnHeaders.r2, ResultColumnHeaders.rl,
                   ResultColumnHeaders.cbs, ResultColumnHeaders.chrf, ResultColumnHeaders.loc, ResultColumnHeaders.comp]

    res_columns = ["metric"] + [column + suffix for column in gen_metrics for suffix in ["_r", "_p"]]

    for m in models:
        print(f"Correlations for model {m}:")
        df_corr_res = pd.DataFrame(columns=res_columns)
        model_df = df[df[ResultColumnHeaders.model] == m.lower()]
        for sm in sim_metrics:
            new_row = {"metric": sm}
            for gm in gen_metrics:
                corr = evaluate_significance(model_df[sm], model_df[gm], use_spearman)
                r_val = round(corr[0], 3)
                p_val = round(corr[2], 5)
                print(f"Correlation between {sm} and {gm} is {corr[1]} (p = {p_val}) with r = {r_val}")
                new_row[gm + "_r"] = r_val
                new_row[gm + "_p"] = p_val
            df_corr_res = pd.concat([df_corr_res, pd.DataFrame([new_row])], ignore_index=True)
            print("\n")
        df_corr_res.to_csv(CRAM_GEN_FOLDER / f"correlation_results_{m}.csv", index=False)


def evaluate_significance(col1, col2, use_spearman: bool) -> (float, str, float):
    if use_spearman:
        res = spearmanr(col1, col2)
    else:
        res = pearsonr(col1, col2)

    if res[1] <= 0.05:
        return res[0], 'significant', res[1]
    else:
        return res[0], 'not significant', res[1]
