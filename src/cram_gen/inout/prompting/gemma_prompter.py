import re

import torch
import transformers

from .prompter import Prompter
from src.cram_gen.inout.prompting.prompts import system_prompt, user_prompt
from src.cram_gen.model import Action, GeneratedDesignator
from src.cram_gen.model import OpenSourceModels


class GemmaPrompter(Prompter):
    def __init__(self, max_new_tokens=2500):
        super().__init__(OpenSourceModels.GEMMA)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(f'google/{self._model_name}')
        self.model = transformers.AutoModelForCausalLM.from_pretrained(
            f'google/{self._model_name}',
            device_map="auto",
            torch_dtype=torch.bfloat16
        )
        self.max_new_tokens = max_new_tokens

    def generate_designator(self, ref_action: Action, target_action: Action) -> GeneratedDesignator:
        messages = [{"role": "user",
                     "content": f"{system_prompt.format(action_name=ref_action.get_name(), action_description=ref_action.get_description(), designator=ref_action.get_designator())}\n{user_prompt.format(action_name=target_action.get_name(), action_description=target_action.get_description())}"}]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
        outputs = self.model.generate(input_ids=inputs.to(self.model.device),
                                      max_new_tokens=self.max_new_tokens,
                                      do_sample=False,  # No randomness if False
                                      temperature=None,
                                      top_p=None)
        outputs = self.tokenizer.decode(outputs[0, len(inputs):])
        match = re.search(r"<start_of_turn>model(.*?)<end_of_turn>", outputs, re.DOTALL)
        result = match.group(1).strip() if match else None
        return self.extract_designator(ref_action, target_action, result)
