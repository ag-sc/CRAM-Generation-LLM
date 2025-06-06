from typing import List

import pandas as pd

from model import Action

NO_ACTIONS = 9


def import_actions() -> List[Action]:
    csv_act = pd.read_csv('./data/actions.csv')
    actions = []
    for idx, row in csv_act.iterrows():
        act = Action(row['Name'], str(row["Description"]), str(row['Designator']))
        actions.append(act)
    return actions
