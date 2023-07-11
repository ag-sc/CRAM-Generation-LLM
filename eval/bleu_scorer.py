import re
from typing import List
from nltk.translate.bleu_score import sentence_bleu


def calculate_bleu(gen: str, ref: str) -> float:
    gen_tokens = tokenize(gen)
    ref_tokens = tokenize(ref)
    return sentence_bleu([ref_tokens], gen_tokens)


def tokenize(code: str) -> List[str]:
    code = re.sub(r'([^A-Za-z0-9_])', r' \1 ', code)
    tokens = [t for t in code.split(' ') if t]
    return tokens
