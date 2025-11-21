# -*- coding: utf-8 -*-

from re import sub
from typing import List

def tokenize(code: str) -> List[str]:
    """
    Tokenize a Python program

    :param code: The Python code
    :returns: Tokenized code
    """

    code = sub(r'([^A-Za-z0-9_])', r' \1 ', code)
    tokens = [t for t in code.split(' ') if t]
    return tokens
