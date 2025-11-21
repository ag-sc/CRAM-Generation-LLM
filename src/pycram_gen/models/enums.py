# -*- coding: utf-8 -*-

from enum import Enum, auto

class ModelType(Enum):
    """
    Enum class for the LLMs to be used
    """

    CHAT_GPT_OLD = "gpt-3.5-turbo-0301"
    CHAT_GPT_NEW = "gpt-3.5-turbo-1106"
    GPT_4_OLD = "gpt-4-0613"
    GPT_4_NEW = "gpt-4-1106-preview"

class ActionSynset(Enum):
    """
    Enum class for the action synsets
    """

    POUR = "decant.v.01"
    WIPE = "wipe.v.01"
    TRANSPORT = "transport.v.01"
    GRASP = "grasp.v.01"
    CUT = "cut.v.01"
    MIX = "blend.v.03"

class Metrics(Enum):
    """
    Enum class for the metric types
    """

    CHRF = auto()
    CODE_BERT_SCORE = auto()
    CODE_BLEU = auto()
    CRYSTAL_BLEU = auto()
    EDIT_DISTANCE = auto()
    ROUGE_L = auto()

class ResultColumnPromptEngineering(Enum):
    """
    Enum class for the columns in the metric computation results for the
    prompt enginering experiment
    """

    TARGET_NAME = "Target Name"
    TARGET_DETAIL = "Target Detail"
    REFERENCE_NAME = "Reference Name"
    REFERENCE_DETAIL = "Reference Detail"
    CHRF = "chrF"
    CODE_BERT_SCORE = "CodeBERTScore"
    CODE_BLEU = "CodeBLEU"
    CRYSTAL_BLEU = "CrystalBLEU"
    EDIT_DISTANCE = "Edit Distance"
    ROUGE_L = "ROUGE-L"
    LOC = "LoC"
    COMPILATION_SUCCESS = "Compilation Success"

class ResultColumnPycram(Enum):
    """
    Enum class for the columns in the metric computation results for the
    experiment "Generating PyCRAM Designators"
    """

    TARGET_NAME = "Target Name"
    REFERENCE_NAME = "Reference Name"
    RUN = "run"
    CHRF = "chrF"
    CODE_BERT_SCORE = "CodeBERTScore"
    CODE_BLEU = "CodeBLEU"
    CRYSTAL_BLEU = "CrystalBLEU"
    EDIT_DISTANCE = "Edit Distance"
    ROUGE_L = "ROUGE-L"
    LOC = "LoC"
    COMPILATION_SUCCESS = "Compilation Success"
    RUN_SUCCESS = "Run Success"
    SIMULATION = "Simulation"

class ResultColumnCram(Enum):
    """
    Enum class for the columns in the metric computation results for the
    experiment "Converting CRAM Designators into PyCRAM Designators"
    """

    ACTION_NAME = "Action Name"
    RUN = "run"
    CHRF = "chrF"
    CODE_BERT_SCORE = "CodeBERTScore"
    CODE_BLEU = "CodeBLEU"
    CRYSTAL_BLEU = "CrystalBLEU"
    EDIT_DISTANCE = "Edit Distance"
    ROUGE_L = "ROUGE-L"
    LOC = "LoC"
    COMPILATION_SUCCESS = "Compilation Success"
    RUN_SUCCESS = "Run Success"
    SIMULATION = "Simulation"

class ActionSimilarityColumns(Enum):
    """
    Enum class for the columns in the action similarity dataset
    """

    TARGET_NAME = "Target Name"
    REFERENCE_NAME = "Reference Name"
    WU_PALMER_SIMILARITY = "Wu-Palmer Similarity"
    GLOVE_SIMILARITY = "Cosine Similarity GloVe"
    SENSORIMOTOR_DISTANCE = "Sensorimotor Distance"
    SAME_AUTHOR = "Same Author"
