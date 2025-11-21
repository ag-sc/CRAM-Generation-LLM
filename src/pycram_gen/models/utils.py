# -*- coding: utf-8 -*-

from typing import List, Tuple, Dict
from nltk.util import ngrams

from .metrics import (chrf, code_bert_score, code_bleu, crystal_bleu,
                          edit_distance, rouge_l, tokenize)
from .metrics.code_bleu.parser.utils import remove_comments_and_docstrings
from .constants import ACTIONS
from .enums import Metrics, ModelType

def remove_comments(source: str) -> str:
    """
    Remove comments and docstrings from given Python source code.
    Wrapper function for the function in CodeBLEU's parser

    :param source: Python source code
    :returns: Code without comments and docstrings
    """

    lang = "python"
    return remove_comments_and_docstrings(source, lang)

def remove_imports(source: str) -> str:
    """
    Remove import statements at beginning of given Python source code

    :param source: Python source code
    :returns: Code without import statements at beginning
    """

    # split the code at the line breaks, resulting in a list of lines
    lines = source.split("\n")

    # iterate over the lines
    for i in range(len(lines)):
        # get line without leading/trailing whitespaces
        line = lines[i].strip()
        # if the line contains an import statement remove the line
        if line.startswith("import") or (line.startswith("from") and "import" in line):
            lines[i] = ""
        # if the line contains a function/class definition the beginning of
        # the actual code has been reached; the following lines will not
        # be altered
        elif line.startswith("class") or line.startswith("def"):
            break

    # join the lines together and re-insert line breaks
    output = "\n".join(lines)
    return output

def remove_blank_lines(source: str) -> str:
    """
    Remove blank lines from given Python source code

    :param source: Python source code
    :returns: Code without blank lines
    """

    # split the code at the line breaks, resulting in a list of lines
    lines = source.split("\n")
    # get the number of lines
    n = len(lines)
    # current line number
    i = 0

    # iterate over all lines
    while i < n:
        # get the current line
        line = lines[i]
        # if the current line is blank
        if not line.strip():
            # remove the line
            del lines[i]
            # decrement current line number
            i -= 1
            # decrement number of lines
            n -= 1
        # increment current line number and go to next line
        i += 1

    # join the lines together and re-insert line breaks
    output = "\n".join(lines)
    # insert empty line at end of code
    output += "\n"
    return output

def get_all_ngrams(path: str) -> List[Tuple]:
    """
    Get all the n-grams from the designators in the directory specified by
    the path

    :param path: Path to directory containing designators
    :returns: All n-grams in designators
    """

    # list of all ngrams
    all_ngrams = []

    # iterate over all the actions
    for action in ACTIONS:
        # read the current designator
        with open(path+action+".py", "r") as f:
            designator = f.read()
        # tokenize the designator
        tokenized_designator = tokenize(designator)
        # get the n-grams and add them to the list
        for n in range(1, 5):
            designator_ngrams = list(ngrams(tokenized_designator, n))
            all_ngrams.extend(designator_ngrams)

    return all_ngrams

def compute_metrics(reference: str, generated:str) -> Dict[int, float]:
    """
    Compute all metrics for given pair of Python code and return scores
    as dictionary

    :param reference: The reference code
    :param generated: The generated code
    :returns: Dictionary containing the results
    """

    chrf_score = chrf(reference, generated)
    code_bert_score_score = code_bert_score(reference, generated)
    code_bleu_score = code_bleu(reference, generated)
    crystal_bleu_score = crystal_bleu(reference, generated)
    edit_distance_score = edit_distance(reference, generated)
    rouge_l_score = rouge_l(reference, generated)

    return {
                Metrics.CHRF.value: chrf_score,
                Metrics.CODE_BERT_SCORE.value: code_bert_score_score,
                Metrics.CODE_BLEU.value: code_bleu_score,
                Metrics.CRYSTAL_BLEU.value: crystal_bleu_score,
                Metrics.EDIT_DISTANCE.value: edit_distance_score,
                Metrics.ROUGE_L.value: rouge_l_score
            }

def get_model_type_from_model_name(model_name: str) -> ModelType:
    """
    Get the element of the ModelType enum whose value corresponds to
    the given model name

    :param model_name: Name of the model
    :return: Element of ModelType enum whose value is the model name
    """

    return [model for model in ModelType if model.value==model_name][0]
