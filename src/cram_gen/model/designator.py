import torch

from src.cram_gen.eval import WordNetHandler, GloveHandler, calculate_bleu, calculate_rouge, calculate_code_bert_score, \
    calculate_chrf
from .action import Action


class GeneratedDesignator:
    wn_handler = WordNetHandler()
    glove_handler = GloveHandler()

    def __init__(self, ref_act: Action, gen_act: Action, designator: str, model_name: str, run: int):
        self.__reference_action = ref_act
        self.__generated_action = gen_act
        self.__designator = designator
        self.__bleu_score = 0.0
        self.__rouge_1 = 0.0
        self.__rouge_2 = 0.0
        self.__rouge_l = 0.0
        self.__code_bert_score = 0.0
        self.__chrf_score = 0.0
        self.__wup = 0.0
        self.__glove_cosine_sim = 0.0
        self.__sensorimotor = 0.0
        self.__compiles = 0
        self.__lines = 0
        self.__model = model_name
        self.__run = run

    def get_generated_designator(self) -> str:
        return self.__designator

    def get_reference_designator(self) -> str:
        return self.__reference_action.get_designator()

    def get_reference_action_name(self) -> str:
        return self.__reference_action.get_name()

    def get_generated_action_name(self) -> str:
        return self.__generated_action.get_name()

    def calculate_metrics(self):
        from src.cram_gen.inout import get_dist_for_action_combination, get_compilation_results

        ref_designator = self.get_reference_designator()
        gen_designator = self.get_generated_designator()

        if not ref_designator or not gen_designator:
            self.__bleu_score = 0
            self.__rouge_1 = {"p": 0.0, "r": 0.0, "f": 0.0}
            self.__rouge_2 = {"p": 0.0, "r": 0.0, "f": 0.0}
            self.__rouge_l = {"p": 0.0, "r": 0.0, "f": 0.0}
            self.__code_bert_score = [torch.tensor(0.0), torch.tensor(0.0), torch.tensor(0.0)]
            self.__chrf_score = 0
        else:
            ref = [ref_designator]
            gen = [gen_designator] * len(ref)

            self.__bleu_score = calculate_bleu(gen_designator, ref_designator)
            self.__rouge_1 = calculate_rouge(gen_designator, ref_designator, '1')
            self.__rouge_2 = calculate_rouge(gen_designator, ref_designator, '2')
            self.__rouge_l = calculate_rouge(gen_designator, ref_designator, 'lcs')
            self.__code_bert_score = calculate_code_bert_score(gen, ref)
            self.__chrf_score = calculate_chrf(gen[0], ref[0])

        self.__wup = GeneratedDesignator.wn_handler.get_wup_sim(self.__reference_action.get_name(), self.__generated_action.get_name())
        self.__glove_cosine_sim = GeneratedDesignator.glove_handler.calculate_cosine(self.get_generated_action_name(), self.get_reference_action_name())
        self.__sensorimotor = get_dist_for_action_combination(self.__reference_action.get_name(), self.__generated_action.get_name())
        self.__compiles = get_compilation_results(self.__reference_action.get_name(), self.__generated_action.get_name(), self.__model, self.__run)
        self.__lines = self.__designator.count('\n') + 1

    def convert_to_dict(self) -> dict:
        from .res_column_header import ResultColumnHeaders
        return {
            ResultColumnHeaders.gen: self.__generated_action.get_name(),
            ResultColumnHeaders.ref: self.__reference_action.get_name(),
            ResultColumnHeaders.model: self.__model,
            ResultColumnHeaders.run: self.__run,
            ResultColumnHeaders.wup: self.__wup,
            ResultColumnHeaders.glove: self.__glove_cosine_sim,
            ResultColumnHeaders.smd: self.__sensorimotor,
            ResultColumnHeaders.bleu: self.__bleu_score,
            ResultColumnHeaders.r1: self.__rouge_1['f'],
            ResultColumnHeaders.r2: self.__rouge_2['f'],
            ResultColumnHeaders.rl: self.__rouge_l['f'],
            ResultColumnHeaders.cbs: self.__code_bert_score[2].item(),
            ResultColumnHeaders.chrf: self.__chrf_score,
            ResultColumnHeaders.loc: self.__lines,
            ResultColumnHeaders.comp: self.__compiles
        }
