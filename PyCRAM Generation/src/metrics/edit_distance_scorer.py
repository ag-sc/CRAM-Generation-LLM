# -*- coding: utf-8 -*-

from pylcs import edit_distance as pylcs_edit_distance

def edit_distance(reference: str, generated: str) -> float:
    """
    Calculate 1 - normalized edit distance for given Python programs

    :param reference: The reference code
    :param generated: The generated code
    :returns: 1 - edit distance normalized by its maximum value, i.e., the
        length of the longer program
    """

    # calculate the edit distance
    ed = pylcs_edit_distance(reference, generated)
    # maximum edit distance is length of the longer program
    max_ed = max(len(reference), len(generated))
    # normalize edit distance
    norm_ed = ed / max_ed

    # return 1 - normalized edit distance
    return 1 - norm_ed
