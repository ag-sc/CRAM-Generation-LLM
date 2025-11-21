# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn

def wu_palmer_similarity(reference: str, generated: str) -> float:
    """
    Calculate Wu-Palmer-Similarity between the given WordNet synsets.

    :param reference: Synset for the reference action
    :param generated: Synset for the generated action
    :returns: Wu-Palmer-Similarity
    """

    reference_synset = wn.synset(reference)
    generated_synset = wn.synset(generated)

    similarity = reference_synset.wup_similarity(generated_synset)
    return similarity
