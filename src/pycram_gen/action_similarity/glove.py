# -*- coding: utf-8 -*-

import torch
import torchtext

def cosine_similarity_glove(reference_action: str, generated_action: str) -> float:
    """
    Calculate cosine similarity using GloVe embeddings for the given actions.

    :param reference_action: Name of the reference action
    :param generated_action: Name of the generated action
    :returns: Cosine similarity using GloVe embeddings for given actions
    """

    cache_path = "src/action_similarity/.vector_cache"
    glove = torchtext.vocab.GloVe(name="6B", dim=50, cache=cache_path)

    reference = glove[reference_action]
    generated = glove[generated_action]

    similarity = torch.cosine_similarity(reference.unsqueeze(0),
                                           generated.unsqueeze(0))
    return similarity.item()
