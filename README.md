# Generation of Robot Manipulation Plans within the CRAM Framework Using Generative Large Language Models - Supplementary Material

This repository contains supplementary material to the paper "Generation of Robot Manipulation Plans within the CRAM Framework Using Generative Large Language Models" submitted to the *IEEE Robotic Computing* conference.

## Abstract

To evaluate the suitability of Generative Large Language Models (LLMs) for the robotics domain, we report an experiment where we generate robot manipulation plans in the CRAM framework using generative LLMs like ChatGPT and GPT-4.
In our experiment, we generate a plan for a single action by providing another action and its CRAM designator as an example.
We analyse the generated designators using machine translation and code generation metrics, as well as assessing whether they compile.
We found that GPT-4 slightly outperforms ChatGPT but both models achieve above average results for all metrics. However, only ~35% of the generated designators successfully compile.
In addition, we assess how the chosen reference action influences the code generation quality as well as the compilation success.
Surprisingly, the action similarity negatively correlates with compilation success and either negatively or positively correlates with the code generation metrics, depending on the model version used. 
Lastly, we describe our attempt to use ChatGPT for co-constructing a specific designator.
Due to hallucinations and ignoring parts of the prompt, the co-construction cannot be recommended for creating novel CRAM designators.

## Repository Structure
```bash
├── co-construction                   # results of the co-construction attempt where each file represents a single exchange with ChatGPT
├── data
│   ├── results                       # folder containing the results for each run for all 3 LLMs 
│   ├── actions.csv                   # overview over the 9 actions, their designators and their source location
│   ├── compilation.csv               # overview over the compilation results
│   └── sensorimotor distance.csv     # overview over the sensorimotor distance calculated between all 72 action combinations
├── eval                              # folder containing the python scripts necessary for calculating the metrics and the correlation
├── inout                             # folder containing the python scripts necessary for accessing (data) files
├── model                             # folder containing the python scripts covering the internal data representation
├── Comparison Overview.pdf           # manual qualitative comparison of generated designators to their manually created gold standard
└── Metrics Overview.pdf              # overview over all metrics calculated for all 72 action combinations for all 3 models
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
