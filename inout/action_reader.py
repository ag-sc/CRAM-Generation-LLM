import pandas as pd
from typing import List
from model import Action


def import_actions() -> List[Action]:
    csv_act = pd.read_csv('./data/actions.csv')
    actions = []
    for idx, row in csv_act.iterrows():
        act = Action(row['Name'], str(row["Description"]), str(row['Designator']))
        actions.append(act)
    return actions
