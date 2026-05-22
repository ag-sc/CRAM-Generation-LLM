from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import BoundaryNorm

from src.cram_gen.utils.paths import CRAM_GEN_FOLDER

# Column Mapping
gen_metr_ax = {
    'BLEU': 'BLEU',
    'ROUGE-1': 'R-1',
    'ROUGE-2': 'R-2',
    'ROUGE-L': 'R-L',
    'CodeBERTScore': 'CBS',
    'chrF': 'chrF',
    'LoC': 'LoC',
    'Compilation': 'Build.',
}
sem_met_ax = {
    'WuP': 'WuP',
    'GloVe-Similarity': 'GloVe',
    'Sensorimotor Distance': 'SMD',
}


def visualise_correlations(models: List[str]):
    for m in models:
        process_and_visualise_correlation_data(m)


def process_and_visualise_correlation_data(model: str):
    file = f'{CRAM_GEN_FOLDER / f"correlation_results_{model}.csv"}'
    df = pd.read_csv(file)

    sem_metr_labels = [sem_met_ax.get(m, m) for m in df["metric"].values]
    r_columns = [col for col in df.columns if col.endswith("_r")]
    p_columns = [col for col in df.columns if col.endswith("_p")]
    gen_metr_labels = [gen_metr_ax.get(c.replace("_r", ""), c.replace("_r", "")) for c in r_columns]

    correlations = df[r_columns].to_numpy()
    p_values = df[p_columns].to_numpy()
    create_and_save_heatmap(p_values, correlations, gen_metr_labels, sem_metr_labels, model)


def create_and_save_heatmap(p_values, correlations, x_labels, y_labels, model):
    # Mask for significance (only paint when p > 0.05)
    mask = p_values > 0.05
    # Prepare a colormap: 3 reds for negative, 3 greens for positive
    bounds = [-1, -0.5, -0.3, 0, 0.3, 0.5, 1]
    cmap = plt.cm.RdYlGn
    norm = BoundaryNorm(bounds, cmap.N)

    # Replace values where p <= 0.05 with a neutral gray background
    plot_data = np.where(mask, 0, correlations)  # placeholder values for coloring

    # Create heatmap
    plt.figure(figsize=(9, 4))
    ax = sns.heatmap(plot_data, annot=correlations, fmt=".3f", cmap=cmap, norm=norm, cbar=True, linewidths=0.5,
                     linecolor='gray', annot_kws={"color": "black"}, xticklabels=x_labels, yticklabels=y_labels)

    # Overlay gray for non-significant cells
    for i in range(plot_data.shape[0]):
        for j in range(plot_data.shape[1]):
            if mask[i, j]:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=True, color='lightgray', edgecolor='gray', lw=0.5))

    plt.tight_layout()
    plt.savefig(f"{CRAM_GEN_FOLDER}/plots/heatmap_{model}.png", dpi=300)  # save as PNG, high resolution
    plt.show()
