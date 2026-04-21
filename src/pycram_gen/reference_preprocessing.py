# -*- coding: utf-8 -*-
"""
Preprocess reference designators in data/designators by removing comments,
docstrings, and blank lines.
Save the processed designators to data/designators/processed .
"""

import os

from src.pycram_gen.models.constants import ACTIONS, VERBOSE
from src.pycram_gen.models.utils import remove_blank_lines, remove_comments

# path of the directory containing reference designators
path = "data/designators/"

# iterate over all actions
for action in ACTIONS:
    if VERBOSE:
        print(action)
    # read the reference designator
    with open(os.path.join(path, action+".py"), "r") as f:
        designator = f.read()
    # process the designator
    processed = remove_blank_lines(remove_comments(designator))
    # write the processed designator
    with open(os.path.join(path, "processed", action+".py"), "x") as f:
        f.write(processed)
