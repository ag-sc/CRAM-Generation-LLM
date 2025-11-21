from eval import calculate_correlations
from inout import ResultReader, import_actions, write_metrics_as_csv, calculate_averages
from model import ALL_MODELS, ResultColumnHeaders
from src.cram_gen.inout.prompting import Prompter, OpenAIPrompter
from src.cram_gen.inout.prompting.gemma_prompter import GemmaPrompter
from src.cram_gen.inout.prompting.llama_prompter import LlamaPrompter
from src.cram_gen.model import OpenAIModels, OpenSourceModels

generation = False
metric_calculation = True
output_latex_table = True
correlation_calculation = True
average_calculation = True

MAX_RUNS = 5


def choose_prompter(model_type) -> Prompter:
    if model_type in [model.value for model in OpenAIModels]:
        return OpenAIPrompter(model_type)
    else:
        if model_type == OpenSourceModels.LLAMA:
            return LlamaPrompter()
        else:
            return GemmaPrompter()


def generate_designators():
    actions = import_actions()
    print("Starting the designator generation:")
    for mt in ALL_MODELS:
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
    print("Finished the designator generation")


def calculate_metrics():
    actions = import_actions()
    print("Starting the metrics calculation:")
    for mt in ALL_MODELS:
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
    else:
        for d in designators:
            d.calculate_metrics()
    write_metrics_as_csv(designators)
    print("Finished the metrics calculation")


if __name__ == '__main__':
    reader = ResultReader()
    designators = []

    if generation:
        generate_designators()

    if metric_calculation:
        calculate_metrics()

    if average_calculation:
        calculate_averages(MAX_RUNS)

    if output_latex_table:
        for mt in ALL_MODELS:
            reader.set_model(mt)
            reader.convert_csv_to_latex_table()

    if correlation_calculation:
        metrics = [ResultColumnHeaders.wup, ResultColumnHeaders.glove, ResultColumnHeaders.smd]
        for mt in ALL_MODELS:
            for m in metrics:
                calculate_correlations(mt, m)
