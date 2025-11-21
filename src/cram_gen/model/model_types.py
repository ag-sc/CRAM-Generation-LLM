from enum import Enum

class OpenAIModels(str, Enum):
    # Model types from original experiments
    CHATGPT_OLD = 'gpt-3.5-turbo-0301'
    CHATGPT_NEW = 'gpt-3.5-turbo-0613'
    GPT4_OLD = "gpt-4-0613"

class OpenSourceModels(str, Enum):
    # Model types for open source experiments
    LLAMA = "Llama-3.3-70B-Instruct"
    GEMMA = "gemma-2-27b-it"

ALL_MODELS = [model.value for model in OpenAIModels] + [model.value for model in OpenSourceModels]
