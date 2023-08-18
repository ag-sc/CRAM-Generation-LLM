import json
import os

import openai

import model


class OpenAIPrompter:
    def __init__(self):
        json_text = json.load(open(os.path.join("./credentials.json")))
        openai.organization = json_text["organization"]
        openai.api_key = json_text["api_key"]
        self.__current_model = model.ModelType.chatgpt_old
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

    def generate_designator(self, action: model.Action, new_action: model.Action) -> model.GeneratedDesignator:
        if self.__current_model == model.ModelType.gpt4:
            return self.generate_designator_gpt4(action, new_action)
        else:
            return self.generate_designator_chatgpt(action, new_action)

    def generate_designator_chatgpt(self, action: model.Action, new_action: model.Action) -> model.GeneratedDesignator:
        from inout import write_designator_as_lisp
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
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
        generated = model.GeneratedDesignator(action, new_action, designator, self.__current_model, self.__current_run)
        write_designator_as_lisp(generated, self.__current_model, self.__current_run)
        return generated

    def generate_designator_gpt4(self, action: model.Action, new_action: model.Action) -> model.GeneratedDesignator:
        from inout import write_designator_as_lisp
        response = openai.ChatCompletion.create(
            model="gpt-4",
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
        generated = model.GeneratedDesignator(action, new_action, designator, self.__current_model, self.__current_run)
        write_designator_as_lisp(generated, self.__current_model, self.__current_run)
        return generated
