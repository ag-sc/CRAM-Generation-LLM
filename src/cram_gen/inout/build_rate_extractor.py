import pandas as pd

from src.cram_gen.utils.paths import BUILD_FILE


def get_build_rate(ref: str, gen: str, model: str, run: int) -> int:
    cf = pd.read_csv(BUILD_FILE)
    compile_result = cf[(cf['Target Action'] == gen) & (cf['Reference Action'] == ref) & (cf['Model'] == model) & (cf['Run'] == run)]
    return convert_res_to_int(compile_result['Builds?'].values[0])


def convert_res_to_int(res: str) -> int:
    if res == "Yes":
        return 1
    else:
        return 0
