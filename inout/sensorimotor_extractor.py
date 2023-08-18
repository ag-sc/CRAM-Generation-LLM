import pandas as pd


def get_dist_for_action_combination(ref: str, gen: str) -> float:
    dist_csv = pd.read_csv('./data/sensorimotor distance.csv')
    filtered = list(dist_csv.loc[(dist_csv['Word 1'] == ref.lower()) & (dist_csv['Word 2'] == gen.lower())]['Cosine distance'])
    if len(filtered) == 0:
        return 0.0
    else:
        return filtered[0]
