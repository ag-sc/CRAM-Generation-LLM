# -*- coding: utf-8 -*-
"""
Python script for computing the k most frequent n-grams among the reference
designators. These are required for computing the CrystalBLEU metric.
"""

from collections import Counter
import numpy as np

from src.utils import get_all_ngrams
from src.constants import CRYSTAL_BLEU_K, TRIVIALLY_SHARED_NGRAMS_LOCATION

# path of directory containing processed designators
path = "data/designators/processed/"

# list of all n-grams contained in the designators
all_ngrams = get_all_ngrams(path)

# get the k most common n-grams, where k has been determines using frequency plot
frequencies = Counter(all_ngrams)
trivially_shared_ngrams = dict(frequencies.most_common(CRYSTAL_BLEU_K))

# save the most common n-grams to npy file
np.save(TRIVIALLY_SHARED_NGRAMS_LOCATION, trivially_shared_ngrams)
