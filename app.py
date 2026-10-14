from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sales Explorer", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the checked-in sales dataset."""
    csv_path = Path(__file__).parent / "sales_explorer_source.csv"
    return pd.read_csv(csv_path, parse_dates=["date"])


df = load_data()

st.title("Sales Explorer")

# --- Sidebar filters ---
st.sidebar.header("Filters")
regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique()),
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
tab_chart, tab_calendar, tab_table = st.tabs(["Chart", "Calendar heatmap", "Data"])

with tab_chart:
    pivot = filtered.pivot(index="date", columns="region", values="revenue")
    st.line_chart(pivot)

with tab_calendar:
    st.subheader("When do sales peak?")
    st.caption(
        "Each square is one day, with revenue summed across the selected regions. "
        "Darker means stronger sales, so hot and cold streaks stand out at a glance."
    )

    daily = filtered.groupby("date", as_index=False)["revenue"].sum()
    daily["week_start"] = daily["date"] - pd.to_timedelta(
        daily["date"].dt.weekday, unit="D"
    )
    daily["weekday"] = daily["date"].dt.day_name()
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    best = daily.loc[daily["revenue"].idxmax()]
    worst = daily.loc[daily["revenue"].idxmin()]
    by_weekday = daily.groupby("weekday")["revenue"].mean()
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Best day",
        f"${best['revenue']:,.0f}",
        best["date"].strftime("%a, %b %d"),
        delta_color="off",
    )
    c2.metric(
        "Weakest day",
        f"${worst['revenue']:,.0f}",
        worst["date"].strftime("%a, %b %d"),
        delta_color="off",
    )
    c3.metric(
        "Strongest weekday",
        by_weekday.idxmax(),
        f"avg ${by_weekday.max():,.0f}",
        delta_color="off",
    )

    heatmap = (
        alt.Chart(daily)
        .mark_rect(cornerRadius=3, stroke="white", strokeWidth=2)
        .encode(
            x=alt.X(
                "week_start:T",
                title=None,
                timeUnit="yearmonthdate",
                axis=alt.Axis(
                    format="%b %d", labelAngle=0, labelOverlap=True, grid=False
                ),
            ),
            y=alt.Y(
                "weekday:O",
                sort=weekday_order,
                title=None,
                axis=alt.Axis(domain=False, ticks=False),
            ),
            color=alt.Color(
                "revenue:Q",
                title="Revenue ($)",
                scale=alt.Scale(scheme="blues"),
                legend=alt.Legend(orient="bottom", gradientLength=300, format="$,.0f"),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date", format="%A, %b %d, %Y"),
                alt.Tooltip("revenue:Q", title="Revenue", format="$,.0f"),
            ],
        )
        .properties(height=280)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(heatmap, use_container_width=True)

    st.markdown("**Average revenue by weekday**")
    weekday_df = by_weekday.reindex(weekday_order).rename("avg_revenue").reset_index()
    bars = (
        alt.Chart(weekday_df)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("avg_revenue:Q", title=None, axis=alt.Axis(format="$,.0f")),
            y=alt.Y("weekday:O", sort=weekday_order, title=None),
            color=alt.condition(
                alt.datum.avg_revenue == float(by_weekday.max()),
                alt.value("#1f77b4"),
                alt.value("#c6dbef"),
            ),
            tooltip=[
                alt.Tooltip("weekday:O", title="Weekday"),
                alt.Tooltip("avg_revenue:Q", title="Avg revenue", format="$,.0f"),
            ],
        )
        .properties(height=220)
    )
    st.altair_chart(bars, use_container_width=True)

with tab_table:
    st.dataframe(filtered, use_container_width=True)
    st.download_button(
        "Download CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="sales_filtered.csv",
        mime="text/csv",
    )
