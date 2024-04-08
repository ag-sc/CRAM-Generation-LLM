import pandas as pd


def get_compilation_results(ref: str, gen: str, model: str, run: int) -> int:
    file = './data/compilation.csv'
    cf = pd.read_csv(file)
    compile_result = cf[(cf['Target Action'] == gen) & (cf['Reference Action'] == ref) & (cf['Model'] == model) & (cf['Run'] == run)]
    return convert_comp_res_to_int(compile_result['Compiles?'].values[0])


def convert_comp_res_to_int(res: str) -> int:
    if res == "Yes":
        return 1
    else:
        return 0
