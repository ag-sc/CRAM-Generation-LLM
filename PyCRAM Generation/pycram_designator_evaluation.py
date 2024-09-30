#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Python script for evaluating the results of the code metric computation and
simulation for the designators generated during the experiment "Generating
PyCRAM Designators".
This is done in the following steps:
    1. Compute correlations between action similarity metrics and the
        code metric results/simulation.
    2. Determine which combination of target/reference action leads to generated
        designators being closer to reference than ground truth.
Usage:
    $ python3 pycram_designator_evaluation.py -m [model]
"""

import os
import argparse
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

from src.utils import get_model_type_from_model_name
from src.enums import ModelType, ResultColumnPycram, ActionSimilarityColumns
from src.constants import VERBOSE, ACTIONS, CLOSER_COLUMN_NAME

# argument parser for selecting the model whose results are to be evaluated
parser = argparse.ArgumentParser(description="Evaluate the generated designators")
parser.add_argument("-m", "--model", help="LLM to be evaluated", required=True,
                    choices=[model.value for model in ModelType])
args = parser.parse_args()

# get the ModelType enum element whose value corresponds to the model argument
model = get_model_type_from_model_name(args.model)

# output selected model name
if VERBOSE:
    print(f"Evaluating results, LLM: {model.value}")

# base path for the results of this experiment
base_path = "data/pycram_generation"
# path containing the results for the selected model
model_path = os.path.join(base_path, model.value)

# read the results of code metrics for target/ground truth
df_gt = pd.read_csv(os.path.join(model_path, "results_target_ground_truth.csv"),
                    index_col=0)
# read the results of code metrics for target/reference
df_ref = pd.read_csv(os.path.join(model_path, "results_target_reference.csv"),
                     index_col=0)

# 1. Compute correlations between action similarity and code metrics

# get the action similarity results
df_as = pd.read_csv("data/action_similarity.csv", index_col=0)

# construct dataframe with code metric results and action similarity metrics

# copy contains the code metric results using ground truth as the reference
df_gt_as = df_gt.copy()

# list for saving action similarities for each row of the df_gt dataframe
action_similarities = []

# iterate over the rows of the df_gt dataframe, determining the action
# similarities for the current reference/target combination from df_as
for row in range(df_gt.shape[0]):
    # get the row's target action
    target_action = df_gt.loc[row, ResultColumnPycram.TARGET_NAME.value]
    # get the row's reference action
    reference_action = df_gt.loc[row, ResultColumnPycram.REFERENCE_NAME.value]

    # get the row in df_as corresponding to the reference/target combination
    as_row = df_as[(df_as[ActionSimilarityColumns.TARGET_NAME.value] == target_action) &
                   (df_as[ActionSimilarityColumns.REFERENCE_NAME.value] == reference_action)]

    # save the action similarities for this row in the corresponding list
    action_similarities.append([
            as_row[ActionSimilarityColumns.WU_PALMER_SIMILARITY.value].values[0],
            as_row[ActionSimilarityColumns.GLOVE_SIMILARITY.value].values[0],
            as_row[ActionSimilarityColumns.SENSORIMOTOR_DISTANCE.value].values[0],
            as_row[ActionSimilarityColumns.SAME_AUTHOR.value].values[0]
        ])

# for each action similarity metric save the results in a new column in df_gt_as
df_gt_as[ActionSimilarityColumns.WU_PALMER_SIMILARITY.value] = \
    [row[0] for row in action_similarities]
df_gt_as[ActionSimilarityColumns.GLOVE_SIMILARITY.value] = \
    [row[1] for row in action_similarities]
df_gt_as[ActionSimilarityColumns.SENSORIMOTOR_DISTANCE.value] = \
    [row[2] for row in action_similarities]
df_gt_as[ActionSimilarityColumns.SAME_AUTHOR.value] = \
    [row[3] for row in action_similarities]

# names of columns in df_gt_as containing the code metric results
metric_cols = [ResultColumnPycram.CHRF.value, ResultColumnPycram.CODE_BERT_SCORE.value,
               ResultColumnPycram.CODE_BLEU.value, ResultColumnPycram.CRYSTAL_BLEU.value,
               ResultColumnPycram.EDIT_DISTANCE.value, ResultColumnPycram.ROUGE_L.value,
               ResultColumnPycram.LOC.value, ResultColumnPycram.COMPILATION_SUCCESS.value,
               ResultColumnPycram.RUN_SUCCESS.value, ResultColumnPycram.SIMULATION.value]

# names of columns in df_gt_as containg the action similarity results
action_similarity_cols = [ActionSimilarityColumns.WU_PALMER_SIMILARITY.value,
                          ActionSimilarityColumns.GLOVE_SIMILARITY.value,
                          ActionSimilarityColumns.SENSORIMOTOR_DISTANCE.value,
                          ActionSimilarityColumns.SAME_AUTHOR.value]

# compute correlations

# list for saving the correlations for each code/action similarity metric combination
correlations = []

# iterate over the code metrics
for metric_col in metric_cols:
    # list for saving the correlations for this code metric
    correlations_for_metric = []

    # iterate over the action similarity metrics
    for action_similarity_col in action_similarity_cols:

        # when evaluating the simulation and run success metrics the results contain NaN values
        # for designators which haven't been simulated or run; when computing correlations
        # for the simulation column the rows cotaining NaN have to be ignored
        if metric_col in [ResultColumnPycram.SIMULATION.value, ResultColumnPycram.RUN_SUCCESS.value]:
            # determine which rows in df_gt_as do not contain NaN for the simulation or run success
            non_null_rows = ~df_gt_as[metric_col].isnull()
            # get the results for this code metric where the simulation or run success is not NaN
            metric_values = df_gt_as[non_null_rows][metric_col]
            # get the results for this action similarity metric where the simulation or run success is not NaN
            action_similarity_values = df_gt_as[non_null_rows][action_similarity_col]

        # the results of the other code metrics do not contain NaN values
        else:
            # get the results for this code metric
            metric_values = df_gt_as[metric_col]
            # get the results for this action similarity metric
            action_similarity_values = df_gt_as[action_similarity_col]

        # compute spearman rank correlation for this code/action similarity
        # metric combination
        res = spearmanr(action_similarity_values, metric_values)

        # save the rho and p values from the results
        correlations_for_metric.append(res.statistic)
        correlations_for_metric.append(res.pvalue)

    # save the correlation results for the current code metric
    correlations.append(correlations_for_metric)

# result dataframe has code metrics as the rows and action similarity metrics
# as the columns
# the columns alternate between rho and p values
correlation_columns = [ActionSimilarityColumns.WU_PALMER_SIMILARITY.value + " rho",
                       ActionSimilarityColumns.WU_PALMER_SIMILARITY.value + " p",
                       ActionSimilarityColumns.GLOVE_SIMILARITY.value + " rho",
                       ActionSimilarityColumns.GLOVE_SIMILARITY.value + " p",
                       ActionSimilarityColumns.SENSORIMOTOR_DISTANCE.value + " rho",
                       ActionSimilarityColumns.SENSORIMOTOR_DISTANCE.value + " p",
                       ActionSimilarityColumns.SAME_AUTHOR.value + " rho",
                       ActionSimilarityColumns.SAME_AUTHOR.value + " p"]

# construct and save result dataframe
dataframe_correlation = pd.DataFrame(correlations, index=metric_cols,
                                     columns=correlation_columns)
dataframe_correlation.to_csv(os.path.join(model_path, "correlations.csv"),
                             na_rep="NaN")


# 2. Determine which target/reference combinations lead to results being
# closer to reference than ground truth

# for each code metric check which results are closer to reference
closer_chrf = np.array(df_ref[ResultColumnPycram.CHRF.value] >
                       df_gt[ResultColumnPycram.CHRF.value], dtype=int)
closer_cbs = np.array(df_ref[ResultColumnPycram.CODE_BERT_SCORE.value] >
                      df_gt[ResultColumnPycram.CODE_BERT_SCORE.value], dtype=int)
closer_cob = np.array(df_ref[ResultColumnPycram.CODE_BLEU.value] >
                      df_gt[ResultColumnPycram.CODE_BLEU.value], dtype=int)
closer_crb = np.array(df_ref[ResultColumnPycram.CRYSTAL_BLEU.value] >
                      df_gt[ResultColumnPycram.CRYSTAL_BLEU.value], dtype=int)
closer_ed = np.array(df_ref[ResultColumnPycram.EDIT_DISTANCE.value] >
                     df_gt[ResultColumnPycram.EDIT_DISTANCE.value], dtype=int)
closer_rl = np.array(df_ref[ResultColumnPycram.ROUGE_L.value] >
                     df_gt[ResultColumnPycram.ROUGE_L.value], dtype=int)

# calculate sum to determine how many metrics judge a result to be closer to reference
closer_total = closer_chrf + closer_cbs + closer_cob + closer_crb + closer_ed + closer_rl

# result dataframe contains target and reference actions and the run
dataframe_closer = df_gt[[ResultColumnPycram.TARGET_NAME.value,
                          ResultColumnPycram.REFERENCE_NAME.value,
                          ResultColumnPycram.RUN.value]]

# add new column for evaluation results
dataframe_closer[CLOSER_COLUMN_NAME] = closer_total

# save the dataframe to a csv file
dataframe_closer.to_csv(os.path.join(model_path, "results_closer_to_reference.csv"))


# calculate means of number of metrics judging a result closer to reference
# than ground truth, grouped by the run; i.e., for each target/reference action
# combination calculate means for all the runs

# list for saving the means
closer_means = []

# iterate over all target/reference action combinations
for target_action in ACTIONS:
    for reference_action in ACTIONS:

        # if both actions are identical, skip the combination
        if reference_action == target_action:
            continue

        # get the rows in dataframe_closer where the target and reference actions
        # correspond to the current actions
        target_reference_df = dataframe_closer[
                    (dataframe_closer[ResultColumnPycram.TARGET_NAME.value] == target_action) &
                    (dataframe_closer[ResultColumnPycram.REFERENCE_NAME.value] == reference_action)]

        # calculate mean of number of metrics judging results closer to reference
        # for all runs generating this action combination
        mean_value = target_reference_df[CLOSER_COLUMN_NAME].mean()

        # append the values to the respective list
        closer_means.append([target_action, reference_action, mean_value])

# columns of resulting dataframe
closer_means_cloumns = [ResultColumnPycram.TARGET_NAME.value,
                        ResultColumnPycram.REFERENCE_NAME.value,
                        CLOSER_COLUMN_NAME+" mean"]

# create dataframe and save it to a csv file
dataframe_closer_means = pd.DataFrame(closer_means, columns=closer_means_cloumns)
dataframe_closer_means.to_csv(os.path.join(model_path, "results_closer_to_reference_means.csv"),
                              na_rep="NaN")
