# -*- coding: utf-8 -*-
"""
Python script for evaluating the results of the code metric computation for
the designators generated during the prompt engineering experiment.
This consists of the following three parts:
    1. For determining the optimal level of detail for the target action descriptions:
        Calculate means of code metrics for target/ground truth, grouped by
        the target detail.
    2. For determining the optimal level of detail for the reference action descriptions:
        Calculate means of code metrics for target/ground truth, grouped by
        the reference detail.
    3. Determine which combination of target/reference action and target/reference
        detail leads to generated designators being closer to reference than
        ground truth.
"""

import os
import pandas as pd
import numpy as np

from src.enums import ResultColumnPromptEngineering
from src.constants import ACTIONS, CLOSER_COLUMN_NAME

# path to directory containing results
path = "data/prompt_engineering"

# read the results of code metrics for target/ground truth
df_gt = pd.read_csv(os.path.join(path, "results_target_ground_truth.csv"),
                    index_col=0)

# read the results of code metrics for target/reference
df_ref = pd.read_csv(os.path.join(path, "results_target_reference.csv"),
                     index_col=0)

# lists for storing the means for 1. and 2.
means_target_detail = []
means_reference_detail = []

# compute means for 1.
# iterate over all actions
for action in ACTIONS:
    # get the dataframe based on df_gt containing only the rows
    # that have the current action as their target action
    action_df = df_gt[df_gt[ResultColumnPromptEngineering.TARGET_NAME.value] == action]

    # iterate over the levels of detail
    for detail in range(1, 3+1):

        # get dataframe based on action_df containing only the rows that have
        # the current detail as their target detail
        detail_df = action_df[action_df[ResultColumnPromptEngineering.TARGET_DETAIL.value] == detail]
        # compute the means of the numeric columns
        means = detail_df.mean(numeric_only=True)
        # save the means of the code metrics for the current target action and detail
        means_target_detail.append([
                                    action,
                                    detail,
                                    means[ResultColumnPromptEngineering.CHRF.value],
                                    means[ResultColumnPromptEngineering.CODE_BERT_SCORE.value],
                                    means[ResultColumnPromptEngineering.CODE_BLEU.value],
                                    means[ResultColumnPromptEngineering.CRYSTAL_BLEU.value],
                                    means[ResultColumnPromptEngineering.EDIT_DISTANCE.value],
                                    means[ResultColumnPromptEngineering.ROUGE_L.value]
        ])

# columns of the dataframes for saving the results for 1.
dataframe_columns = [ResultColumnPromptEngineering.TARGET_NAME.value,
                     ResultColumnPromptEngineering.TARGET_DETAIL.value,
                     ResultColumnPromptEngineering.CHRF.value,
                     ResultColumnPromptEngineering.CODE_BERT_SCORE.value,
                     ResultColumnPromptEngineering.CODE_BLEU.value,
                     ResultColumnPromptEngineering.CRYSTAL_BLEU.value,
                     ResultColumnPromptEngineering.EDIT_DISTANCE.value,
                     ResultColumnPromptEngineering.ROUGE_L.value]

# create dataframe for 1. and save it to a csv file
dataframe_target = pd.DataFrame(means_target_detail, columns=dataframe_columns)
dataframe_target.to_csv("data/prompt_engineering/results_means_target_detail.csv")


# compute means for 2.
# iterate over all actions
for action in ACTIONS:
    # get the dataframe based on df_gt containing only rows
    # that have the current action as their reference action
    action_df = df_gt[df_gt[ResultColumnPromptEngineering.REFERENCE_NAME.value] == action]
    
    # iterate over the levels of detail
    for detail in range(1, 3+1):

        # get dataframe based on action_df containing only rows that have
        # the current detail as their reference detail
        detail_df = action_df[action_df[ResultColumnPromptEngineering.REFERENCE_DETAIL.value] == detail]
        # compute the means of the numeric columns
        means = detail_df.mean(numeric_only=True)
        # save the means of the code metrics for the current target action
        # and the current reference detail
        means_reference_detail.append([
                            action,
                            detail,
                            means[ResultColumnPromptEngineering.CHRF.value],
                            means[ResultColumnPromptEngineering.CODE_BERT_SCORE.value],
                            means[ResultColumnPromptEngineering.CODE_BLEU.value],
                            means[ResultColumnPromptEngineering.CRYSTAL_BLEU.value],
                            means[ResultColumnPromptEngineering.EDIT_DISTANCE.value],
                            means[ResultColumnPromptEngineering.ROUGE_L.value]
        ])

# exchange target name column name for reference name
dataframe_columns[0] = ResultColumnPromptEngineering.REFERENCE_NAME.value
# exchange the target detail column name for reference detail
dataframe_columns[1] = ResultColumnPromptEngineering.REFERENCE_DETAIL.value
# create dataframe for 2. and save it to a csv file
dataframe_reference = pd.DataFrame(means_reference_detail, columns=dataframe_columns)
dataframe_reference.to_csv("data/prompt_engineering/results_means_reference_detail.csv")


# 3. for each metric determine which of the generated designators are closer
# to the reference than the ground truth
closer_chrf = np.array(df_ref[ResultColumnPromptEngineering.CHRF.value] >
                       df_gt[ResultColumnPromptEngineering.CHRF.value], dtype=int)
closer_cbs = np.array(df_ref[ResultColumnPromptEngineering.CODE_BERT_SCORE.value] >
                      df_gt[ResultColumnPromptEngineering.CODE_BERT_SCORE.value], dtype=int)
closer_cob = np.array(df_ref[ResultColumnPromptEngineering.CODE_BLEU.value] >
                      df_gt[ResultColumnPromptEngineering.CODE_BLEU.value], dtype=int)
closer_crb = np.array(df_ref[ResultColumnPromptEngineering.CRYSTAL_BLEU.value] >
                      df_gt[ResultColumnPromptEngineering.CRYSTAL_BLEU.value], dtype=int)
closer_ed = np.array(df_ref[ResultColumnPromptEngineering.EDIT_DISTANCE.value] >
                     df_gt[ResultColumnPromptEngineering.EDIT_DISTANCE.value], dtype=int)
closer_rl = np.array(df_ref[ResultColumnPromptEngineering.ROUGE_L.value] >
                     df_gt[ResultColumnPromptEngineering.ROUGE_L.value], dtype=int)

# calculate sum to determine how many metrics judge a result to be closer to reference
closer_total = closer_chrf + closer_cbs + closer_cob + closer_crb + closer_ed + closer_rl

# result dataframe saves reference/target names and details
dataframe_closer = df_gt[[ResultColumnPromptEngineering.TARGET_NAME.value,
                          ResultColumnPromptEngineering.TARGET_DETAIL.value,
                          ResultColumnPromptEngineering.REFERENCE_NAME.value,
                          ResultColumnPromptEngineering.REFERENCE_DETAIL.value]]
# add new column for evaluation results
dataframe_closer[CLOSER_COLUMN_NAME] = closer_total
# save the results to a csv file
dataframe_closer.to_csv("data/prompt_engineering/results_closer_to_reference.csv")
