import pandas as pd
from typing import List
from model import GeneratedDesignator


def write_metrics_as_csv(designators: List[GeneratedDesignator]):
    file = './data/results.csv'
    df = pd.DataFrame.from_records([des.convert_to_dict() for des in designators])
    df.to_csv(file)


def write_designator_as_lisp(designator: GeneratedDesignator):
    folder = './data/gen/'
    file = f'{folder}/{designator.get_generated_action_name().lower()}_based_on_{designator.get_reference_action_name().lower()}.lisp'
    with open(file, "w") as text_file:
        text_file.write(designator.get_generated_designator().strip())
        print(f'Successfully generated: {designator.get_generated_action_name()} based on {designator.get_reference_action_name()}')
