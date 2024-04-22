# -*- coding: utf-8 -*-

from typing import Final, List, Dict, Set, FrozenSet

VERBOSE: Final[bool] = True

CODE_BLEU_PARAMETERS: Final[List[float]] = [0.1, 0.1, 0.4, 0.4]

CRYSTAL_BLEU_K: Final[int] = 300

TRIVIALLY_SHARED_NGRAMS_LOCATION: Final[str] = "data/trivially_shared_ngrams.npy"

ACTIONS: Final[List[str]] = ["cut", "grasp", "mix", "pour", "transport", "wipe"]

CRAM_ACTIONS: Final[List[str]] = ["cut", "pour", "wipe"]

CLOSER_COLUMN_NAME: Final[str] = "Closer to reference by n metrics"

REFERENCE_DETAIL: Final[Dict[str, str]] = {
            "cut": "1",
            "grasp": "3",
            "mix": "2",
            "pour": "2",
            "transport": "2",
            "wipe": "3"
        }

TARGET_DETAIL: Final[str] = "3"

SAME_AUTHOR_ACTIONS: Final[Set[FrozenSet]] = set([
            frozenset(["cut", "mix"]),
            frozenset(["grasp", "transport"]),
            frozenset(["pour", "wipe"])
        ])
