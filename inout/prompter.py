import json
import os

import openai

import inout
import model


class OpenAIPrompter:
    def __init__(self):
        json_text = json.load(open(os.path.join("./credentials.json")))
        openai.organization = json_text["organization"]
        openai.api_key = json_text["api_key"]

    def check_models(self):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[
                {"role": "system", "content": "Are you still available?"}
            ],
            temperature=0,
        )
        print(response)

    def generate_designator_gpt3(self,
                                 action: model.Action,
                                 new_action: model.Action) -> model.GeneratedDesignator:
        prompt = f"The following LISP source code describes a CRAM designator for the action of \'{action.get_name()}\', where the executing robot" \
                 f" would {action.get_description()}:\n{action.get_designator()}\nCan you please take this example and create a new designator for" \
                 f" the action \'{new_action.get_name()}\', where the robot should {new_action.get_description()}. Your answer should only include " \
                 f"the designator and no additional text. The designator should begin after a line only containing <desig>"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0,
        )
        designator = response['choices'][0]['text']
        print(designator)
        designator = str(designator).split("<desig>")[1]
        generated = model.GeneratedDesignator(action, new_action, designator)
        inout.write_designator_as_lisp(generated)
        return generated

    def generate_designator_chatgpt(self,
                                    action: model.Action,
                                    new_action: model.Action) -> model.GeneratedDesignator:
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
                                            #" The designator should begin after a "
                                            #"line only containing <desig> in a new line."},
            ],
            temperature=0,
        )
        designator = response['choices'][0]['message']['content']
        after_tag = str(designator).split('```lisp')
        if len(after_tag) >= 2:
            designator = after_tag[1]
        designator = str(designator).split("```")[0]
        generated = model.GeneratedDesignator(action, new_action, designator)
        inout.write_designator_as_lisp(generated)
        return generated


    def generate_designator_gpt4(self,
                                 action: model.Action,
                                 new_action: model.Action) -> str:
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
                                            #" The designator should begin after a "
                                            #"line only containing <desig> in a new line."},
            ],
            temperature=0,
        )
        designator = response['choices'][0]['message']['content']
        after_tag = str(designator).split('```lisp')
        if len(after_tag) >= 2:
            designator = after_tag[1]
        designator = str(designator).split("```")[0]
        generated = model.GeneratedDesignator(action, new_action, designator)
        inout.write_designator_as_lisp(generated)
        return designator
