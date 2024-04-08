from enum import Enum


class ResultColumnHeaders(str, Enum):
    gen = 'Generated'
    ref = 'Reference'
    model = 'Model'
    run = 'Run'
    wup = 'WuP'
    glove = 'GloVe-Similarity'
    smd = 'Sensorimotor Distance'
    bleu = 'BLEU'
    r1 = 'ROUGE-1'
    r2 = 'ROUGE-2'
    rl = 'ROUGE-L'
    cbs = 'CodeBERTScore'
    chrf = 'chrF'
    loc = 'LoC'
    comp = 'Compilation'
