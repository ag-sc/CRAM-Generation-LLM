import pandas as pd

from inout import ResultReader, import_actions


def calculate_averages():
    from model import ModelType
    for mt in ModelType:
        average_specific_model(mt)


def average_specific_model(model_name: str):
    from model import ResultColumnHeaders
    no_runs = 5
    metrics = [ResultColumnHeaders.wup, ResultColumnHeaders.glove, ResultColumnHeaders.smd, ResultColumnHeaders.bleu, ResultColumnHeaders.r1,
               ResultColumnHeaders.r2, ResultColumnHeaders.rl, ResultColumnHeaders.cbs, ResultColumnHeaders.chrf, ResultColumnHeaders.loc]
    results = ResultReader.read_all_results()
    avg_df = pd.DataFrame(columns=metrics)
    avg_df[ResultColumnHeaders.gen] = ""
    avg_df[ResultColumnHeaders.ref] = ""
    actions = import_actions()

    row_count = 0
    for ref_a in actions:
        for gen_a in actions:
            if ref_a is gen_a:
                continue
            ref = ref_a.get_name()
            gen = gen_a.get_name()
            avg_df.loc[row_count, ResultColumnHeaders.gen] = gen
            avg_df.loc[row_count, ResultColumnHeaders.ref] = ref
            runs = results[(results[ResultColumnHeaders.gen] == gen) & (results[ResultColumnHeaders.ref] == ref) &
                           (results[ResultColumnHeaders.model] == model_name)]
            assert len(runs) == no_runs
            for m in metrics:
                val = 0.0
                for idx, row in runs.iterrows():
                    val += row[m]
                avg_val = val / no_runs
                avg_df.loc[row_count, m] = avg_val
            row_count += 1
    avg_df.to_csv(f'./data/results/average results {model_name}.csv')
