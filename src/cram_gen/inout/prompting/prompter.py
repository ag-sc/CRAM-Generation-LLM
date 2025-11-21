from src.cram_gen.inout import write_designator_as_lisp
from src.cram_gen.model import Action, GeneratedDesignator


class Prompter:
    def __init__(self, model: str, temp=0.0):
        self._model_name = model
        self._temperature = temp
        self._run = 1

    def generate_designator(self, ref_action: Action, target_action: Action) -> GeneratedDesignator:
        pass

    def extract_designator(self, ref_action: Action, target_action: Action, answer: str) -> GeneratedDesignator:
        after_tag = str(answer).split('```lisp')
        if len(after_tag) >= 2:
            designator = after_tag[1]
        designator = str(answer).split("```")[0]
        generated = GeneratedDesignator(ref_action, target_action, designator, self.get_model_name(), self.get_run())
        write_designator_as_lisp(generated, self.get_model_name(), self.get_run())
        return generated

    def get_model_name(self) -> str:
        return self._model_name

    def get_run(self) -> int:
        return self._run

    def set_run_number(self, run: int):
        self._run = run
