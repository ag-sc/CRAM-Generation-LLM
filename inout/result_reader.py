import os
import statistics
from os.path import exists

import pandas as pd

from model import Action, GeneratedDesignator


def check_if_already_generated(action: str, new_act: str) -> bool:
    folder = './data/gen/'
    file = f'{folder}/{new_act.lower()}_based_on_{action.lower()}.lisp'
    return exists(file)


def read_designator(gen_act: Action, ref_act: Action) -> GeneratedDesignator:
    folder = './data/gen/'
    file = f'{folder}/{gen_act.get_name().lower()}_based_on_{ref_act.get_name().lower()}.lisp'
    with open(file, 'r') as txt_file:
        gen_des = txt_file.read()
    return GeneratedDesignator(ref_act, gen_act, gen_des)


def read_results() -> pd.DataFrame:
    # file = './data/results.csv'
    file = './data/average results gpt-3.5-turbo-0613.csv'
    return pd.read_csv(file)


def convert_csv_to_latex_table():
    df = read_results().sort_values(['Generated', 'Reference'])
    for idx, row in df.iterrows():
        print(f'{row["Generated"]} & {row["Reference"]} & & {format_float(row["WuP"])} & {format_float(row["GloVe-Similarity"])} & '
              f'{format_float(row["BLEU"])} & {format_float(row["ROUGE-1"])} & {format_float(row["ROUGE-2"])} & '
              f'{format_float(row["ROUGE-L"])} & {format_float(row["CodeBERTScore"])} & {format_float(row["chrF"])}\\\\')


def format_float(val: float) -> str:
    return "%2.2f" % (val * 100)


def count_lines_gen():
    no_runs = 5
    folder = './data/results'
    lines = {}
    for x in range(no_runs):
        directory = os.fsencode(f'{folder}/gen gpt-3.5-turbo-0613 run0{x + 1}/')
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    line_count = sum(1 for line in f)
                    if file not in lines:
                        lines[file] = []
                    lines[file].append(line_count)

    for file, count in lines.items():
        avg = statistics.mean(count)
        print(f"File {file} has {count} lines. Average={avg}")
