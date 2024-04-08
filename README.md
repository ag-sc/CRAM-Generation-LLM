# Generation of Robot Manipulation Plans Using Generative Large Language Models

This repository contains supplementary material and source code for the paper **Generation of Robot Manipulation Plans Using Generative Large Language Models**, which won the **Best Paper Award** at the *Seventh IEEE International Conference on Robotic Computing (IRC 2023)*. 
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
├── CRAM Generation         # folder for the first experiment where CRAM designators are generated (based on CRAM designators)
│   └── ...                             
├── Designator Refinement   # results of the incremental refinement attempt where each file represents a single exchange with ChatGPT
├── PyCRAM Generation       # folder for the second & third experiment where PyCRAM designators are generated
│   └── ...  
└── Supplementary Material  # folder containing additional material (presentations, explanations, etc.) as pdfs
```

## Disclaimer

This work was done by the [Semantic Computing Group](https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/arbeitsgruppen/semantic-computing/) at the Center for Cognitive Interaction Technology @ Bielefeld University.
Please contact [Jan-Philipp Töberg](https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/arbeitsgruppen/semantic-computing/team/jan-philipp-toeberg) (jtoeberg(at)techfak(dot)uni-bielefeld(dot)de) for further information or collaboration.


[^1]: https://platform.openai.com/docs/models/gpt-3-5
