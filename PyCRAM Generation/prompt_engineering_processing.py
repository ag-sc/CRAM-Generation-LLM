# -*- coding: utf-8 -*-
"""
Python script for preprocessing the designators generated during the prompt
engineering experiment.
Each designator is saved in three copies:
    - the raw designator as output by the LLM
    - the full designator contains all the common import statements (all
     import statements added by the LLM are removed)
    - the processed designator contains no comments and blank lines
"""

import os

from src.utils import remove_imports, remove_blank_lines, remove_comments
from src.constants import VERBOSE

# paths of directories for the prompt engineering designators
base_path = "data/prompt_engineering/"
path_raw = os.path.join(base_path, "raw")
path_full = os.path.join(base_path, "full")
path_processed = os.path.join(base_path, "processed")

# create the directories for saving the newly created designators
os.mkdir(path_full)
os.mkdir(path_processed)

# get the common import statements
with open("data/designators/imports.py", "r") as f:
    import_statements = f.read()

# get the file names of the designators which were generated during
# the prompt engineering experiment
designators = os.listdir(path_raw)

# variables for determining the current progress
if VERBOSE:
    current_num = 1
    total_num = len(designators)

# iterate over all the generated designators
for fname in designators:
    # print current progress
    if VERBOSE:
        print(f"({current_num:2d}/{total_num:2d})", end=" ")
        print(f"file: {fname} ...", end = " ", flush=True)
        current_num += 1

    # get the generated designator
    with open(os.path.join(path_raw, fname), "r") as f:
        designator = f.read()

    # remove any import statements in the generated designator
    designator = remove_imports(designator)

    # a full designator contains the common import statements and the
    # generated designator
    full_designator = import_statements + "\n" + designator

    # write the full designator
    with open(os.path.join(path_full, fname), "x") as f:
        f.write(full_designator)

    # a processed designator contains no import statements, comments or blank lines
    processed_designator = remove_comments(designator)
    processed_designator = remove_blank_lines(processed_designator)

    # write the processed designator
    with open(os.path.join(path_processed, fname), "x") as f:
        f.write(processed_designator)

    if VERBOSE:
        print("done")
