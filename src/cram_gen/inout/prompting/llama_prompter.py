import torch
import transformers

from .prompter import Prompter
from src.cram_gen.inout.prompting.prompts import system_prompt, user_prompt
from src.cram_gen.model import Action, GeneratedDesignator
from src.cram_gen.model import OpenSourceModels


class LlamaPrompter(Prompter):
    def __init__(self, max_new_tokens=2500):
        super().__init__(OpenSourceModels.LLAMA)
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

    def generate_designator(self, ref_action: Action, target_action: Action) -> GeneratedDesignator:
        # Instruct version needs specific conversation structure
        messages = [
            {"role": "system", "content": system_prompt.format(action_name=ref_action.get_name(),
                                                               action_description=ref_action.get_description(),
                                                               designator=ref_action.get_designator())},
            {"role": "user", "content": user_prompt.format(action_name=target_action.get_name(),
                                                           action_description=target_action.get_description())}
        ]
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
        return self.extract_designator(ref_action, target_action, result)
