import pandas as pd
from nltk.corpus import wordnet as wn

from model import Action


class WordNetHandler:
    def __init__(self):
        csv_act = pd.read_csv('./data/actions.csv')
        self.__synsets = {}
        for idx, row in csv_act.iterrows():
            self.__synsets[row['Name']] = row['Synset']

    def calculate_wup(self, ref_a: Action, gen_a: Action) -> float:
        ref = wn.synset(self.__synsets.get(ref_a.get_name()))
        gen = wn.synset(self.__synsets.get(gen_a.get_name()))
        return ref.wup_similarity(gen)
