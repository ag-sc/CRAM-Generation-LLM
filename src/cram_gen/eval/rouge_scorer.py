from rouge import Rouge


def calculate_rouge(gen: str, ref: str, metr_type: str):
    rouge = Rouge()
    scores = rouge.get_scores(gen, ref)
    if metr_type == 'lcs':
        return scores[0]['rouge-l']
    elif metr_type == '2':
        return scores[0]['rouge-2']
    else:
        return scores[0]['rouge-1']
