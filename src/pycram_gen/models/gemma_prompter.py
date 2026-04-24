import re

import torch
import transformers

from .enums import ModelType
from .prompter import Prompter
from .prompts import *


class GemmaPrompter(Prompter):
    def __init__(self, max_new_tokens=2500):
        super().__init__(ModelType.GEMMA.value)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(f'google/{self._model_name}')
        self.model = transformers.AutoModelForCausalLM.from_pretrained(
            f'google/{self._model_name}',
            device_map="auto",
            torch_dtype=torch.bfloat16
        )
        self.max_new_tokens = max_new_tokens

    def _prompt(self, messages) -> str:
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer.encode(
            prompt,
            add_special_tokens=False,
            return_tensors="pt",
            truncation=True,
            max_length=4096
        ).to(self.model.device)
        outputs = self.model.generate(
            input_ids=inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=False
        )
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        match = re.search(r"<start_of_turn>model(.*?)<end_of_turn>", generated, re.DOTALL)
        result = match.group(1).strip() if match else None
        return self.extract_designator(str(result))

    def extract_designator(self, model_answer: str) -> str:
        designator = model_answer.split("```")[0]
        return designator

    def generate_designator(self, reference_name: str, reference_description: str, reference_designator: str,
                            target_name: str, target_description: str, target_constructor: str) -> str:
        messages = [{"role": "user",
                     "content": f"{sys_prompt_pycram.format(reference_name=reference_name, reference_description=reference_description, reference_designator=reference_designator)}\n{usr_prompt_pycram.format(target_name=target_name, target_description=target_description, target_constructor=target_constructor)}"}]
        return self._prompt(messages)

    def translate_cram_designatoraction_name(self, action_name: str, cram_description: str, cram_designator: str,
                                             pycram_basic_structure: str, pycram_description: str,
                                             pycram_constructor: str) -> str:
        messages = [{"role": "user",
                     "content": f"{sys_prompt_translate.format(action_name=action_name, cram_description=cram_description, cram_designator=cram_designator, pycram_basic_structure=pycram_basic_structure)}\n{usr_prompt_translate.format(action_name=action_name, pycram_description=pycram_description, pycram_constructor=pycram_constructor)}"}]
        return self._prompt(messages)
