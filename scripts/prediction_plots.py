#%%
from pandas.core.reshape.merge import merge
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib_inline
import geopandas as gpd
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry.point import Point


matplotlib_inline.backend_inline.set_matplotlib_formats("png")
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 16

ROOT_DIR = "../"
DUKEBLUE = "#00339B"

#%%
leverage_removed = pd.read_parquet(ROOT_DIR + "data/intermediaries/leverage_removed.parquet")
catcols = ["object_type", "rooms", "zip_code"]
leverage_removed[catcols] = leverage_removed[catcols].astype("category")

#%%
model = smf.ols(
    "np.log(price) ~ object_type + private_offer + rooms + square_meters", data=leverage_removed
)
result = model.fit()
print(result.summary())

#%%
hierarchical_model = smf.mixedlm(
    "np.log(price) ~ object_type + private_offer + rooms * square_meters",
    data=leverage_removed,
    groups=leverage_removed["zip_code"],
)
hierarchical_result = hierarchical_model.fit()
hierarchical_result.summary()


#%%

USE_MODEL = result

preds = np.exp(USE_MODEL.predict(leverage_removed))
_df = pd.concat([leverage_removed, pd.DataFrame(preds, columns=["preds"])], axis=1)

room_order = [
    "Missing",
    "Shared",
    "1",
    "2",
    "3",
    "4",
    "5",
]

fig, ax = plt.subplots(figsize=(10, 5))
palette = {
    "APARTMENT": DUKEBLUE,
    "HOUSE": "#95BF74",
    "SHARED_APARTMENT": "#48BEFF",
    "TEMPORARY_LIVING": "#659B5E",
    "HOLIDAY_HOUSE_APARTMENT": "white",
}
sns.pointplot(
    data=_df, x="rooms", y="preds", hue="object_type", palette=palette, ax=ax, order=room_order
)

label_yvals = _df.query("rooms == '5'").groupby("object_type")["preds"].mean().dropna().to_dict()
label_yvals["APARTMENT"] = label_yvals["APARTMENT"] * 0.9
label_yvals["HOUSE"] = label_yvals["HOUSE"] * 1.025
label_yvals["TEMPORARY_LIVING"] = label_yvals["TEMPORARY_LIVING"] * 0.9
label_yvals["SHARED_APARTMENT"] = label_yvals["SHARED_APARTMENT"] * 1.1

for label, yval in label_yvals.items():
    ax.text(6.2, yval, label, verticalalignment="center", weight="bold", color=palette[label])

ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: "€{:,.0f}".format(y)))
ax.set_xlabel("Number of Rooms")
ax.set_ylabel("Rent Price")
ax.set_title("Predicted Rent Price by Number of Rooms", weight="bold")
ax.grid(axis="y", ls="--")
ax.set_xlim(0, 6.1)
ax.legend([], frameon=False)
plt.tight_layout()
sns.despine()
plt.savefig(ROOT_DIR + "documents/plots/predplot_rooms_objtype.png", dpi=300, facecolor="w")


#%%
##################### EXAMPLE PROPERTY #####################
example_prop = pd.DataFrame(
    {
        "object_type": ["APARTMENT"],
        "private_offer": [False],
        "rooms": ["3"],
        "square_meters": [65],
    }
)

cheap = np.exp(
    hierarchical_result.predict(example_prop) + hierarchical_result.random_effects["13059"]["Group"]
).iloc[0]
expensive = np.exp(
    hierarchical_result.predict(example_prop) + hierarchical_result.random_effects["10117"]["Group"]
).iloc[0]

print(f"{cheap = :.2f}€")
print(f"{expensive = :.2f}€")

#%%
USE_RENTALS = False
#################### Random Effects by ZIP ####################
def is_sig(pointestimate, err):
    if pointestimate < 0 and pointestimate + err * 1.96 >= 0:
        return np.nan
    elif pointestimate > 0 and pointestimate - err * 1.96 <= 0:
        return np.nan
    else:
        return pointestimate


geodf = gpd.read_file(ROOT_DIR + "data/plz.geojson")


