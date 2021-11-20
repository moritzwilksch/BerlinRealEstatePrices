#%%
import geopandas as gpd
import matplotlib.pyplot as plt

# df = gpd.read_file("../../../strassenkataster-potsdam.geojson")

# fig, ax = plt.subplots(1, 1, figsize=(20, 20))
# df.plot(ax=ax, color="black")

#%%
df = gpd.read_file("../../../brb_geo/gis_osm_roads_free_1.shp")

#%%
fclasses = [
    "motorway",
    "motorway_link",
    # "residential",
    "primary",
    "secondary",
    # "tertiary",
    # "living_street",
    # "service",
    # "footway",
    # "unclassified",
    # "trunk",
    # "cycleway",
    # "secondary_link",
    # "track_grade1",
    # "track_grade3",
    # "steps",
    # "trunk_link",
    # "track",
    # "pedestrian",
    # "path",
    # "primary_link",
    # "tertiary_link",
    # "track_grade5",
    # "track_grade4",
    # "track_grade2",
    # "bridleway",
    # "unknown",
]


fig, ax = plt.subplots(1, 1, figsize=(20, 20))
df.query("fclass.isin(@fclasses)").plot(color="black", ax=ax)
