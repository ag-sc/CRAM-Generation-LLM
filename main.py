from eval import calculate_correlations
from inout import ResultReader, OpenAIPrompter, import_actions, write_metrics_as_csv, calculate_averages
from model import ModelType, ResultColumnHeaders

generation = False
metric_calculation = False
output_latex_table = False
correlation_calculation = True
average_calculation = False


def generate_designators():
    actions = import_actions()
    max_runs = 5
    print("Starting the designator generation:")
    for mt in ModelType:
        reader.set_model(mt)
        prompter.set_model(mt)
        for r in range(1, max_runs+1):
            reader.set_run(r)
            prompter.set_run(r)
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
    max_runs = 5
    print("Starting the metrics calculation:")
    if not designators:
        c = 1
        for mt in ModelType:
            reader.set_model(mt)
            for r in range(1, max_runs + 1):
                reader.set_run(r)
                for ref_a in actions:
                    for gen_a in actions:
                        if ref_a is gen_a:
                            continue
                        designator = reader.read_designator(gen_a, ref_a)
                        designator.calculate_metrics()
                        designators.append(designator)
                        print(f'{c}/1080 - {"%2.1f" % ((c / 1080.0) * 100)}%')
                        c += 1
    else:
        c = 1
        for d in designators:
            d.calculate_metrics()
            print(f'{c}/1080 - {"%2.1f" % ((c / 1080.0) * 100)}%')
            c += 1
    write_metrics_as_csv(designators)
    print("Finished the metrics calculation")


if __name__ == '__main__':
    prompter = OpenAIPrompter()
    reader = ResultReader()
    designators = []

    if generation:
        generate_designators()

    if metric_calculation:
        calculate_metrics()

    if average_calculation:
        calculate_averages()

    if output_latex_table:
        for mt in ModelType:
            reader.set_model(mt)
            reader.convert_csv_to_latex_table()

    if correlation_calculation:
        metrics = [ResultColumnHeaders.wup, ResultColumnHeaders.glove, ResultColumnHeaders.smd]
        for mt in ModelType:
            for m in metrics:
                calculate_correlations(mt, m)
