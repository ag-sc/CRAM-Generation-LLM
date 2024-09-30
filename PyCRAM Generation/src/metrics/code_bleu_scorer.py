# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

# -*- coding: utf-8 -*-

import os

from .tokenizer import tokenize
from ..constants import CODE_BLEU_PARAMETERS
from .code_bleu import corpus_bleu, weighted_corpus_bleu, corpus_syntax_match, corpus_dataflow_match

def code_bleu(reference: str, generated: str) -> float:
    """
    Calculate CodeBLEU score for given Python programs

    :param reference: The reference code
    :param generated: The generated code
    :returns: CodeBLEU score
    """

    # set the programming language
    lang = "python"

    # tokenize reference and generated programs
    ref_tokens = [[tokenize(reference)]]
    gen_tokens = [tokenize(generated)]

    # calculate BLEU score
    ngram_match_score = corpus_bleu(ref_tokens, gen_tokens)

    # get the Python specific keywords
    cur_dir = os.path.dirname(__file__)
    rel_path = 'code_bleu/keywords/' + lang + '.txt'
    abs_path = os.path.join(cur_dir, rel_path)
    keywords = [x.strip() for x in open(abs_path ,'r', encoding='utf-8').readlines()]

    # calculate weights for tokens; keywords are given higher weight
    def make_weights(reference_tokens, key_word_list):
        return {token:1 if token in key_word_list else 0.2 \
                for token in reference_tokens}

    tokenized_refs_with_weights = [[[reference_tokens, make_weights(reference_tokens, keywords)]\
                for reference_tokens in reference] for reference in ref_tokens]

    # calculate weighted BLEU score
    weighted_ngram_match_score = weighted_corpus_bleu(tokenized_refs_with_weights, gen_tokens)

    # calculate syntax match score
    syntax_match_score = corpus_syntax_match([[reference]], [generated], lang)

    #calculate dataflow match score
    dataflow_match_score = corpus_dataflow_match([[reference]], [generated], lang)

    # get constant parameters; values set as recommended in paper
    alpha = CODE_BLEU_PARAMETERS[0]
    beta = CODE_BLEU_PARAMETERS[1]
    gamma = CODE_BLEU_PARAMETERS[2]
    theta = CODE_BLEU_PARAMETERS[3]

    # calculate CodeBLEU score
    code_bleu_score = alpha*ngram_match_score\
                + beta*weighted_ngram_match_score\
                + gamma*syntax_match_score\
                + theta*dataflow_match_score

    return code_bleu_score
