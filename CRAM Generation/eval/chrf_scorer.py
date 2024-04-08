from nltk.translate.chrf_score import sentence_chrf


def calculate_chrf(gen: str, ref: str):
    return sentence_chrf(ref, gen)
