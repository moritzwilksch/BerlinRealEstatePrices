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
    ax=axes[0],
)

sns.scatterplot(
    data=dfbuy,
    x="square_meters",
    y="price",
    hue="private_offer",
    palette=[DUKEBLUE, "red"],
    alpha=0.075,
    ax=axes[1],
)

axes[0].set_xlabel("Size ($m^2$)")
axes[0].set_ylabel("Price")
sns.despine()

plt.savefig(ROOT_DIR + "documents/plots/price_sqm_scatter.png", dpi=300, facecolor="w")


#%%
# ----------------------------- Comparing Coefficients ----------------------------#
def read_latex_summary(path: str) -> pd.DataFrame:
    """
    Reads a LaTeX table from a file and returns a pandas DataFrame.
    """
    return (
        pd.read_csv(
            path,
            sep="&",
            engine="python",
            skiprows=6,
            names=["name", "coef", "std", "tstat", "pval"],
            skipfooter=3,
        )
        .replace(r"[ \\]", "", regex=True)
        .astype({"name": "string", "pval": "float"})
        .assign(name=lambda x: x["name"].str.replace("square_meters", "sqm"))
        .assign(name=lambda x: x["name"].str.replace("object_type", "obj_type"),)
        .assign(name=lambda x: x["name"].str.replace("APARTMENT", "APT"),)
        .assign(name=lambda x: x["name"].str.replace("TEMPORARY", "TEMP"),)
        .set_index("name")
    )


coef_rentals = read_latex_summary(ROOT_DIR + "documents/scripts_output/rentals_model2_summary.tex")
coef_sales = read_latex_summary(ROOT_DIR + "documents/scripts_output/sales_model2_summary.tex")
coef_sales = coef_sales.reindex(coef_rentals.index).reset_index()
coef_rentals = coef_rentals.reset_index()

# exclude the intercept
rentals_ex_intercept = coef_rentals.query("not name == '(Intercept)'")
sales_ex_intercept = coef_sales.query("not name == '(Intercept)'")

# order by rental coefficients
rentals_ex_intercept
order = rentals_ex_intercept.sort_values("coef", ascending=True)["name"].tolist()

rentals_ex_intercept = rentals_ex_intercept.set_index("name").loc[order].reset_index()
sales_ex_intercept = sales_ex_intercept.set_index("name").loc[order].reset_index()


fig, ax = plt.subplots(figsize=(15, 5))
sns.pointplot(
    data=rentals_ex_intercept,
    x="name",
    y="coef",
    color=DUKEBLUE,
    ci=None,
    ax=ax,
    join=False,
    zorder=10,
)
sns.pointplot(
    data=sales_ex_intercept, x="name", y="coef", color="red", ci=None, ax=ax, join=False, zorder=10,
)
ax.errorbar(
    y=rentals_ex_intercept["coef"],
    yerr=rentals_ex_intercept["std"],
    x=rentals_ex_intercept["name"],
    color=DUKEBLUE,
    zorder=5,
    label="Rentals",
)
ax.errorbar(
    y=sales_ex_intercept["coef"],
    yerr=sales_ex_intercept["std"],
    x=sales_ex_intercept["name"],
    color="red",
    zorder=5,
    label="Sales",
)


ax.text(
    x=16.5,
    y=rentals_ex_intercept.query("name == 'obj_typeHOUSE'")["coef"],
    s="Rentals",
    va="center",
    weight="bold",
    color=DUKEBLUE,
)

ax.text(
    x=16.5,
    y=sales_ex_intercept.query("name == 'obj_typeHOUSE'")["coef"],
    s="Sales",
    va="center",
    weight="bold",
    color="red",
)

ratios = (
    pd.DataFrame(
        {
            "name": sales_ex_intercept.name,
            "ratio": sales_ex_intercept.coef / rentals_ex_intercept.coef,
        }
    )
    .replace(np.inf, 1)
    .set_index("name")
    .to_dict()["ratio"]
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right", rotation_mode="anchor")
for lab in ax.get_xticklabels():
    lab.set_y(lab.get_position()[1] - 0.02)
    lab.set_alpha(1) if abs(float(ratios[lab.get_text()]) - 1) > 0.9 else lab.set_alpha(0.33)
    lab.set_weight("bold") if abs(float(ratios[lab.get_text()]) - 1) > 0.9 else lab.set_weight(
        "normal"
    )
ax.tick_params(left=False, bottom=True, size=10)

ax.set_ylabel("Coefficient")
ax.set_xlabel("")
ax.axhline(y=0, color="0.8", linestyle="--", zorder=-1)
sns.despine(bottom=True, left=True)
ax.set_title("Comparison of Fixed Effects for Rentals vs. Sales", weight="bold")
plt.tight_layout()
plt.savefig(ROOT_DIR + "documents/plots/compare_coefs.png", dpi=300, facecolor="w")

#%%
