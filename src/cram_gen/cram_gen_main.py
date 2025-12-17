import argparse
from typing import List

from tqdm import tqdm

from src.cram_gen.eval import calculate_correlations
from src.cram_gen.inout import ResultReader, import_actions, write_metrics_as_csv, calculate_averages
from src.cram_gen.inout.prompting import Prompter, OpenAIPrompter, GemmaPrompter, LlamaPrompter
from src.cram_gen.model import ALL_MODELS, ResultColumnHeaders, OpenAIModels, OpenSourceModels

MAX_RUNS = 5

def choose_prompter(model_type) -> Prompter:
    if model_type in [model.value for model in OpenAIModels]:
        return OpenAIPrompter(model_type)
    else:
        if model_type == OpenSourceModels.LLAMA:
            return LlamaPrompter()
        else:
            return GemmaPrompter()


def generate_designators(models: List[str]):
    print("\n-----\nSTART STEP 1: GENERATION\n")
    actions = import_actions()
    for mt in tqdm(models, 'Generating designators for each model'):
        reader.set_model(mt)
        prompter = choose_prompter(mt)
        for r in range(1, MAX_RUNS + 1):
            reader.set_run(r)
            prompter.set_run_number(r)
            for ref_a in actions:
                for gen_a in actions:
                    if ref_a is gen_a:
                        continue
                    if reader.check_if_already_generated(ref_a.get_name(), gen_a.get_name()):
                        print(f'Already generated: {gen_a.get_name()} based on {ref_a.get_name()} for model {mt} - run {r}')
                        continue
                    des = prompter.generate_designator(ref_a, gen_a)
                    designators.append(des)
                    print(f'Successfully generated: {gen_a.get_name()} based on {ref_a.get_name()} for model {mt} - run {r}')
    print("\n-----\nEND STEP 1: GENERATION\n")


def calculate_metrics(models: List[str]):
    print("\n-----\nSTART STEP 2: METRIC CALCULATION\n")
    actions = import_actions()
    for mt in tqdm(models, 'Calculating the metrics for each model'):
        reader.set_model(mt)
        for r in range(1, MAX_RUNS + 1):
            reader.set_run(r)
            for ref_a in actions:
                for gen_a in actions:
                    if ref_a is gen_a:
                        continue
                    designator = reader.read_designator(gen_a, ref_a)
                    designator.calculate_metrics()
                    designators.append(designator)
    write_metrics_as_csv(designators)
    print("\n-----\nEND STEP 2: METRIC CALCULATION\n")

if __name__ == '__main__':
    reader = ResultReader()
    designators = []

    parser = argparse.ArgumentParser(description='One-Shot Prompting experiment for generating CRAM manipulation plans')
    parser.add_argument("--models", type=str, choices=["all", "openai", "open_source", "llama", "gemma"], nargs=1,
                        help="Choose for which group of models plans should be generated")
    parser.add_argument("--steps", type=str, choices=["all", "gen", "metrics", "avg", "corr", "ltx_tab"], nargs="+",
                        help="Choose one or more steps to perform")
    args = parser.parse_args()

    if "openai" in args.models:
        models = [m.value for m in OpenAIModels]
    elif "open_source" in args.models:
        models = [m.value for m in OpenSourceModels]
    elif "llama" in args.models:
        models = [OpenSourceModels.LLAMA.value]
    elif "gemma" in args.models:
        models = [OpenSourceModels.GEMMA.value]
    else:
        models = ALL_MODELS

    if "all" in args.steps or "gen" in args.steps:
        generate_designators(models)
    if "all" in args.steps or "metrics" in args.steps:
        calculate_metrics(models)
    if "all" in args.steps or "avg" in args.steps:
        print("\n-----\nSTART STEP 3: AVERAGE CALCULATION\n")
        calculate_averages(MAX_RUNS, models)
        print("\n-----\nEND STEP 3: AVERAGE CALCULATION\n")
    if "all" in args.steps or "corr" in args.steps:
        print("\n-----\nSTART STEP 4: CORRELATIONS\n")
        metrics = [ResultColumnHeaders.wup, ResultColumnHeaders.glove, ResultColumnHeaders.smd]
        for mt in models:
            for m in metrics:
                calculate_correlations(mt, m)
        print("\n-----\nEND STEP 4: CORRELATIONS\n")
    if "ltx_tab" in args.steps:
        for mt in models:
            reader.set_model(mt)
            reader.convert_csv_to_latex_table()
