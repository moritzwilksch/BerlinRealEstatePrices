#%%
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib_inline

matplotlib_inline.backend_inline.set_matplotlib_formats("svg")
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 14

ROOT_DIR = "../"
DUKEBLUE = "#00339B"

#%%
df = pd.read_parquet(ROOT_DIR + "data/berlin_clean.parquet")
# df['to_rent'] = df['to_rent'].astype('category')

#%%
RENT_QUANTILE = 0.98
BUY_QUANTILE = 0.99

rent_cutoff = df.query("to_rent")["price"].quantile(RENT_QUANTILE)
buy_cutoff = df.query("not to_rent")["price"].quantile(BUY_QUANTILE)
print(f"{' Quantile Cutoffs ':-^40}")
print(f"{'RENT cutoff':<15} = €{rent_cutoff:,.2f}")
print(f"{'BUY cutoff':<15} = €{buy_cutoff:,.2f}")
print("-" * 40)

dfrent = df.query("price <= @rent_cutoff and to_rent == True")
dfbuy = df.query("price <= @buy_cutoff and to_rent == False")
dfall = pd.concat([dfrent, dfbuy])

#%%
################## Price Distribution ##################
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
sns.histplot(dfrent["price"], bins=50, color=DUKEBLUE, ax=axes[0])
sns.histplot(dfbuy["price"], bins=50, color=DUKEBLUE, ax=axes[1])

axes[0].xaxis.set_major_formatter(lambda x, _: f"{x:,.0f}")
axes[1].xaxis.set_major_formatter(lambda x, _: f"{x/1000:,.0f}k" if x < 1e6 else f"{x/1e6:,.1f}m")
_ = [ax.set_xlabel("Price") for ax in axes]
fig.suptitle("Price Distribution of Listings for Rent and for Sale", weight="bold")
sns.despine()
plt.tight_layout()
plt.savefig(ROOT_DIR + "documents/plots/price_distribution_rentbuy.png", dpi=300, facecolor="w")

#%%
################## Rent Price vs. SQM by private offer ##################

fig, ax = plt.subplots(figsize=(12, 6))

sns.scatterplot(
    data=dfrent,
    x="square_meters",
    y="price",
    hue="private_offer",
    palette=[DUKEBLUE, "red"],
    alpha=0.075,
    ax=ax
)

ax.set_xlabel("Size ($m^2$)")
ax.set_ylabel("Price")
sns.despine()

#%%


