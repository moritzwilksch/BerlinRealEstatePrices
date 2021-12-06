#%%
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib_inline

matplotlib_inline.backend_inline.set_matplotlib_formats("png")
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 14

ROOT_DIR = "../"
DUKEBLUE = "#00339B"

dfrent = pd.read_parquet(ROOT_DIR + "data/dfrent.parquet")
dfbuy = pd.read_parquet(ROOT_DIR + "data/dfbuy.parquet")
#%%

dfrent_cutoff = np.quantile(dfrent.square_meters.fillna(0), 0.999)
dfbuy_cutoff = np.quantile(dfbuy.square_meters.fillna(0), 0.999)

dfrent = dfrent.query("square_meters <= @dfrent_cutoff")
dfbuy = dfbuy.query("square_meters <= @dfbuy_cutoff")

#%%
# --------------------------- Appendix A ---------------------------


def hatch_missing(ax):
    ax.patches[-1].set_hatch("///")


fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)

colors = [DUKEBLUE] * 6 + ["0.8"]

sns.countplot(x=dfrent.rooms, ax=axes[0], color=DUKEBLUE, ec="k", palette=colors, zorder=10)
sns.countplot(x=dfbuy.rooms, ax=axes[1], color=DUKEBLUE, ec="k", palette=colors, zorder=10)

[hatch_missing(ax) for ax in axes]
[ax.grid("major", axis='y', ls="--", zorder=-1) for ax in axes]

axes[0].set_title("Rentals", weight="bold")
axes[1].set_title("Sales", weight="bold")

fig.suptitle("Number of Rooms", weight="bold")

plt.tight_layout()
sns.despine()

plt.savefig(ROOT_DIR + "documents/plots/rooms_distribution_rentbuy.png", dpi=300, facecolor="w")

