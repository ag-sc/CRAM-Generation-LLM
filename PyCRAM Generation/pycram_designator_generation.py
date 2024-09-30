#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Python script for generating designators in the experiment "Generating PyCRAM
Designators".
Performs a single run using the selected LLM.
Usage:
    $ python3 pycram_designator_generation.py -m [model]
"""

import json
import os
import argparse

from src.prompter import OpenAIPrompter, PrompterException
from src.utils import get_model_type_from_model_name
from src.enums import ModelType
from src.constants import ACTIONS, VERBOSE, REFERENCE_DETAIL, TARGET_DETAIL

# argument parser for parsing command line argument which sets the LLM to be used
parser = argparse.ArgumentParser(description="Generate PyCRAM designators using " +
                                 "OpenAI's LLMs ChatGPT and GPT-4")
parser.add_argument("-m", "--model", help="LLM to be used", required=True,
                    choices=[model.value for model in ModelType])
args = parser.parse_args()

# set to True if generation of a designator ends unexpecteldy
# if this occurs, a warning is printed in the end
generation_interrupted = False

# get the ModelType enum element whose value corresponds to the model argument
model = get_model_type_from_model_name(args.model)

# base path for saving the generated designators for this experiment
base_path = "data/pycram_generation/"
# path for saving generated designators for this model
model_path = os.path.join(base_path, model.value)

# check whether the model path exists
if os.path.exists(model_path):
    # list the contents of the model path, i.e., the names of any previously
    # performed runs
    previous_runs = sorted(next(os.walk(model_path))[1])
    # if a run has been performed
    if previous_runs:
        # get the name of the last run
        last_run = previous_runs[-1]
        # get the number of the current run, i.e., the number of the
        # last run incremented by 1
        run = int(last_run.split("_")[-1]) + 1
    # if no run has been performed this is the first run
    else:
        run = 1
# if the model path does not exist no runs have been performed;
# this is the first run
else:
    run = 1

# create directory for saving results of current run
run_path = os.path.join(model_path, "run_"+str(run))
path = os.path.join(run_path, "raw")
os.makedirs(path)

# get the action descriptions from the json file
with open("data/action_descriptions.json", "r") as f:
    action_descriptions = json.load(f)

# get the import statements which are shared by all designators
with open("data/designators/imports.py", "r") as f:
    import_statements = f.read()

# initialize the prompter
prompter = OpenAIPrompter()

# variables for determining the current progress
if VERBOSE:
    print(f"Generating PyCRAM Designators, LLM: {model.value}, run: {run}")
    current_num = 1
    total_num = len(ACTIONS) * (len(ACTIONS) - 1)

# iterate over the reference actions
for reference_action in ACTIONS:

    # get the level of detail for the reference action description
    reference_detail = REFERENCE_DETAIL[reference_action]

    # get the reference action description
    reference_description = action_descriptions[reference_action][reference_detail]

    # get the reference designator
    with open(os.path.join("data/designators/", reference_action+".py"), "r") as f:
        reference_designator = f.read()

    # full reference consists of the common import statements and the reference
    # designator
    full_reference = import_statements + "\n" + reference_designator

    # iterate over the target actions
    for target_action in ACTIONS:

        # if the reference and target actions are identical, skip the combination
        if reference_action == target_action:
            continue

        # print the current progress
        if VERBOSE:
            print(f"({current_num:2d}/{total_num:2d})", end=" ")
            print(f"Reference: {reference_action:9}, Target: {target_action:9} ...",
                  end = " ", flush=True)
            current_num += 1

        # get the target action description and target constructor
        target_description = action_descriptions[target_action][TARGET_DETAIL]
        target_constructor = action_descriptions[target_action]["constructor"]

        # send prompt to LLM to generate the designator
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
        # if this occurs and save the reponse to a log file
        except PrompterException as e:
            details = e.args[0]
            print("Warning:", details["message"], "Reason:", details["reason"])
            generation_interrupted = True
            with open(os.path.join(run_path, "generation_log.txt"), "a") as f:
                f.write(f"Warning: {details['message']}, Reason: {details['reason']}\n")
                f.write(f"Reference Action: {reference_action}, Target Action: {target_action}\n")
                f.write("Response:\n")
                f.write(str(details["full_response"]))
                f.write("\n\n")
            continue


        # generate name for result file
        fname = target_action + "_from_" + reference_action + ".py"

        # save the generated result
        with open(os.path.join(path, fname), "x") as f:
            f.write(target_designator)

        if VERBOSE:
            print("done")


# output a warning message if the generation of a designator has ended unexpectedly
if generation_interrupted:
    print("Warning: Generation of a designator has ended unexpectedly")
    print(f"See {os.path.join(run_path, 'generation_log.txt')} for details")
