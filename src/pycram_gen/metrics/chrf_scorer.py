# -*- coding: utf-8 -*-

from nltk.translate.chrf_score import sentence_chrf

def chrf(reference: str, generated: str) -> float:
    """
    Calculate chrF score for given Python programs

    :param reference: The reference code
    :param generated: The generated code
    :returns: chrF score
    """

    # calculate chrF score
    score = sentence_chrf(reference, generated)
    return score
