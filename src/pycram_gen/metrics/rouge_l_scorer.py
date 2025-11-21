# -*- coding: utf-8 -*-

from rouge import Rouge

def rouge_l(reference: str, generated: str) -> float:
    """
    Calculate ROUGE-L F1-score for given Python programs

    :param reference: The reference code
    :param generated: The generated code
    :returns: ROUGE-L F1-score
    """

    rouge = Rouge()
    # calculate ROUGE scores
    scores = rouge.get_scores(generated, reference)
    # get the dictionary containing results
    score = scores[0]
    # get the ROUGE-L score
    rouge_l_score = score['rouge-l']
    # get the F1-score
    return rouge_l_score['f']
