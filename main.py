import eval
import inout

generation = False
metric_calculation = False
output_latex_table = True
correlation_calculation = False
average_calculation = False
count_and_average_lines = True
test = False


def generate_designators():
    actions = inout.import_actions()
    for ref_a in actions:
        for gen_a in actions:
            if ref_a is gen_a:
                continue
            if inout.check_if_already_generated(ref_a.get_name(), gen_a.get_name()):
                print(f'Already generated: {gen_a.get_name()} based on {ref_a.get_name()}')
                continue
            prompter.generate_designator_chatgpt(ref_a, gen_a)


def calculate_metrics():
    actions = inout.import_actions()
    designators = []
    c = 1
    for ref_a in actions:
        for gen_a in actions:
            if ref_a is gen_a:
                continue
            designator = inout.read_designator(gen_a, ref_a)
            designator.calculate_metrics()
            designators.append(designator)
            print(f'{c}/72 - {"%2.1f" % ((c / 72.0) * 100)}%')
            c += 1
    inout.write_metrics_as_csv(designators)


if __name__ == '__main__':
    prompter = inout.OpenAIPrompter()
    if generation:
        generate_designators()

    if metric_calculation:
        calculate_metrics()

    if output_latex_table:
        inout.convert_csv_to_latex_table()

    if correlation_calculation:
        eval.calculate_correlations(inout.read_results(), 'WuP')
        eval.calculate_correlations(inout.read_results(), 'GloVe-Similarity')

    if average_calculation:
        inout.calculate_average()

    if count_and_average_lines:
        inout.count_lines_gen()

    if test:
        pass
