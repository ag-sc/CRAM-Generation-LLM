from enum import Enum


class ModelType(str, Enum):
    chatgpt_old = 'gpt-3.5-turbo-0301'
    chatgpt_new = 'gpt-3.5-turbo-0613'
    gpt4 = "gpt-4-0613"
