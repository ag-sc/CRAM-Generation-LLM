#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Python script for evaluating the designators generated in the experiment
"Converting CRAM Designators into PyCRAM Designators" using the code metrics.
For each generated designator the code metrics are computed using the
respective PyCRAM ground truth designator as the reference.
Usage:
    $ python3 cram_conversion_metrics.py -m [model]
"""

import os
import argparse
import math
import pandas as pd

from src.metrics import compilation_success
from src.utils import compute_metrics, get_model_type_from_model_name
from src.enums import Metrics, ModelType, ResultColumnCram
from src.constants import VERBOSE

# argument parser for selecting the model whose results are to be evaluated
parser = argparse.ArgumentParser(description="Compute code metrics for the " +
                                 "generated designators")
parser.add_argument("-m", "--model", help="LLM to be evaluated", required=True,
                    choices=[model.value for model in ModelType])
args = parser.parse_args()

# get the ModelType enum element whose value corresponds to the model argument
model = get_model_type_from_model_name(args.model)

# list for saving the results of the code metric computation using the
# respective PyCRAM ground truth designator as the reference for the metrics
scores_target_ground_truth = []

# get the path for the results generated using this model
base_path = "data/cram_conversion"
model_path = os.path.join(base_path, model.value)

# determine paths for the full and processed designators
path_full = os.path.join(model_path, "full")
path_processed = os.path.join(model_path, "processed")

# path for the reference designators
path_reference = "data/designators/processed"

# get the file names of the designators generated using this model
designators = sorted(os.listdir(path_processed))

# variables for determining the current progress
if VERBOSE:
    print(f"Computing metrics for generated designators, LLM: {model.value}")
    current_num = 1
    total_num = len(designators)

# iterate over the designators generated using this model
for fname in designators:

    # print the current progress
    if VERBOSE:
        print(f"({current_num:2d}/{total_num:2d})", end=" ")
        print(f"file: {fname} ...", end = " ", flush=True)
        current_num += 1

    # check whether the generated designator compiles
    compilation = int(compilation_success(os.path.join(path_full, fname)))

    # get the processed version of the generated designator
    with open(os.path.join(path_processed, fname), "r") as f:
        generated = f.read()

    # lines of code in the generated designator
    loc = generated.count("\n")

    # get the action name and run from the file name
    file_name_without_ending = fname.split(".")[0]
    split_name = file_name_without_ending.split("_")
    action_name = split_name[0]
    run = split_name[2]

    # get the ground truth designator for the action
    with open(os.path.join(path_reference, action_name+".py"), "r") as f:
        ground_truth = f.read()

    # calculate metrics for ground truth designator and generated designator
    metrics_ground_truth = compute_metrics(ground_truth, generated)

    # save the results in the respective list
    scores_target_ground_truth.append(
            [
                action_name,
                run,
                metrics_ground_truth[Metrics.CHRF.value],
                metrics_ground_truth[Metrics.CODE_BERT_SCORE.value],
                metrics_ground_truth[Metrics.CODE_BLEU.value],
                metrics_ground_truth[Metrics.CRYSTAL_BLEU.value],
                metrics_ground_truth[Metrics.EDIT_DISTANCE.value],
                metrics_ground_truth[Metrics.ROUGE_L.value],
                loc,
                compilation,
                math.nan,
                math.nan
            ]
        )

    if VERBOSE:
        print("done")

# names of the columns are defined by the ResultColumnCram enum
dataframe_columns = [column.value for column in ResultColumnCram]

# generate and save dataframe for metric computation
dataframe_target_ground_truth = pd.DataFrame(scores_target_ground_truth,
                                             columns=dataframe_columns)
dataframe_target_ground_truth.to_csv(os.path.join(model_path,
                                                  "results_target_ground_truth.csv"),
                                        na_rep="NaN")
