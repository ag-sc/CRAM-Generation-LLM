# -*- coding: utf-8 -*-
"""
Python script for generating designator in the prompt engineering experiment.
"""

import json
import os

from src.prompter import OpenAIPrompter
from src.exceptions import PrompterException
from src.enums import ModelType
from src.constants import ACTIONS, VERBOSE

# get the action descriptions from the json file
with open("data/action_descriptions.json", "r") as f:
    action_descriptions = json.load(f)

# get the import statemets which are shared by all designators
with open("data/designators/imports.py", "r") as f:
    import_statements = f.read()

# the levels of deatil to be used for the reference and target action descriptions
levels_of_detail = ["1", "2", "3"]

# initialize the prompter and set the model to be used
prompter = OpenAIPrompter()
model = ModelType.GPT_4_OLD

# path to directory for saving generated designators
path = "data/prompt_engineering/raw/"
os.makedirs(path)

# variables for determining the current progress
if VERBOSE:
    current_num = 1
    total_num = len(levels_of_detail)**2 * len(ACTIONS)

# iterate over all the levels of detail for the reference
for reference_detail in levels_of_detail:
    # iterate over all the levels of detail for the target
    for target_detail in levels_of_detail:
        # iterate over all the actions
        for i in range(len(ACTIONS)):
            # for each specific combination of reference detail and target detail
            # use each action once as a reference and once as a target
            reference_action = ACTIONS[i-1]
            target_action = ACTIONS[i]

            # print current progress
            if VERBOSE:
                print(f"({current_num:2d}/{total_num:2d})", end=" ")
                print(f"Reference: {reference_action:9}, detail: {reference_detail}"+
                      f"; Target: {target_action:9}, detail: {target_detail} ...",
                      end = " ", flush=True)
                current_num += 1

            # get the action descriptions for the specific levels of detail
            reference_description = action_descriptions[reference_action][reference_detail]
            target_description = action_descriptions[target_action][target_detail]
            # get the target action's constructor
            target_constructor = action_descriptions[target_action]["constructor"]

            # get the reference designator
            with open("data/designators/"+reference_action+".py", "r") as f:
                reference_designator = f.read()

            # create the full reference, i.e., reference designator with imports
            full_reference = import_statements + "\n" + reference_designator

            # send prompt to LLM
            try:
                target_designator = prompter.generate_designator(model,
                                                                 reference_action,
                                                                 reference_description,
                                                                 full_reference,
                                                                 target_action,
                                                                 target_description,
                                                                 target_constructor)
            # PrompterException raised if the finish reason is not 'stop', in this
            # case generation has ended unexpectedly; Output a warning message
            # if this occurs
            except PrompterException as e:
                details = e.args[0]
                print("Warning:", details["message"], "Reason:", details["reason"])
                target_designator = details["response"]

            # generate name for result file
            fname = (target_action + "_" + target_detail + "_from_" +
                     reference_action + "_" + reference_detail + ".py")

            # save the generated result
            with open(os.path.join(path, fname), "x") as f:
                f.write(target_designator)

            if VERBOSE:
                print("done")
