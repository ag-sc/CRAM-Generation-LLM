# -*- coding: utf-8 -*-

import json
from typing import List, Dict

from openai import OpenAI, ChatCompletion

from .constants import VERBOSE
from .enums import ModelType
from .exceptions import PrompterException
from .prompter import Prompter
from .prompts import *


class OpenAIPrompter(Prompter):
    """
    Class for prompting OpenaAI's LLMs ChatGPT and GPT-4
    """

    def __init__(self, model: str):
        super().__init__(model)
        with open("./credentials.json", "r") as f:
            credentials = json.load(f)
        self._client = OpenAI(organization=credentials["organization"], api_key=credentials["api_key"])

    def _prompt(self, messages: List[Dict]) -> ChatCompletion:
        """
        Send a prompt to an LLM and return the response

        :param messages: The messages to be sent in the prompt,
            refer to OpenAI's documentation
        :returns: The model's response
        """

        response = self._client.chat.completions.create(
            model=self.get_model_name(),
            messages=messages,
            temperature=0
        )
        return response

    def test(self, model: ModelType) -> ChatCompletion:
        """
        Send a simple test prompt for test purposes

        :param model: The model to be used
        :returns: Model's response
        """

        if VERBOSE:
            print(model.value)
        response = self._prompt(model, messages=[
            {
                "role": "user",
                "content": "Say hello world"
            }
        ]
                                )
        if VERBOSE:
            print(response)
            print(response.choices[0].finish_reason)
        print(response.choices[0].message.content)
        return response

    def extract_designator(self, model_answer: ChatCompletion) -> str:
        response_message = model_answer.choices[0].message.content
        finish_reason = model_answer.choices[0].finish_reason
        # if VERBOSE:
        #     print(finish_reason)
        if finish_reason != "stop":
            raise PrompterException({
                "message": "Generation ended unexpectedly",
                "reason": finish_reason,
                "response": response_message,
                "full_response": model_answer
            })
        after_tag = response_message.split("```python")[1]
        designator = after_tag.split("```")[0]
        # if VERBOSE:
        #     print(designator)
        return designator

    def generate_designator(self, reference_name: str, reference_description: str, reference_designator: str,
                            target_name: str, target_description: str, target_constructor: str) -> str:
        messages = [
            {
                "role": "system",
                "content": sys_prompt_pycram.format(reference_name=reference_name,
                                                    reference_description=reference_description,
                                                    reference_designator=reference_designator)
            },
            {
                "role": "user",
                "content": usr_prompt_pycram.format(target_name=target_name, target_description=target_description,
                                                    target_constructor=target_constructor)
            }
        ]
        # if VERBOSE:
        #     print(messages)
        response = self._prompt(messages)
        # if VERBOSE:
        #     print(response)
        designator = self.extract_designator(response)
        return designator

    def translate_cram_designator(self, action_name: str, cram_description: str, cram_designator: str,
                                  pycram_basic_structure: str, pycram_description: str, pycram_constructor: str) -> str:
        messages = [
            {
                "role": "system",
                "content": sys_prompt_translate.format(action_name=action_name, cram_description=cram_description,
                                                       cram_designator=cram_designator,
                                                       pycram_basic_structure=pycram_basic_structure)
            },
            {
                "role": "user",
                "content": usr_prompt_translate.format(action_name=action_name, pycram_description=pycram_description,
                                                       pycram_constructor=pycram_constructor)
            }
        ]
        response = self._prompt(messages)
        designator = self.extract_designator(response)
        return designator
