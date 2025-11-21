import pandas as pd
from nltk.corpus import wordnet as wn

from src.cram_gen.utils.paths import ACTIONS_FILE


class WordNetHandler:
    def __init__(self):
        csv_act = pd.read_csv(ACTIONS_FILE)
        self.__synsets = {}
        for idx, row in csv_act.iterrows():
            self.__synsets[row['Name']] = row['Synset']

    def calculate_wup(self, ref_a: str, gen_a: str) -> float:
        ref = wn.synset(self.__synsets.get(ref_a))
        gen = wn.synset(self.__synsets.get(gen_a))
        return ref.wup_similarity(gen)
