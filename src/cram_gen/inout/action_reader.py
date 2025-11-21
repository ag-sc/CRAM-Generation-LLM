from typing import List

import pandas as pd

from src.cram_gen.model import Action
from src.cram_gen.utils.paths import ACTIONS_FILE

NO_ACTIONS = 9

def import_actions() -> List[Action]:
    csv_act = pd.read_csv(ACTIONS_FILE)
    actions = []
    for idx, row in csv_act.iterrows():
        act = Action(row['Name'], str(row["Description"]), str(row['Designator']))
        actions.append(act)
    return actions
