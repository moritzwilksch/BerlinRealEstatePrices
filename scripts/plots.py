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
################## Price Distribution ##################
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.histplot(dfrent["price"], bins=50, color=DUKEBLUE, ax=axes[0])
sns.histplot(dfbuy["price"], bins=50, color=DUKEBLUE, ax=axes[1])

axes[0].xaxis.set_major_formatter(lambda x, _: f"{x:,.0f}")
axes[0].set_title("Rentals", weight="bold")
axes[1].xaxis.set_major_formatter(lambda x, _: f"{x/1000:,.0f}k" if x < 1e6 else f"{x/1e6:,.1f}m")
axes[1].set_title("Sales", weight="bold")

# set labels and margins
_ = [ax.set_xlabel("Price (EUR)") for ax in axes]
_ = [ax.margins(x=0) for ax in axes]

fig.suptitle("Price Distribution of Listings", weight="bold")
sns.despine()
plt.tight_layout()
plt.savefig(ROOT_DIR + "documents/plots/price_distribution_rentbuy.png", dpi=300, facecolor="w")

#%%
################## Rent Price vs. SQM by private offer ##################

fig, axes = plt.subplots(1, 2, figsize=(8, 4))

sns.scatterplot(
    data=dfrent,
    x="square_meters",
    y="price",
    hue="private_offer",
    palette=[DUKEBLUE, "red"],
    alpha=0.075,
    ax=axes[0]
)

sns.scatterplot(
    data=dfbuy,
    x="square_meters",
    y="price",
    hue="private_offer",
    palette=[DUKEBLUE, "red"],
    alpha=0.075,
    ax=axes[1]
)

axes[0].set_xlabel("Size ($m^2$)")
axes[0].set_ylabel("Price")
sns.despine()

plt.savefig(ROOT_DIR + "documents/plots/price_sqm_scatter.png", dpi=300, facecolor="w")


#%%





