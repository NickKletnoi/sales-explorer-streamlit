import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sales Explorer", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    """Build sample data once; cached so reruns are instant."""
    rng = np.random.default_rng(42)
    dates = pd.date_range("2026-01-01", periods=180)
    frames = []
    for region, base in [("East", 1000), ("West", 1200), ("South", 800)]:
        frames.append(pd.DataFrame({
            "date": dates,
            "region": region,
            "revenue": rng.normal(base, 150, len(dates)).round(2),
        }))
    return pd.concat(frames, ignore_index=True)


df = load_data()

st.title("Sales Explorer")

# --- Sidebar filters ---
st.sidebar.header("Filters")
regions = st.sidebar.multiselect(
    "Region", options=sorted(df["region"].unique()), default=sorted(df["region"].unique())
)
date_range = st.sidebar.date_input(
    "Date range",
    value=(df["date"].min().date(), df["date"].max().date()),
    min_value=df["date"].min().date(),
    max_value=df["date"].max().date(),
)

# date_input returns a 1-tuple while the user is mid-selection
if len(date_range) != 2:
    st.info("Select both a start and an end date.")
    st.stop()

start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
filtered = df[df["region"].isin(regions) & df["date"].between(start, end)]

if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# --- Summary metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total revenue", f"${filtered['revenue'].sum():,.0f}")
col2.metric("Average daily revenue", f"${filtered['revenue'].mean():,.0f}")
col3.metric("Days in range", filtered["date"].nunique())

# --- Chart and table ---
tab_chart, tab_table = st.tabs(["Chart", "Data"])

with tab_chart:
    pivot = filtered.pivot(index="date", columns="region", values="revenue")
    st.line_chart(pivot)

with tab_table:
    st.dataframe(filtered, use_container_width=True)
    st.download_button(
        "Download CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="sales_filtered.csv",
        mime="text/csv",
    )
