import os
from typing import List

import pandas as pd

from src.cram_gen.inout import ResultReader, import_actions, NO_ACTIONS
from src.cram_gen.utils.paths import CRAM_GEN_FOLDER, AVERAGE_RESULTS_FILE


def calculate_averages(runs: int, models: List[str]):
    # Clear the file with the average results per model before appending to it below
    with open(AVERAGE_RESULTS_FILE, 'w') as f:
        pass

    for mt in models:
        average_model_action_specific(mt, runs)
        average_whole_model(mt, runs)


def average_model_action_specific(model_name: str, runs: int):
    from src.cram_gen.model import ResultColumnHeaders
    headers = [h.value for h in ResultColumnHeaders if
               h.value not in (ResultColumnHeaders.model, ResultColumnHeaders.run)]
    metrics = [h for h in headers if h not in (ResultColumnHeaders.gen, ResultColumnHeaders.ref)]
    results = ResultReader.read_all_results()
    avg_df = pd.DataFrame(columns=headers)
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
    file = CRAM_GEN_FOLDER / f'average action results {model_name.lower()}.csv'
    avg_df.to_csv(file, index=False)


def average_whole_model(model_name: str, runs: int):
    from src.cram_gen.model import ResultColumnHeaders
    no_desigs = NO_ACTIONS * (NO_ACTIONS-1) * runs
    metrics = [ResultColumnHeaders.bleu, ResultColumnHeaders.r1, ResultColumnHeaders.r2, ResultColumnHeaders.rl, ResultColumnHeaders.cbs,
               ResultColumnHeaders.chrf, ResultColumnHeaders.loc, ResultColumnHeaders.comp]
    results = ResultReader.read_all_results()
    avg_df = pd.DataFrame(columns=metrics)

    model_results = results[results[ResultColumnHeaders.model] == model_name]
    assert len(model_results) == no_desigs
    for m in metrics:
        avg_val = model_results[m].sum() / no_desigs
        avg_df.loc[0, m] = avg_val
    avg_df.insert(0, 'model', model_name)
    write_header = not os.path.exists(AVERAGE_RESULTS_FILE) or os.path.getsize(AVERAGE_RESULTS_FILE) == 0
    avg_df.to_csv(AVERAGE_RESULTS_FILE, mode='a', header=write_header, index=False)
