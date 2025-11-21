import json
import os

import openai

from src.cram_gen.model import ModelType, Action, GeneratedDesignator


class OpenAIPrompter:
    def __init__(self):
        json_text = json.load(open(os.path.join("./credentials.json")))
        openai.organization = json_text["organization"]
        openai.api_key = json_text["api_key"]
        self.__current_model = ModelType.chatgpt_old
        self.__current_run = 1

    def set_model(self, new_model: str):
        self.__current_model = new_model

    def set_run(self, run: int):
        self.__current_run = run

    def check_models(self):
        response = openai.ChatCompletion.create(
            model=self.__current_model,
            messages=[
                {"role": "system", "content": "Are you still available?"}
            ],
            temperature=0,
        )
        print(response)

    def generate_designator(self, action: Action, new_action: Action) -> GeneratedDesignator:
        from src.cram_gen.inout import write_designator_as_lisp
        response = openai.ChatCompletion.create(
            model=self.__current_model,
            messages=[
                {"role": "system", "content": "The following LISP source code describes a CRAM designator for the "
                                              f"action of \'{action.get_name()}\', where the executing robot would be "
                                              f"{action.get_description()}:"},
                {"role": "system", "content": f"{action.get_designator()}"},
                {"role": "user", "content": "Can you please take this example and create a new designator for the "
                                            f"action \'{new_action.get_name()}\', where the robot should be "
                                            f"{new_action.get_description()}. Your answer should only include the"
                                            " designator and no additional text."},
                # " The designator should begin after a "
                # "line only containing <desig> in a new line."},
            ],
            temperature=0,
        )
        designator = response['choices'][0]['message']['content']
        after_tag = str(designator).split('```lisp')
        if len(after_tag) >= 2:
            designator = after_tag[1]
        designator = str(designator).split("```")[0]
        generated = GeneratedDesignator(action, new_action, designator, self.__current_model, self.__current_run)
        write_designator_as_lisp(generated, self.__current_model, self.__current_run)
        return generated
