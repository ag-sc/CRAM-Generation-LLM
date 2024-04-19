# -*- coding: utf-8 -*-

import numpy as np
from crystalbleu import corpus_bleu

from .tokenizer import tokenize
from ..constants import TRIVIALLY_SHARED_NGRAMS_LOCATION

def crystal_bleu(reference: str, generated: str) -> float:
    """
    Calculate CrystalBLEU score for given Python programs

    :param reference: The reference code
    :param generated: The generated code
    :param trivially_shared_ngrams: The previously determined most common
        n-grams of all reference designators
    :returns: CrystalBLEU score
    """

    # tokenize reference and generated programs
    ref_tokens = tokenize(reference)
    gen_tokens = tokenize(generated)

    # get the trivially shared ngrams
    trivially_shared_ngrams = np.load(TRIVIALLY_SHARED_NGRAMS_LOCATION,
                                          allow_pickle=True).item()

    # calculate BLEU score, ignoring most frequent ngrams
    crystal_bleu_score = corpus_bleu([[ref_tokens]], [gen_tokens],
                                         ignoring=trivially_shared_ngrams)

    return crystal_bleu_score
