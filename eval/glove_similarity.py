import torch
import torchtext


def clean_up_verb(verb: str) -> str:
    res = verb.split("-")[0]
    return res.lower()


class GloveHandler:
    def __init__(self):
        self.glove = torchtext.vocab.GloVe(name="6B", dim=50)

    def calculate_cosine(self, gen_act: str, ref_act: str) -> float:
        gen = self.glove[clean_up_verb(gen_act)]
        ref = self.glove[clean_up_verb(ref_act)]
        sim = torch.cosine_similarity(gen.unsqueeze(0), ref.unsqueeze(0)).item()
        #print(f'Cosine Similarity between {gen_act} and {ref_act}: {round(sim, 3)}')
        return sim
