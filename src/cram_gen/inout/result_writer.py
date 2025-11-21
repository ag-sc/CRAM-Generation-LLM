from typing import List

import pandas as pd

from src.cram_gen.model import GeneratedDesignator
from src.cram_gen.utils.paths import ALL_RESULTS_FILE, CRAM_GEN_FOLDER


def write_metrics_as_csv(designators: List[GeneratedDesignator]):
    df = pd.DataFrame.from_records([des.convert_to_dict() for des in designators])
    df.to_csv(ALL_RESULTS_FILE, index=False)


def write_designator_as_lisp(designator: GeneratedDesignator, model_name: str, run: int):
    folder = CRAM_GEN_FOLDER / f"gen {model_name} run0{run}"
    file = folder / f'{designator.get_generated_action_name().lower()}_based_on_{designator.get_reference_action_name().lower()}.lisp'
    with open(file, "w") as text_file:
        text_file.write(designator.get_generated_designator().strip())
