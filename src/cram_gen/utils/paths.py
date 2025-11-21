from pathlib import Path

# Folders
DATA_FOLDER = Path(__file__).resolve().parent.parent.parent.parent / "data"
CRAM_GEN_FOLDER = DATA_FOLDER / "cram_generation"
DESIGNATOR_FOLDER = DATA_FOLDER / "cram_designators"

# Files
ACTIONS_FILE =  DATA_FOLDER / "cram_actions.csv"
COMP_FILE = CRAM_GEN_FOLDER / "compilation.csv"
ALL_RESULTS_FILE = CRAM_GEN_FOLDER / "all_results.csv"
SMD_FILE = DATA_FOLDER / "sensorimotor_distance.csv"