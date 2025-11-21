# -*- coding: utf-8 -*-

import code_bert_score as cbs

def code_bert_score(reference: str, generated: str) -> float:
    """
    Calculate CodeBERTScore F1-score for given Python programs

    :param reference: The reference code
    :param generated: The generated code
    :returns: CodeBERTScore F1-score
    """

    # calculate CodeBERTScore
    score = cbs.score([generated], [reference], lang="Python")
    # F1-score is the third value
    f_score = score[2]
    return f_score.item()
