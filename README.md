# Generation of Robot Manipulation Plans Using Generative Large Language Models - Supplementary Material

This repository contains supplementary material to the paper "Generation of Robot Manipulation Plans Using Generative Large Language Models" accepted at the *Seventh IEEE International Conference on Robotic Computing (IRC)*. 
If you want to reference this work, please cite the following paper: *tba*

## Abstract

Designing plans that allow robots to carry out actions such as grasping an object or cutting a fruit is a time-consuming activity requiring specific skills and knowledge. 
The recent success of Generative Large Language Models (LLMs) has opened new avenues for code generation.
In order to evaluate the ability of LLMs to generate code representing manipulation plans, we carry out experiments with different LLMs in the CRAM framework.
In our experimental framework, we ask an LLM such as ChatGPT or GPT-4 to generate a plan for a specific target action given the plan (called designator within CRAM) for a given reference action as an example.
We evaluate the generated designators against a ground truth designator using machine translation and code generation metrics, as well as assessing whether they compile.
We find that GPT-4 slightly outperforms ChatGPT, but  both models achieve a solid performance above all evaluated metrics.
However, only ~35% of the generated designators compile successfully.
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
4) Remove/Move the generation results in "./data/results" since new designators are only generated when no existing ones are found
5) Adjust the settings in the main.py
6) Run the project & Enjoy!

**Remark**: Please note that the *gpt-3.5-turbo-0301* model we employed is only available until June 13th, 2024[^1]

## Disclaimer

This work was done by the [Semantic Computing Group](https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/arbeitsgruppen/semantic-computing/) at the Center for Cognitive Interaction Technology @ Bielefeld University.
Please contact <a href="https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/arbeitsgruppen/semantic-computing/team/jan-philipp-toeberg/">Jan-Philipp Töberg</a> (jtoeberg(at)techfak(dot)uni-bielefeld(dot)de) for further information or collaboration.


[^1]: https://platform.openai.com/docs/models/gpt-3-5
