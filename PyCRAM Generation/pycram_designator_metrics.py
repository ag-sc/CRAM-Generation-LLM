#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Python script for evaluating the designators generated in the experiment
"Generating PyCRAM Designators" using the code metrics.
The evaluation is performed (1) using the respective ground truth designator as
the reference and (2) using the reference provided in the prompt as the reference.
Detailed description in prompt_engineering_metrics.py
Usage:
    $ python3 pycram_designator_metrics.py -m [model]
"""

import os
import argparse
import math
import pandas as pd

from src.metrics import compilation_success
from src.utils import compute_metrics, get_model_type_from_model_name
from src.enums import Metrics, ModelType, ResultColumnPycram
from src.constants import VERBOSE

# argument parser for selecting the model whose results are to be evaluated
parser = argparse.ArgumentParser(description="Compute code metrics for the " +
                                 "generated designators")
parser.add_argument("-m", "--model", help="LLM to be evaluated", required=True,
                    choices=[model.value for model in ModelType])
args = parser.parse_args()

# get the ModelType enum element whose value corresponds to the model argument
model = get_model_type_from_model_name(args.model)

# lists for saving the results of the code metric computation using the
# ground truth/reference designator as the reference for the metrics
scores_target_ground_truth = []
scores_target_reference = []

# get the path for the results generated using this model
base_path = "data/pycram_generation"
model_path = os.path.join(base_path, model.value)

# get the runs performed using this model
runs = sorted(next(os.walk(model_path))[1])

# path for the reference designators
path_reference = "data/designators/processed"

# variables for determining the current progress
if VERBOSE:
    print(f"Computing metrics for generated designators, LLM: {model.value}")
    current_num = 1
    total_num = len(runs) * 30

# iterate over the runs performed using this model
for run in runs:
    # determine paths for the full and processed generated designators
    run_path = os.path.join(model_path, run)
    path_full = os.path.join(run_path, "full")
    path_processed = os.path.join(run_path, "processed")

    # get the file names of the designators generated in this run
    designators = sorted(os.listdir(path_processed))

    # iterate over the generated designators
    for fname in designators:

        # print current progress
        if VERBOSE:
            print(f"({current_num:3d}/{total_num:3d})", end=" ")
            print(f"run: {run}, file: {fname} ...", end = " ", flush=True)
            current_num += 1

        # check whether the generated designator compiles
        compilation = int(compilation_success(os.path.join(path_full, fname)))

        # get the processed version of the generated designator
        with open(os.path.join(path_processed, fname), "r") as f:
            generated = f.read()

        # lines of code in the generated designator
        loc = generated.count("\n")

        # get the reference and target action names from the file name
        fname_without_ending = fname.split(".")[0]
        split_name = fname_without_ending.split("_")
        target_action = split_name[0]
        reference_action = split_name[2]

        # get the ground truth designator for the target action
        with open(os.path.join(path_reference, target_action+".py"), "r") as f:
            ground_truth = f.read()

        # calculate metrics for ground truth designator and generated designator
        metrics_ground_truth = compute_metrics(ground_truth, generated)

        # save the results in the respective list
        scores_target_ground_truth.append(
                [
                    target_action,
                    reference_action,
                    run.split("_")[-1],
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

        # get the reference designator provided in the prompt
        with open(os.path.join(path_reference, reference_action+".py"), "r") as f:
            reference = f.read()

        # calculate metrics for reference designator and generated desingator
        metrics_reference = compute_metrics(reference, generated)

        # save the results in the respective list
        scores_target_reference.append(
                [
                    target_action,
                    reference_action,
                    run.split("_")[-1],
                    metrics_reference[Metrics.CHRF.value],
                    metrics_reference[Metrics.CODE_BERT_SCORE.value],
                    metrics_reference[Metrics.CODE_BLEU.value],
                    metrics_reference[Metrics.CRYSTAL_BLEU.value],
                    metrics_reference[Metrics.EDIT_DISTANCE.value],
                    metrics_reference[Metrics.ROUGE_L.value],
                    loc,
                    compilation,
                    math.nan,
                    math.nan
                ]
            )

        if VERBOSE:
            print("done")

# names of the columns are defined by the ResultColumnPycram enum
dataframe_columns = [column.value for column in ResultColumnPycram]

# generate and save dataframe for metric computation using reference
dataframe_target_reference = pd.DataFrame(scores_target_reference,
                                          columns=dataframe_columns)
dataframe_target_reference.to_csv(os.path.join(model_path,
                                               "results_target_reference.csv"),
                                    na_rep="NaN")

# generate and save dataframe for metric computation using ground truth
dataframe_target_ground_truth = pd.DataFrame(scores_target_ground_truth,
                                             columns=dataframe_columns)
dataframe_target_ground_truth.to_csv(os.path.join(model_path,
                                                  "results_target_ground_truth.csv"),
                                        na_rep="NaN")
