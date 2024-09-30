# -*- coding: utf-8 -*-
"""
Python script for evaluating the designators generated during prompt engineering
using the code metrics.
This is done in two steps:
    - the first step uses the ground truth designator for the same action as
        the generated designator as the reference for computing the metrics
    - the second step uses the reference designator provided in the prompt
        (i.e., the ground truth designator for the reference action)  as the
        reference for computing the metrics

Note that the set of reference designators and the set of ground truth
designators used for the metric computaion are identical! Whether the currently
used reference designator is defined as the "reference" or "ground truth"
only depends on the reference and target actions for the generated designator.

The metric computation always uses the processed versions of the designators,
i.e., the versions without comments and imports.
"""

import os
import pandas as pd

from src.metrics import compilation_success
from src.utils import compute_metrics
from src.enums import Metrics, ResultColumnPromptEngineering
from src.constants import VERBOSE

# list for saving the evaluation results when using the ground truth designator
# as the reference for computing the metrics
scores_target_ground_truth = []

# list for saving the evaluation results when using the reference provided in
# the prompt as the reference for computing the metrics
scores_target_reference = []

# paths of directories containing the generated designators
base_path = "data/prompt_engineering"
path_full = os.path.join(base_path, "full")
path_processed = os.path.join(base_path, "processed")

# path of diretory containing the references and ground truth designators
path_reference = "data/designators/processed"

# get the names of all generated designators
designators = sorted(os.listdir(path_processed))

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

    # check whether the generated designator compiles
    # compiles -> 1; does not compile -> 0
    compilation = int(compilation_success(os.path.join(path_full, fname)))

    # get the generated designator
    with open(os.path.join(path_processed, fname), "r") as f:
        generated = f.read()

    # lines of code in generated designator
    loc = generated.count("\n")

    # get the details from filename
    fname_without_ending = fname.split(".")[0]
    split_name = fname_without_ending.split("_")
    target_action = split_name[0]
    target_detail = split_name[1]
    reference_action = split_name[3]
    reference_detail = split_name[4]

    # Step 1: Compute metrics using the ground truth designator (i.e., the
    # manually written designator for the same action as the target) as reference

    # get the ground truth designator for the target action
    with open(os.path.join(path_reference, target_action+".py"), "r") as f:
        ground_truth = f.read()


    # calculate metrics for ground truth designator and generated designator
    metrics_ground_truth = compute_metrics(ground_truth, generated)

    # save the results in the respective list
    scores_target_ground_truth.append(
            [
               target_action,
               target_detail,
               reference_action,
               reference_detail,
               metrics_ground_truth[Metrics.CHRF.value],
               metrics_ground_truth[Metrics.CODE_BERT_SCORE.value],
               metrics_ground_truth[Metrics.CODE_BLEU.value],
               metrics_ground_truth[Metrics.CRYSTAL_BLEU.value],
               metrics_ground_truth[Metrics.EDIT_DISTANCE.value],
               metrics_ground_truth[Metrics.ROUGE_L.value],
               loc,
               compilation
            ]
        )

    # Step 2: Compute metrics using the reference provided in the prompt
    # during generation as reference

    # get the reference designator
    with open(os.path.join(path_reference, reference_action+".py"), "r") as f:
        reference = f.read()

    # calculate metrics for reference designator and generated designator
    metrics_reference = compute_metrics(reference, generated)

    # save the results in the respective list
    scores_target_reference.append(
            [
               target_action,
               target_detail,
               reference_action,
               reference_detail,
               metrics_reference[Metrics.CHRF.value],
               metrics_reference[Metrics.CODE_BERT_SCORE.value],
               metrics_reference[Metrics.CODE_BLEU.value],
               metrics_reference[Metrics.CRYSTAL_BLEU.value],
               metrics_reference[Metrics.EDIT_DISTANCE.value],
               metrics_reference[Metrics.ROUGE_L.value],
               loc,
               compilation
            ]
        )

    if VERBOSE:
        print("done")


# get the column names for the resulting DataFrames; they are defined
# by the ResultColumnPromptEngineering enum
dataframe_columns = [column.value for column in ResultColumnPromptEngineering]

# generate and save dataframe for metric computation using reference
dataframe_target_reference = pd.DataFrame(scores_target_reference,
                                          columns=dataframe_columns)
dataframe_target_reference.to_csv(os.path.join(base_path,
                                               "results_target_reference.csv"))

# generate and save dataframe for metric computation using ground truth
dataframe_target_ground_truth = pd.DataFrame(scores_target_ground_truth,
                                             columns=dataframe_columns)
dataframe_target_ground_truth.to_csv(os.path.join(base_path,
                                                  "results_target_ground_truth.csv"))
