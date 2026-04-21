import torch
import transformers

from .enums import ModelType
from .prompter import Prompter
from .prompts import *


class LlamaPrompter(Prompter):
    def __init__(self, max_new_tokens=2500):
        super().__init__(ModelType.LLAMA.value)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(f'meta-llama/{self._model_name}')
        self.tokenizer.pad_token_id = self.tokenizer.eos_token_id  # for open-ended generation
        self.max_new_tokens = max_new_tokens
        bnb_config = transformers.BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        model_id = transformers.AutoModelForCausalLM.from_pretrained(
            f'meta-llama/{self._model_name}',
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        self.generation_pipe = transformers.pipeline(
            "text-generation",
            model=model_id,
            tokenizer=self.tokenizer,
            trust_remote_code=True,
            device_map="auto",  # finds GPU
        )

    def _prompt(self, messages) -> str:
        prompt = self.generation_pipe.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        terminators = [
            self.generation_pipe.tokenizer.eos_token_id,
            self.generation_pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        outputs = self.generation_pipe(
            prompt,
            max_new_tokens=self.max_new_tokens,
            eos_token_id=terminators,
            do_sample=False,  # No randomness
            temperature=None,
            top_p=None
        )
        result = outputs[0]["generated_text"][len(prompt):]
        return self.extract_designator(result)

    def extract_designator(self, model_answer: str) -> str:
        designator = model_answer.split("```")[0]
        return designator

    def generate_designator(self, reference_name: str, reference_description: str, reference_designator: str,
                            target_name: str, target_description: str, target_constructor: str) -> str:
        messages = [
            {"role": "system", "content": sys_prompt_pycram.format(reference_name=reference_name,
                                                                   reference_description=reference_description,
                                                                   reference_designator=reference_designator)},
            {"role": "user",
             "content": usr_prompt_pycram.format(target_name=target_name, target_description=target_description,
                                                 target_constructor=target_constructor)}
        ]
        return self._prompt(messages)

    def translate_cram_designator(self, action_name: str, cram_description: str, cram_designator: str,
                                  pycram_basic_structure: str, pycram_description: str, pycram_constructor: str) -> str:
        messages = [
            {"role": "system",
             "content": sys_prompt_translate.format(action_name=action_name, cram_description=cram_description,
                                                    cram_designator=cram_designator,
                                                    pycram_basic_structure=pycram_basic_structure)},
            {"role": "user",
             "content": usr_prompt_translate.format(action_name=action_name, pycram_description=pycram_description,
                                                    pycram_constructor=pycram_constructor)}
        ]
        return self._prompt(messages)
