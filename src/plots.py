import matplotlib.pyplot as plt
import seaborn as sns

def box_with_jitter(df, x, y, hue=None, title=None):
    """
    Box + jitter with circles, no legend, no grid, larger fonts, jitter on top.
    """
    plt.figure(figsize=(8,5))
    ax = sns.boxplot(data=df, x=x, y=y, hue=hue, dodge=bool(hue), linewidth=1, showfliers=False)
    sns.stripplot(data=df, x=x, y=y, hue=hue, dodge=bool(hue), alpha=0.6, size=3, marker='o', edgecolor=None, linewidth=0)
    if hue is not None:
        ax.legend_.remove()
    ax.grid(False)
    ax.set_title(title or f"{y} by {x}", fontsize=14)
    ax.set_xlabel(x, fontsize=12)
    ax.set_ylabel(y, fontsize=12)
    plt.tight_layout()
    return ax
