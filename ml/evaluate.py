from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import math
import numpy as np

def plot_confusion_matrix(models_preds, y_true, titles):
    """
    Visualize the confusion matrix for one or multiple models side by side
    without seaborn.
    """
    n_models = len(models_preds)
    n_cols = 2
    n_rows = math.ceil(n_models / n_cols)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows))
    axes = axes.ravel()

    for i, (y_pred, title) in enumerate(zip(models_preds, titles)):
        cm = confusion_matrix(y_true, y_pred)

        # Custom labels
        labels = np.array([
            [f"TN\n{cm[0,0]}", f"FP\n{cm[0,1]}"],
            [f"FN\n{cm[1,0]}", f"TP\n{cm[1,1]}"]
        ])
        
        # heatmap using imshow + cmap
        im = axes[i].imshow(cm, interpolation='nearest', cmap="Blues")
        axes[i].set_title(f"Confusion Matrix - {title}")
        axes[i].set_xlabel("Predicted Label")
        axes[i].set_ylabel("True Label")

        # Annotate each cell manually
        thresh = cm.max() / 2.
        for r in range(2):
            for c in range(2):
                color = "white" if cm[r, c] > thresh else "black"
                axes[i].text(
                    c, r, labels[r, c],
                    ha="center", va="center",
                    color=color, fontsize=12
                )

        axes[i].set_xticks([0, 1])
        axes[i].set_yticks([0, 1])

    # Remove unused axes if odd
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # (Opsional) tambahkan colorbar agar mirip seaborn
    fig.colorbar(im, ax=axes, fraction=0.02, pad=0.03)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.4, wspace=0.3)
    plt.show()
