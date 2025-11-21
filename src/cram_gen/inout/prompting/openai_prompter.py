import json

from openai import OpenAI

from .prompter import Prompter
from src.cram_gen.inout.prompting.prompts import system_prompt, user_prompt
from src.cram_gen.model import Action, GeneratedDesignator, OpenAIModels
from src.cram_gen.utils.paths import OPENAI_CREDENTIALS


class OpenAIPrompter(Prompter):
    def __init__(self, model: OpenAIModels):
        super().__init__(model)
        with OPENAI_CREDENTIALS.open() as f:
            json_text = json.load(f)
        self.client = OpenAI(
            api_key=json_text["api_key"],
        )

    def generate_designator(self, ref_action: Action, target_action: Action) -> GeneratedDesignator:
        response = self.client.chat.completions.create(
            model=self._model_name,
            messages=[
                {"role": "system", "content": system_prompt.format(action_name=ref_action.get_name(),
                                                                   action_description=ref_action.get_description(),
                                                                   designator=ref_action.get_designator())},
                {"role": "user", "content": user_prompt.format(action_name=target_action.get_name(),
                                                               action_description=target_action.get_description())}
            ],
            temperature=self._temperature,
        )
        designator = response['choices'][0]['message']['content']
        return self.extract_designator(ref_action, target_action, designator)
