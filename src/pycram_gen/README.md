# Generating PyCRAM Designators Using Large Language Models

In this part of the repository you can find the Python project used for generating PyCRAM designators in a one-shot fashion.
This covers three experiments:
1. Prompt engineering for determining the optimal levels of detail in the action descriptions (refer to the supplementary material),
2. Generating PyCRAM designators from other PyCRAM designators and
3. Generating PyCRAM designators from CRAM designators

Below is an explanation on how to repeat these experiments.

## Repository Structure
```
├── data/                            # folder containing the results of the three experiments and additional data required for the experiments
│   ├── designators/                 # folder containing the manually created designators
│   ├── prompt_engineering/          # folder containing the results of the prompt engineering experiment
│   ├── pycram_generation/           # folder containing the results of the PyCRAM generation experiment
│   ├── cram_conversion/             # folder containing the results of the CRAM conversion experiment
│   ├── action_descriptions.json     # the action descriptions included in the prompt for the designator generation
│   ├── action_synsets.json          # the selected WordNet synsets for determining the Wu-Palmer similarit between two PyCRAM actions
│   ├── sensorimotor_distance.csv    # results of the Sensorimotor Distance metric for all pairs of PyCRAM actions, retrieved from https://www.lancaster.ac.uk/psychology/smdistance/
│   └── simulation_criteria.csv      # criteria for evaluating the Simulation Quality metric
├── src/                             # folder containing the implementations required for performing the experiments
├── action_similarity_metrics.py     # Python script for computing the action similrity metrics for all pairs of PyCRAM actions
├── cram_conversion_*.py             # Python scripts for performing the CRAM conversion experiment
├── crystal_bleu_init.py             # Python script for determining the most frequent n-grams among the manually created PyCRAM designators
├── prompt_engineering_*.py          # Python scripts for performing the prompt engineering experiment
├── pycram_designator_*.py           # Python script for performing the PyCRAM generation experiment
├── reference_preprocessing.py       # Python script for processing the manually created PyCRAM designators by removing comments and blank lines
└── requirements.txt                 # list of Python packages required for performing the experiments
```

## Repeating the Experiments

### Preparatory Work

1. Clone the repository

2. Install the requirements: `pip3 install -r requirements.txt`

3. Add the manually created PyCRAM designators for the actions *cut*, *grasp*, *mix* and *transport* in the "./data/designators/" folder.
Add the manually created CRAM designators for the actions *cut*, *pour* and *mix* in the "./data/designators/cram/" folder.
The sources of these designators are indicated below:

| Designator Type | Action    | Source Repository |
|:---------------:|:---------:|:-----------------:|
| PyCRAM          | cut       | https://github.com/sunava/pycram/blob/1b96732c833282f2db9f7db8fb5c81ae216aa4cd/src/pycram/designators/action_designator.py |
| PyCRAM          | mix       | https://github.com/sunava/pycram/blob/1b96732c833282f2db9f7db8fb5c81ae216aa4cd/src/pycram/designators/action_designator.py |
| PyCRAM          | grasp     | https://github.com/cram2/pycram/blob/6e495df2c4b86b20c7c18b92b7a542ce663c67dd/src/pycram/designators/action_designator.py |
| PyCRAM          | transport | https://github.com/cram2/pycram/blob/6e495df2c4b86b20c7c18b92b7a542ce663c67dd/src/pycram/designators/action_designator.py |
| CRAM            | cut       | https://github.com/Food-Ninja/FoodCutting/blob/fb72bd3ac19f6763bb7cab479939a6890b47160f/cutting_action_designator.lisp |
| CRAM            | pour      | https://github.com/cram2/cram/blob/48333421167c2564e91d8af7f3608d0858a3450e/cram_common/cram_mobile_cut_pour_plans/src/cut-pour-designators.lisp |
| CRAM            | wipe      | https://github.com/Duxi98/cram/blob/74317c0b4043f778c2d457669e86fc9b3ee215d6/cram_demos/cram_pr2_wipe_demo/src/wipe-designators.lisp |

Use the names "cut.py" etc. for the PyCRAM designators and "cut.lisp" etc. for the CRAM designators.
Note that the CRAM action of *cut* combines the existing designators for *halve* and *slice*.

4. Process the manually created PyCRAM designators using the Python script `python3 reference_preprocessing.py`

5. Determine the most frequent n-grams among the manually created PyCRAM designators for the CrystalBLEU metric: `python3 crystal_bleu_init.py`

6. Compute the action similarity metrics for all pairs of PyCRAM actions: `python3 action_similarity_metrics.py`

7. Add the following files for the CodeBLEU metric in the "./src/metrics/code_bleu" folder: "bleu.py", "utils.py", "weighted_ngram_match.py".
These files can be found in the following repository: https://github.com/microsoft/CodeXGLUE/tree/e252e54a74dd55b1294e2379b213b1541dfefaf5/Code-Code/code-to-code-trans/evaluator/CodeBLEU

8. Add your credentials for accessing the OpenAI API in a file called "credentials.json":
```json
{
    "organization": "organization-id-here",
    "api_key": "api-key-here"
}
```

9. Remove or move the existing results in the "data/prompt_engineering/", "data/pycram_generation/" and "data/cram_conversion/" folders

### Prompt Engineering Experiment

```bash
python3 prompt_engineering_generation.py
python3 prompt_engineering_processing.py
python3 prompt_engineering_metrics.py
python3 prompt_engineering_evaluation.py
```

### PyCRAM Generation Experiment

```bash
for model in gpt-3.5-turbo-0301 gpt-3.5-turbo-1106 gpt-4-0613 gpt-4-1106-preview # Repeat for all four models
do
    for run in {1...5} # Perform five runs using each model
    do
        python3 pycram_designator_generation.py -m $model
    done
    python3 pycram_designator_processing.py -m $model
    python3 pycram_designator_metrics.py -m $model
    python3 pycram_designator_evaluation.py -m $model
done
```

### CRAM Conversion Experiment

```bash
for model in gpt-3.5-turbo-0301 gpt-3.5-turbo-1106 gpt-4-0613 gpt-4-1106-preview # Repeat for all four models
do
    python3 cram_conversion_generation.py -m $model
    python3 cram_conversion_processing.py -m $model
    python3 cram_conversion_metrics.py -m $model
done
```

**Remark**: Please note that the older ChatGPT version we employed (*gpt-3.5-turbo-0301*) is only available until June 13th, 2024[^1]


[^1]: https://platform.openai.com/docs/deprecations
