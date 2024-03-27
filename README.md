# Generation of Robot Manipulation Plans Using Generative Large Language Models - Supplementary Material

This repository contains supplementary material to the paper **Generation of Robot Manipulation Plans Using Generative Large Language Models**, which won the **Best Paper Award** at the *Seventh IEEE International Conference on Robotic Computing (IRC 2023)*. 
You can find the conference presentation on [Youtube](https://youtu.be/S4FzqqqdSE4?si=w3Jjj8Hyo3xS-n-v). If you want to reference this work, please cite the following paper:
```
@inproceedings{Toberg2023GenerationRobot,
  title = {Generation of {{Robot Manipulation Plans Using Generative Large Language Models}}},
  booktitle = {2023 {{Seventh IEEE International Conference}} on {{Robotic Computing}} ({{IRC}})},
  author = {T{\"o}berg, Jan-Philipp and Cimiano, Philipp},
  year = {2023},
  month = dec,
  pages = {190--197},
  publisher = {IEEE},
  address = {Laguna Hills, CA, USA},
  doi = {10.1109/IRC59093.2023.00039},
  isbn = {9798350395747},
}
```

## Abstract

Designing plans that allow robots to carry out actions such as grasping an object or cutting a fruit is a time-consuming activity requiring specific skills and knowledge. 
The recent success of Generative Large Language Models (LLMs) has opened new avenues for code generation.
In order to evaluate the ability of LLMs to generate code representing manipulation plans, we carry out experiments with different LLMs in the CRAM framework.
In our experimental framework, we ask an LLM such as ChatGPT or GPT-4 to generate a plan for a specific target action given the plan (called designator within CRAM) for a given reference action as an example.
We evaluate the generated designators against a ground truth designator using machine translation and code generation metrics, as well as assessing whether they compile.
We find that GPT-4 slightly outperforms ChatGPT, but  both models achieve a solid performance above all evaluated metrics.
However, only 35% of the generated designators compile successfully.
In addition, we assess how the chosen reference action influences the code generation quality as well as the compilation success. 
Unexpectedly, the action similarity negatively correlates with compilation success.
With respect to the metrics, we obtain either a positive or negative correlation depending on the used model. 
Finally, we describe our attempt to use ChatGPT in an interactive fashion to incrementally refine the initially generated designator.
On the basis of our observations we conclude that the behaviour of ChatGPT is not reliable and robust enough to support the incremental refinement of a designator.

## Repository Structure
```bash
├── data
│   ├── results                       		# folder containing the results for each run for all 3 LLMs 
│   ├── actions.csv                   	# overview over the 9 actions, their designators and their source location
│   ├── compilation.csv               	# overview over the compilation results
│   └── sensorimotor distance.csv # overview over the sensorimotor distance calculated between all 72 action combinations
├── designator refinement             # results of the incremental refinement attempt where each file represents a single exchange with ChatGPT
├── eval                              		# folder containing the python scripts necessary for calculating the metrics and the correlation
├── inout                             		# folder containing the python scripts necessary for accessing (data) files
├── model                             		# folder containing the python scripts covering the internal data representation
├── Comparison Overview.pdf       # manual qualitative comparison of generated designators to their manually created gold standard
└── Metrics Overview.pdf				# overview over all metrics calculated for all 72 action combinations for all 3 models
```

## Repeating the Experiment
To repeat the experiment reported in the paper, you need to follow the following steps:
1) Add the manually created reference designators to the "./data/designators" folder (Naming conventions and where to find them can be found in the actions.csv file)
2) Create an OpenAI account with which you can access the OpenAI API
3) Create a file called "credentials.json" in the root folder in which you save the OpenAI organization and key:
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

## Disclaimer

This work was done by the [Semantic Computing Group](https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/arbeitsgruppen/semantic-computing/) at the Center for Cognitive Interaction Technology @ Bielefeld University.
Please contact [Jan-Philipp Töberg](https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/arbeitsgruppen/semantic-computing/team/jan-philipp-toeberg) (jtoeberg(at)techfak(dot)uni-bielefeld(dot)de) for further information or collaboration.


[^1]: https://platform.openai.com/docs/models/gpt-3-5
