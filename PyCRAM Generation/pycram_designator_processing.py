#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Python script for processing the designators generated in the experiment
"Generating PyCRAM Designators".
For each designator, the raw version (output from LLM) is used to generate
the full version (adds the common import statements and removes any imports
contained in the output) and the processed version (no imports, comments,
and blak lines).
Processing is performed for all runs of the selected LLM.
Usage:
    $ python3 pycram_designator_processing.py -m [model]
"""

import os
import argparse

from src.utils import (remove_imports, remove_blank_lines, remove_comments,
                           get_model_type_from_model_name)
from src.enums import ModelType
from src.constants import VERBOSE

# argument parser for selecting the model whose results are to be processed
parser = argparse.ArgumentParser(description="Process generated designators")
parser.add_argument("-m", "--model", help="LLM to be evaluated", required=True,
                    choices=[model.value for model in ModelType])
args = parser.parse_args()

# get the ModelType enum element whose value corresponds to the model argument
model = get_model_type_from_model_name(args.model)

# get the common import statements
with open("data/designators/imports.py", "r") as f:
    import_statements = f.read()

# base path for the results of this experiment
base_path = "data/pycram_generation"
# path containing the results for the selected model
model_path = os.path.join(base_path, model.value)

# get the runs performed using this model
runs = sorted(next(os.walk(model_path))[1])

# variables for determining the current progress
if VERBOSE:
    print(f"Processing generated designators, LLM: {model.value}")
    current_num = 1
    total_num = len(runs) * 30

# iterate over the runs performed using this model
for run in runs:
    # determine paths for the 3 versions of the designators generated in this run
    run_path = os.path.join(model_path, run)
    path_raw = os.path.join(run_path, "raw")
    path_full = os.path.join(run_path, "full")
    path_processed = os.path.join(run_path, "processed")

    # create directories for saving the full and processed designators
    os.makedirs(path_full)
    os.makedirs(path_processed)

    # get the file names of the designators generated in this run
    designators = sorted(os.listdir(path_raw))

    # iterate over the generated designators in the current run
    for fname in designators:
        # print current progress
        if VERBOSE:
            print(f"({current_num:3d}/{total_num:3d})", end=" ")
            print(f"run: {run}, file: {fname} ...", end = " ", flush=True)
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
