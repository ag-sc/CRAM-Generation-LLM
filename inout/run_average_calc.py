import pandas as pd

from eval import correlation, get_dist_for_action_combination


def calculate_average():
    model_old = "gpt-3.5-turbo-0301"
    model_new = "gpt-3.5-turbo-0613"
    model_gpt4 = "gpt-4-0613"

    print(f'Correlations for the {model_old} model version:')
    df_old = average_specific_model(model_old)
    correlation.calculate_correlations(df_old, 'WuP')
    correlation.calculate_correlations(df_old, 'GloVe-Similarity')
    correlation.calculate_correlations(df_old, 'SensorimotorDistance')

    print(f'\nCorrelations for the {model_new} model version:')
    df_new = average_specific_model(model_new)
    correlation.calculate_correlations(df_new, 'WuP')
    correlation.calculate_correlations(df_new, 'GloVe-Similarity')
    correlation.calculate_correlations(df_new, 'SensorimotorDistance')

    print(f'\nCorrelations for the {model_gpt4} model version:')
    df_gpt4 = average_specific_model(model_gpt4)
    correlation.calculate_correlations(df_gpt4, 'WuP')
    correlation.calculate_correlations(df_gpt4, 'GloVe-Similarity')
    correlation.calculate_correlations(df_gpt4, 'SensorimotorDistance')


def average_specific_model(model_name: str) -> pd.DataFrame:
    no_runs = 5
    no_rows = 72
    metrics = ['GloVe-Similarity', 'BLEU', 'ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'CodeBERTScore', 'chrF']
    experiment_results = [None] * no_runs

    for x in range(no_runs):
        experiment_results[x] = pd.read_csv(f'./data/results/res {model_name} run0{x + 1}.csv')

    avg_df = pd.DataFrame(columns=experiment_results[0].columns)
    avg_df['SensorimotorDistance'] = ""
    for r in range(no_rows):
        gen = experiment_results[0].loc[r, 'Generated']
        ref = experiment_results[0].loc[r, 'Reference']
        avg_df.loc[r, 'Generated'] = gen
        avg_df.loc[r, 'Reference'] = ref
        avg_df.loc[r, 'WuP'] = experiment_results[0].loc[r, 'WuP']
        avg_df.loc[r, 'SensorimotorDistance'] = get_dist_for_action_combination(ref, gen)

        for m in metrics:
            val = 0.0
            for e in range(no_runs):
                val += experiment_results[e].loc[r, m]
            avg_val = val / no_runs
            avg_df.loc[r, m] = avg_val

    avg_df.to_csv(f'./data/average results {model_name}.csv')
    return avg_df
