import itertools
import json
import os

import pandas as pd

from src.cram_gen.utils.paths import ACTIONS_FILE, WORDNET_FILE


class WordNetHandler:
    def __init__(self):
        if os.path.isfile(WORDNET_FILE):
            with open(WORDNET_FILE, "r") as f:
                self._wups = json.load(f)
            csv_act = pd.read_csv(ACTIONS_FILE)
            self._synsets = {row['Name']: row['Synset'] for _, row in csv_act.iterrows()}
        else:
            # Build synsets dictionary
            from nltk.corpus import wordnet as wn
            csv_act = pd.read_csv(ACTIONS_FILE)
            self._synsets = {row['Name']: row['Synset'] for _, row in csv_act.iterrows()}
            self._wups = {}
            action_names = list(self._synsets.keys())
            for a1, a2 in itertools.combinations(action_names, 2):
                ref_synset = wn.synset(self._synsets[a1])
                gen_synset = wn.synset(self._synsets[a2])
                sim = ref_synset.wup_similarity(gen_synset)
                if a1 not in self._wups:
                    self._wups[a1] = {}
                self._wups[a1][a2] = sim
            with open(WORDNET_FILE, "w") as f:
                json.dump(self._wups, f)

    def get_wup_sim(self, ref_a: str, gen_a: str) -> float:
        if ref_a in self._wups and gen_a in self._wups[ref_a]:
            return self._wups[ref_a][gen_a]
        elif gen_a in self._wups and ref_a in self._wups[gen_a]:
            return self._wups[gen_a][ref_a]
        else:
            return 0.0
