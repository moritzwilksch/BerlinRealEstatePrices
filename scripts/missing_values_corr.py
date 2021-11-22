#%%
import pandas as pd

#%%
df = pd.read_parquet("../data/berlin_clean.parquet")

df.isna().melt(value_vars=df.columns).pivot_table(
    index="variable", columns="variable", values="value", aggfunc="sum"
).fillna(0).style.background_gradient(cmap="coolwarm")

#%%
import polars as pl

#%%
pdf = pl.read_parquet("../data/berlin_clean.parquet")

#%%
pdf.with_columns(pl.col("*").is_null())#.melt(id_vars=pdf.columns, value_vars=pdf.columns)

# .with_column(pl.col("value").cast(pl.UInt8)).groupby("variable").pivot("variable", "value")

#%%

pdf
