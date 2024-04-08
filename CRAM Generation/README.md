# Generating CRAM Designators Using Large Language Models

In this part of the repository you can find the Python project used for generating CRAM designators in a one-shot fashion.
The input designators are taken from the official [CRAM repository](https://github.com/cram2/cram) and from the [WebKat-MealRobot repository](https://github.com/Food-Ninja/WebKat-MealRobot).
A complete explanation on how to repeat the experiment and what settings to choose can be seen below.

## Repository Structure
```bash
├── data
│   ├── results                       	# folder containing the results for each run for all 3 LLMs 
│   ├── actions.csv                   	# overview over the 9 actions, their designators and their source location
│   ├── compilation.csv               	# overview over the compilation results
│   └── sensorimotor distance.csv       # overview over the sensorimotor distance calculated between all 72 action combinations
├── eval                              	# folder containing the python scripts necessary for calculating the metrics and the correlation
├── inout                             	# folder containing the python scripts necessary for accessing (data) files
└── model                             	# folder containing the python scripts covering the internal data representation
```

## Repeating the Experiment
To repeat the experiment, you need to follow the following steps:
1) Add the manually created reference designators to the "./data/designators" folder (Naming conventions and where to find them can be found in the actions.csv file)
2) Create an OpenAI account with which you can access the OpenAI API
3) Create a file called "credentials.json" in the this folder in which you save the OpenAI organization and key:
```json
{
    "organization": "organization-id-here",
    "api_key": "api-key-here"
}
```
4) Adjust the settings in the main.py
5) Run the project & Enjoy!

**Remark**: Please note that both ChatGPT models we employed (*gpt-3.5-turbo-0301* and *gpt-3.5-turbo-0613*) are only available until June 13th, 2024[^1]

## Settings

- *generation*: Generate the designators for all model types in the specified number of runs (default = 5)
- *metric_calculation*: Calculate the metrics for all generated designators (1080 for 5 runs and 3 models)
- *output_latex_table*: Format the calculated and saved metrics in a Latex table
- *correlation_calculation*: For all models, calculate the correlation between the code generation and the action similarity metrics
- *average_calculation*: Calculate the mean value for all metrics two times: For each action in a model and for the whole model

[^1]: https://platform.openai.com/docs/models/gpt-3-5
