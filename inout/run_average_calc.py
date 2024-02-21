import pandas as pd

from inout import ResultReader, import_actions, NO_ACTIONS


def calculate_averages(runs: int):
    from model import ModelType
    for mt in ModelType:
        average_model_action_specific(mt, runs)
        average_whole_model(mt, runs)


def average_model_action_specific(model_name: str, runs: int):
    from model import ResultColumnHeaders
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
            runs_df = results[(results[ResultColumnHeaders.gen] == gen) & (results[ResultColumnHeaders.ref] == ref) &
                              (results[ResultColumnHeaders.model] == model_name)]
            assert runs_df.shape[0] == runs
            for m in metrics:
                val = 0.0
                for idx, row in runs_df.iterrows():
                    val += row[m]
                avg_val = val / runs
                avg_df.loc[row_count, m] = avg_val
            row_count += 1
    avg_df.to_csv(f'./data/results/average action results {model_name}.csv')


def average_whole_model(model_name: str, runs: int):
    from model import ResultColumnHeaders
    no_desigs = NO_ACTIONS * (NO_ACTIONS-1) * runs
    metrics = [ResultColumnHeaders.bleu, ResultColumnHeaders.r1, ResultColumnHeaders.r2, ResultColumnHeaders.rl, ResultColumnHeaders.cbs,
               ResultColumnHeaders.chrf]
    results = ResultReader.read_all_results()
    avg_df = pd.DataFrame(columns=metrics)

    model_results = results[results[ResultColumnHeaders.model] == model_name]
    assert len(model_results) == no_desigs
    for m in metrics:
        val = 0.0
        for idx, row in model_results.iterrows():
            val += row[m]
        avg_val = val / no_desigs
        avg_df.loc[0, m] = avg_val
    avg_df.to_csv(f'./data/results/average results {model_name}.csv')

