#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Python script for generating designators in the experiment "Converting CRAM
Designators into PyCRAM Designators".
Performs 5 independent runs using the selected LLM.
Usage:
    $ python3 cram_conversion_generation.py -m [model]
"""

import json
import os
import argparse

from src.prompter import OpenAIPrompter, PrompterException
from src.utils import get_model_type_from_model_name
from src.enums import ModelType
from src.constants import VERBOSE, CRAM_ACTIONS, TARGET_DETAIL

# argument parser for parsing command line argument which sets the LLM to be used
parser = argparse.ArgumentParser(description="Convert CRAM designators into PyCRAM " +
                                 "desingators using OpenAI's LLMs ChatGPT and GPT-4")
parser.add_argument("-m", "--model", help="LLM to be used", required=True,
                    choices=[model.value for model in ModelType])
args = parser.parse_args()

# set to True if generation of a designator ends unexpecteldy
# if this occurs, a warning is printed in the end
generation_interrupted = False

# get the ModelType enum element whose value corresponds to the model argument
model = get_model_type_from_model_name(args.model)

# base path for saving the generated designators for this experiment
base_path = "data/cram_conversion/"
# path for saving generated designators for this model
model_path = os.path.join(base_path, model.value)

# create directory for saving results for this model
path = os.path.join(model_path, "raw")
os.makedirs(path)

# get the action descriptions from the json file
with open("data/action_descriptions.json", "r") as f:
    action_descriptions = json.load(f)

# get the basic structure of a PyCRAM designator
with open("data/designators/basic_structure.py", "r") as f:
    pycram_structure = f.read()

# get the import statements for the PyCRAM designators
with open("data/designators/imports.py", "r") as f:
    import_statements = f.read()

# the full basic structure of a PyCRAM designator consists of the import
# statements and the basic structure
pycram_structure_full = import_statements + "\n" + pycram_structure

# initialize the prompter
prompter = OpenAIPrompter()

# the number of runs to be performed using this model
NUMBER_OF_RUNS = 5

# variables for determining the current progress
if VERBOSE:
    print(f"Converting CRAM Designators into PyCRAM Designators, LLM: {model.value}")
    current_num = 1
    total_num = len(CRAM_ACTIONS) * NUMBER_OF_RUNS

# iterate over the actions to be used
for action in CRAM_ACTIONS:

    # get the action description for the CRAM reference designator
    cram_description = action_descriptions[action]["cram"]

    # get the action description and constructor for the PyCRAM target designator
    pycram_description = action_descriptions[action][TARGET_DETAIL]
    pycram_constructor = action_descriptions[action]["constructor"]

    # get the CRAM reference designator
    with open(os.path.join("data/designators/cram", action+".lisp"), "r") as f:
        cram_designator = f.read()

    # iterate over the runs to be performed
    for run in range(1, NUMBER_OF_RUNS+1):

        # print the current progress
        if VERBOSE:
            print(f"({current_num:2d}/{total_num:2d})", end=" ")
            print(f"Action: {action:4}, Run: {run} ...", end=" ", flush=True)
            current_num += 1

        # send prompt to LLM to convert designator
        try:
            pycram_designator = prompter.convert_cram_designator(model,
                                                                 action,
                                                                 cram_description,
                                                                 cram_designator,
                                                                 pycram_structure_full,
                                                                 pycram_description,
                                                                 pycram_constructor)
        # PrompterException raised if the finish reason is not 'stop', in this
        # case generation has ended unexpectedly; Output a warning message
        # if this occurs and save the reponse to a log file
        except PrompterException as e:
            details = e.args[0]
            print("Warning:", details["message"], "Reason:", details["reason"])
            generation_interrupted = True
            with open(os.path.join(model_path, "generation_log.txt"), "a") as f:
                f.write(f"Warning: {details['message']}, Reason: {details['reason']}\n")
                f.write(f"Action: {action}, Run: {run}\n")
                f.write("Response:\n")
                f.write(str(details["full_response"]))
                f.write("\n\n")
            continue

        # generate name for result file
        fname = action + "_run_" + str(run) + ".py"

        # save the generated result
        with open(os.path.join(path, fname), "x") as f:
            f.write(pycram_designator)

        if VERBOSE:
            print("done")


# output a warning message if the generation of a designator has ended unexpectedly
if generation_interrupted:
    print("Warning: Generation of a designator has ended unexpectedly")
    print(f"See {os.path.join(model_path, 'generation_log.txt')} for details")