def plot_geoplot(type_: str, fig, ax):
    """type = "rentals" or "sales" """

    BBOX = (13.0, 52.3, 13.8, 52.7)
    df_dotplot = pd.read_parquet(
        f"../data/intermediaries/ranef_by_zipcode_{type_}.parquet"
    ).sort_values(by="pointestimate")
    df_dotplot["zip"] = df_dotplot["zip"].astype("category")

    df_dotplot = df_dotplot.assign(
        sig=df_dotplot.apply(lambda row: is_sig(row["pointestimate"], row["err"]), axis=1)
    )

    _sorted = df_dotplot.dropna().sort_values(by="sig", ascending=False)
    # print(_sorted.head(5))
    # print(_sorted.tail(5))

    # home = gpd.read_file(ROOT_DIR + "data/home.geojson")

    merged = pd.merge(geodf.rename({"plz": "zip"}, axis=1), df_dotplot, on="zip", how="left")
    merged = merged.assign(
        pointestimate_sig=merged.apply(lambda row: is_sig(row["pointestimate"], row["err"]), axis=1)
    )

    streets = gpd.read_file("../../../brb_geo/gis_osm_roads_free_1.shp", bbox=BBOX)

    fclasses = [
        "motorway",
        "motorway_link",
        "primary",
        "secondary",
        "tertiary",
    ]

    streets = streets.query("fclass.isin(@fclasses)")

    # fig, ax = plt.subplots(figsize=(15, 9))
    merged = merged.to_crs(4326)

    merged.plot(
        column="pointestimate_sig",
        ax=ax,
        edgecolor="black",
        linewidth=0.75,
        # legend=True,
        missing_kwds={"color": "0.95", "hatch": "..."},
    )
    # home.plot(ax=ax, color="red", marker="*", markersize=125)
    ax.set_xticklabels(())
    ax.set_yticklabels(())
    ax.set_xticks(())
    ax.set_yticks(())
    ax.set_title(type_.capitalize(), weight="bold", size=20, family="Arial")
    sns.despine(left=True, bottom=True)

    # Scalebar - Need to calculate ratio from pixels to real world
    points = gpd.GeoSeries([Point(-73.5, 40.5), Point(-74.5, 40.5)], crs=4326)
    points = points.to_crs(32619)
    distance_meters = points[0].distance(points[1])
    ax.add_artist(ScaleBar(distance_meters, location="lower left"))

    plt.tight_layout()

    fig.colorbar(ax.collections[0], ax=ax, label="Random Intercept", shrink=0.5)

    streets.plot(color="0.8", ax=ax, zorder=-1)
    ax.set_xlim(13, 13.8)
    ax.set_ylim(52.3, 52.7)

    return merged


fig, axes = plt.subplots(1, 2, figsize=(15, 9))
merged_rentals = plot_geoplot("rentals", fig, axes[0])
merged_sales = plot_geoplot("sales", fig, axes[1])


plt.savefig(ROOT_DIR + "documents/plots/geoplot_rentals_and_sales.png", dpi=300, facecolor="w")

#%%


#%%
merged = merged_rentals  # CAUTION


mitte = geodf.query("plz == '10117'").to_crs(epsg=32642).centroid.to_frame().set_geometry(0)
mitte_df = mitte.sjoin_nearest(
    merged.to_crs(epsg=32642), how="right", distance_col="dist_to_mitte"
).assign(dist_to_mitte=lambda x: x["dist_to_mitte"] / 1000)

#%%
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(
    data=mitte_df, x="dist_to_mitte", y=np.exp(mitte_df["pointestimate_sig"]), ax=ax, color=DUKEBLUE
)
ax.axhline(1, color="0.7", linestyle="--")

good_deal = ["13627", "12057", "10969"]
_annot_df = mitte_df.query("zip.isin(@good_deal)")
for x, y, zipcode in zip(
    _annot_df["dist_to_mitte"], np.exp(_annot_df["pointestimate_sig"]), _annot_df["zip"]
):
    ax.text(x, y - 0.05, str(zipcode), ha="right")

ax.set_title("Distance to Mitte (km) vs. Multiplicative Price Effect", weight="bold")
ax.set_xlabel("Distance to Mitte (km)")
ax.set_ylabel("Multiplicative Price Effect")
sns.despine()
plt.tight_layout()
plt.savefig(ROOT_DIR + "documents/plots/dist_to_mitte.png", dpi=300, facecolor="w")
