# -*- coding: utf-8 -*-

import json
from typing import List, Dict
from openai import OpenAI, ChatCompletion

from .enums import ModelType
from .exceptions import PrompterException
from .constants import VERBOSE

class OpenAIPrompter:
    """
    Class for prompting OpenaAI's LLMs ChatGPT and GPT-4
    """

    def __init__(self):
        with open("./credentials.json", "r") as f:
            credentials = json.load(f)
        self._client = OpenAI(organization=credentials["organization"],
                                 api_key=credentials["api_key"])

    def _prompt(self, model: ModelType, messages: List[Dict]) -> ChatCompletion:
        """
        Send a prompt to an LLM and return the response

        :param model: The model to be used
        :param messages: The messages to be sent in the prompt,
            refer to OpenAI's documentation
        :returns: The model's response
        """

        response = self._client.chat.completions.create(
            model=model.value,
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

    def _extract_designator(self, response: ChatCompletion) -> str:
        """
        Extracts the generated PyCRAM designator from the model's response

        :param response: The model's full response (ChatCompletion object)
        :returns: The designator contained in the response, any additional
            output is removed
        :raises PrompterException: If the finish reason is not 'stop'
            (i.e., any reason apart from the default). Exception argument
            is dictionary containing exception message, finish reason,
            and generated response.
        """

        response_message = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        # if VERBOSE:
        #     print(finish_reason)
        if finish_reason != "stop":
            raise PrompterException({
                "message": "Generation ended unexpectedly",
                "reason": finish_reason,
                "response": response_message,
                "full_response": response
            })
        after_tag = response_message.split("```python")[1]
        designator = after_tag.split("```")[0]
        # if VERBOSE:
        #     print(designator)
        return designator

    def generate_designator(self, model: ModelType,
                                reference_name: str,
                                reference_description: str,
                                reference_designator: str,
                                target_name: str,
                                target_description: str,
                                target_constructor: str) -> str:
        """
        Generate a designator using an LLM by providing
        a reference designator

        :param model: The model to be used
        :param reference_name: The reference action's name
        :param reference_description: The reference action's description
        :param reference_designator: The full reference designator
        :param target_name: The target action's name
        :param target_description: The target action's description
        :param target_constructor: The target action's constructor
        :returns: The generated designator
        """

        messages=[
            {
                "role": "system",
                "content": f'''The following Python source code describes a \
PyCRAM designator for the action of "{reference_name}", where the robot would \
{reference_description}
```python
{reference_designator}
```'''
            },
            {
                "role": "user",
                "content": f'Take the example and create a new designator \
for the action "{target_name}", where the robot should {target_description}. \
Output only the designator with no additional text. Do not include comments \
in the code. Use only the imported libraries and designators. Use the \
following constructor: {target_constructor}'
            }
        ]
        # if VERBOSE:
        #     print(messages)
        response = self._prompt(model, messages)
        # if VERBOSE:
        #     print(response)
        designator = self._extract_designator(response)
        return designator

    def convert_cram_designator(self, model: ModelType,
                                    action_name: str,
                                    cram_description: str,
                                    cram_designator: str,
                                    pycram_basic_structure: str,
                                    pycram_description: str,
                                    pycram_constructor: str) -> str:
        """
        Convert a CRAM designator into a PyCRAM designator using an LLM

        :param model: The model to be used
        :param action_name: The name of the action
        :param cram_description: The action description of the CRAM designator
        :param cram_designator: The CRAM designator
        :param pycram_basic_structure: The basic structure of a PyCRAM designator
            with import statements
        :param pycram_description: The action description of the PyCRAM designator
        :param pycram_constructor: The constructor of the PyCRAM designator
        :returns: The generated PyCRAM designator
        """

        messages = [
            {
                "role": "system",
                "content": f'''The following Lisp source code describes a \
CRAM designator for the action of "{action_name}", where the robot would \
{cram_description}
```lisp
{cram_designator}
```

PyCRAM designators are written in Python and have the following basic structure:
```python
{pycram_basic_structure}
```'''
            },
            {
                "role": "user",
                "content": f'Take the CRAM designator and convert it into a \
PyCRAM designator (include an implementation of the perform method) for the \
same action of "{action_name}", where the robot should {pycram_description}. \
Output only the designator with no additional text. \
Do not include comments in the code. Follow the provided basic structure and \
use only the imported libraries and designators. Use the following \
constructor: {pycram_constructor}'
            }
        ]
        response = self._prompt(model, messages)
        designator = self._extract_designator(response)
        return designator
