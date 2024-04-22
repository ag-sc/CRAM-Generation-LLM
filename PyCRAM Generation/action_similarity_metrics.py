# -*- coding: utf-8 -*-
"""
Python script for computing the action similarity between all combinations
of reference and target actions using the following metrics:
    Wu-Palmer Similarity between WordNet Synsets
    Cosine Similarity using GloVe Embeddings
    Sensorimotor Distance (using https://embodiedcognitionlab2.shinyapps.io/sensorimotordistance/)
"""

import json
import pandas as pd

from src.action_similarity import cosine_similarity_glove, wu_palmer_similarity
from src.enums import ActionSimilarityColumns
from src.constants import ACTIONS, SAME_AUTHOR_ACTIONS

# get the WordNet synsets for the actions
with open("data/action_synsets.json", "r") as f:
    action_synsets = json.load(f)

# get the Sensorimotor Distance results
sensorimotor_distance = pd.read_csv("data/sensorimotor_distance.csv")

# list for saving the computed action similarities
action_similarities = []

# iterate over all target actions
for target_action in ACTIONS:
    # iterate over all reference actions
    for reference_action in ACTIONS:
        # if the reference and target actions are identical skip the combination
        if reference_action == target_action:
            continue

        # get the WordNet synsets for the reference and target actions
        reference_synset = action_synsets[reference_action]
        target_synset = action_synsets[target_action]

        # compute the Wu-Palmer Similarity between the reference and target synsets
        wup = wu_palmer_similarity(reference_synset, target_synset)

        # compute the cosine similarity using GloVe Embeddings
        glove = cosine_similarity_glove(reference_action, target_action)

        # get the Sensorimotor Distance for the reference and target actions
        sd = sensorimotor_distance[
                (sensorimotor_distance['Reference Action'] == reference_action) &
                (sensorimotor_distance['Target Action'] == target_action)
            ]['Cosine distance'].values[0]

        # determine whether the reference and target actions were created
        # by the same author
        sa = 1 if set([target_action, reference_action]) in SAME_AUTHOR_ACTIONS else 0

        # save the results in the list
        action_similarities.append([target_action, reference_action, wup, glove, sd, sa])

# the dataframe columns are defined by the ActionSimilarityColumns enum
dataframe_columns = [column.value for column in ActionSimilarityColumns]

# create and save the result dataframe
dataframe_action_similarity = pd.DataFrame(action_similarities,
                                           columns=dataframe_columns)
dataframe_action_similarity.to_csv("data/action_similarity.csv")
