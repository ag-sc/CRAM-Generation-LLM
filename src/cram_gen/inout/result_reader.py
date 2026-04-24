from os.path import exists

import pandas as pd

from src.cram_gen.model import OpenAIModels, GeneratedDesignator, Action
from src.cram_gen.utils.paths import ALL_RESULTS_FILE, CRAM_GEN_FOLDER


class ResultReader:
    def __init__(self):
        self.__model = OpenAIModels.CHATGPT_OLD
        self.__run = 1
        self.__folder = None
        self.set_folder()

    def set_folder(self):
        self.__folder = CRAM_GEN_FOLDER / f'gen {self.__model} run0{self.__run}'

    def set_model(self, new_model: str):
        self.__model = new_model.lower()
        self.set_folder()

    def set_run(self, run: int):
        self.__run = run
        self.set_folder()

    def check_if_already_generated(self, action: str, new_act: str) -> bool:
        file = self.__folder / f'{new_act.lower()}_based_on_{action.lower()}.lisp'
        return exists(file)

    def read_designator(self, gen_act: Action, ref_act: Action) -> GeneratedDesignator:
        file = self.__folder / f'{gen_act.get_name().lower()}_based_on_{ref_act.get_name().lower()}.lisp'
        with open(file, 'r') as txt_file:
            gen_des = txt_file.read()
        return GeneratedDesignator(ref_act, gen_act, gen_des, self.__model, self.__run, file)

    def read_average_results(self) -> pd.DataFrame:
        file = CRAM_GEN_FOLDER / f"average results {self.__model}.csv"
        return pd.read_csv(file)

    @staticmethod
    def read_all_results() -> pd.DataFrame:
        return pd.read_csv(ALL_RESULTS_FILE)

    def convert_csv_to_latex_table(self):
        from src.cram_gen.model import ResultColumnHeaders
        df = self.read_average_results().sort_values([ResultColumnHeaders.gen, ResultColumnHeaders.ref])
        print(f"Latex Table for average results of the {self.__model} model:")
        for idx, row in df.iterrows():
            print(f'{row[ResultColumnHeaders.gen]} & {row[ResultColumnHeaders.gen]} & {row[ResultColumnHeaders.loc]} & & '
                  f'{ResultReader.format_float(row[ResultColumnHeaders.wup])} & {ResultReader.format_float(row[ResultColumnHeaders.glove])} & '
                  f'{ResultReader.format_float(row[ResultColumnHeaders.smd])} & {ResultReader.format_float(row[ResultColumnHeaders.bleu])} & '
                  f'{ResultReader.format_float(row[ResultColumnHeaders.r1])} & {ResultReader.format_float(row[ResultColumnHeaders.r2])} & '
                  f'{ResultReader.format_float(row[ResultColumnHeaders.rl])} & {ResultReader.format_float(row[ResultColumnHeaders.cbs])} & '
                  f'{ResultReader.format_float(row[ResultColumnHeaders.chrf])}\\\\')

    @staticmethod
    def format_float(val: float) -> str:
        return "%2.2f" % (val * 100)
