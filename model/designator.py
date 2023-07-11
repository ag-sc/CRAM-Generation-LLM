from .action import Action
import eval as ev


class GeneratedDesignator:
    wn_handler = ev.WordNetHandler()
    glove_handler = ev.GloveHandler()

    def __init__(self, ref_act: Action, gen_act: Action, designator: str):
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

    def get_generated_designator(self) -> str:
        return self.__designator

    def get_reference_designator(self) -> str:
        return self.__reference_action.get_designator()

    def get_reference_action_name(self) -> str:
        return self.__reference_action.get_name()

    def get_generated_action_name(self) -> str:
        return self.__generated_action.get_name()

    def calculate_metrics(self):
        ref = [self.get_reference_designator()]
        gen = [self.get_generated_designator()] * len(ref)
        self.__bleu_score = ev.calculate_bleu(self.get_generated_designator(), self.get_reference_designator())
        self.__rouge_1 = ev.calculate_rouge(self.get_generated_designator(), self.get_reference_designator(), '1')
        self.__rouge_2 = ev.calculate_rouge(self.get_generated_designator(), self.get_reference_designator(), '2')
        self.__rouge_l = ev.calculate_rouge(self.get_generated_designator(), self.get_reference_designator(), 'lcs')
        self.__code_bert_score = ev.calculate_code_bert_score(gen, ref)
        self.__chrf_score = ev.calculate_chrf(gen[0], ref[0])
        self.__wup = GeneratedDesignator.wn_handler.calculate_wup(self.__reference_action, self.__generated_action)
        self.__glove_cosine_sim = GeneratedDesignator.glove_handler.calculate_cosine(self.get_generated_action_name(), self.get_reference_action_name())

    def convert_to_dict(self) -> dict:
        return {
            'Generated': self.__generated_action.get_name(),
            'Reference': self.__reference_action.get_name(),
            'WuP': self.__wup,
            'GloVe-Similarity': self.__glove_cosine_sim,
            'BLEU': self.__bleu_score,
            #'ROUGE-1-PR': self.__rouge_1['p'],
            #'ROUGE-1-RE': self.__rouge_1['r'],
            #'ROUGE-1-F1': self.__rouge_1['f'],
            'ROUGE-1': self.__rouge_1['f'],
            'ROUGE-2': self.__rouge_2['f'],
            #'ROUGE-L-PR': self.__rouge_l['p'],
            #'ROUGE-L-RE': self.__rouge_l['r'],
            #'ROUGE-L-F1': self.__rouge_l['f'],
            'ROUGE-L': self.__rouge_l['f'],
            #'CodeBERTScore-PR': self.__code_bert_score[0].item(),
            #'CodeBERTScore-RE': self.__code_bert_score[1].item(),
            #'CodeBERTScore-F1': self.__code_bert_score[2].item(),
            'CodeBERTScore': self.__code_bert_score[2].item(),
            'chrF': self.__chrf_score,
        }
