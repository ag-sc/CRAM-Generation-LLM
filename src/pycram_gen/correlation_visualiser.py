from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import BoundaryNorm

# Column Mapping
gen_metr_ax = {
    'ROUGE-L': 'R-L',
    'chrF': 'chrF',
    'CodeBERTScore': 'CBS',
    'CodeBLEU': 'CoB',
    'CrystalBLEU': 'CrB',
    'Edit Distance': 'ED',
    'Run Success': 'RunS',
    'Simulation': 'SimQ',
}
sem_met_ax = {
    'Wu-Palmer Similarity': 'WuP',
    'Cosine Similarity GloVe': 'GloVe',
    'Sensorimotor Distance': 'SMD',
}


def visualise_correlations(models: List[str]):
    for m in models:
        process_and_visualise_correlation_data(m)


def process_and_visualise_correlation_data(model: str):
    file = f'/home/jan-philipp/Git/Projects/ChatGPT-CRAM-Generation/data/pycram_generation/{model.lower()}/correlations.csv'
    df = pd.read_csv(file)

    # Keep only rows whose metric exists in mapping
    row_mask = df.iloc[:, 0].isin(gen_metr_ax.keys())
    df = df[row_mask]

    gen_metr_labels = [gen_metr_ax[m] for m in df.iloc[:, 0]]
    r_columns = [col for col in df.columns if col.endswith(" rho")]
    p_columns = [col for col in df.columns if col.endswith(" p")]

    # Keep only semantic metrics in mapping
    valid_pairs = [
        (r_col, p_col)
        for r_col, p_col in zip(r_columns, p_columns)
        if r_col.replace(" rho", "") in sem_met_ax
    ]

    r_columns = [r for r, _ in valid_pairs]
    p_columns = [p for _, p in valid_pairs]

    sem_metr_labels = [
        sem_met_ax[col.replace(" rho", "")]
        for col in r_columns
    ]

    correlations = df[r_columns].to_numpy().T
    p_values = df[p_columns].to_numpy().T
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
    plt.savefig(f'/home/jan-philipp/Git/Projects/ChatGPT-CRAM-Generation/data/pycram_generation/{model.lower()}/correlation_heatmap.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    models = ["gpt-3.5-turbo-0301", "gpt-3.5-turbo-1106", "gpt-4-0613", "gpt-4-1106-preview"]
    visualise_correlations(models)