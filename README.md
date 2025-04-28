# Generation of Robot Manipulation Plans Using Generative Large Language Models

This repository contains supplementary material and source code for the paper **Generation of Robot Manipulation Plans Using Generative Large Language Models**, which won the **Best Paper Award** at the *Seventh IEEE International Conference on Robotic Computing (IRC 2023)*. 
You can find the paper on [IEEEXplore](https://ieeexplore.ieee.org/document/10473591) and the conference presentation on [Youtube](https://youtu.be/S4FzqqqdSE4?si=w3Jjj8Hyo3xS-n-v).
An updated version of the paper was published in the *International Journal of Semantic Computing* and can be found on [World Scientific Connect](https://worldscientific.com/doi/10.1142/S1793351X25410041).
If you want to reference this work, please cite one (or both) of the following papers:
```
@article{Toberg2025GenerationRobot,
  title = {Generation of Robot Manipulation Plans Using Generative Large Language Models},
  author = {Töberg, Jan-Philipp and Frese, Philip and Cimiano, Philipp},
  year = {2025},
  journal = {Int. J. Semantic Computing},
  volume = {19},
  number = {01},
  pages = {1--25},
  doi = {10.1142/S1793351X25410041},
}

@inproceedings{Toberg2023GenerationRobot,
  title = {Generation of Robot Manipulation Plans Using Generative Large Language Models},
  booktitle = {2023 Seventh IEEE International Conference on Robotic Computing (IRC)},
  author = {Töberg, Jan-Philipp and Cimiano, Philipp},
  year = {2023},
  pages = {190--197},
  publisher = {IEEE},
  address = {Laguna Hills, CA, USA},
  doi = {10.1109/IRC59093.2023.00039},
}
```

## Abstract

Designing plans that allow robots to carry out actions such as grasping an object or cutting a fruit is a time-consuming activity requiring specific skills and knowledge. 
The recent success of Generative Large Language Models (LLMs) has opened new avenues for code generation.
In order to evaluate the ability of LLMs to generate code representing manipulation plans, we carry out experiments with different LLMs in the CRAM framework and its PyCRAM implementation.

In our experimental framework, we ask an LLM such as ChatGPT or GPT-4 to generate a plan for a specific target action given the plan for a given reference action as an example.
We evaluate the generated designators against a ground truth designator using machine translation and code generation metrics, as well as assessing whether they compile or can be simulated.
We find that GPT-4 slightly outperforms ChatGPT, but both models achieve a solid performance above all evaluated metrics.
However, only 35% of the generated CRAM designators compile successfully and the generated PyCRAM designators fulfil roughly 42\% of the action's simulation success criteria.
In addition, we assess how the chosen reference action influences the code generation quality as well as the compilation success.
Unexpectedly, the action similarity negatively correlates with compilation success.
With respect to the metrics, we obtain either a positive or negative correlation depending on the model and programming language used.

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
Please contact [Jan-Philipp Töberg](https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/arbeitsgruppen/semantic-computing/team/jan-philipp-toeberg) (jtoeberg(at)techfak(dot)uni-bielefeld(dot)de) for further information or potential collaborations.


[^1]: https://platform.openai.com/docs/models/gpt-3-5
