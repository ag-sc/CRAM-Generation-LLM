from typing import List

from code_bert_score import BERTScorer


def calculate_code_bert_score(gen: List[str], ref: List[str]):
    scorer = BERTScorer(lang="Lisp")
    return scorer.score(gen, ref)
