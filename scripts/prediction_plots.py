#%%
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib_inline

matplotlib_inline.backend_inline.set_matplotlib_formats("png")
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 16

ROOT_DIR = "../"
DUKEBLUE = "#00339B"

#%%
leverage_removed = pd.read_parquet(ROOT_DIR + "data/intermediaries/leverage_removed.parquet")

#%%
model = smf.ols(
    "np.log(price) ~ object_type + private_offer + rooms + square_meters", data=leverage_removed
)
result = model.fit()
print(result.summary())


#%%
preds = np.exp(result.predict(leverage_removed))
_df = pd.concat([leverage_removed, pd.DataFrame(preds, columns=["preds"])], axis=1)

fig, ax = plt.subplots(figsize=(10, 5))
palette = {
    "APARTMENT": DUKEBLUE,
    "HOUSE": "#95BF74",
    "SHARED_APARTMENT": "#48BEFF",
    "TEMPORARY_LIVING": "#659B5E",
    "HOLIDAY_HOUSE_APARTMENT": "white",
}
sns.pointplot(data=_df, x="rooms", y="preds", hue="object_type", palette=palette, ax=ax)

label_yvals = _df.query("rooms == '5'").groupby("object_type")["preds"].mean().dropna().to_dict()
label_yvals["APARTMENT"] = label_yvals["APARTMENT"] * 0.9

for label, yval in label_yvals.items():
    ax.text(4.2, yval, label, verticalalignment="center", weight="bold", color=palette[label])

ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: "€{:,.0f}".format(y)))
ax.set_xlabel("Number of Rooms")
ax.set_ylabel("Rent Price")
ax.set_title("Predicted Rent Price by Number of Rooms", weight="bold")
ax.grid(axis="y", ls="--")
ax.set_xlim(0, 4.1)
ax.legend([], frameon=False)
plt.tight_layout()
sns.despine()
plt.savefig(ROOT_DIR + "documents/plots/predplot_rooms_objtype.png", dpi=300, facecolor="w")

#%%
#################### Random Effects by ZIP ####################
df_dotplot = pd.read_parquet(
    "../data/intermediaries/ranef_by_zipcode.parquet"
).sort_values(by="pointestimate")
df_dotplot["zip"] = df_dotplot["zip"].astype("category")

df_dotplot

#%%
