"""The Diary of a CEO — YouTube Channel Analysis (Public Dashboard)."""

import os

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from components.metrics import metric_row, format_number, format_duration

st.set_page_config(
    page_title="DOAC YouTube Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

ERAS = {
    "Early": ("2017-09-01", "2019-12-31"),
    "Growth": ("2020-01-01", "2021-12-31"),
    "Scale": ("2022-01-01", "2023-12-31"),
    "Dominant": ("2024-01-01", "2026-12-31"),
}

MILESTONES = {
    "2017-09-29": "First episode launched",
    "2021-01-01": "Dragons' Den debut",
    "2021-07-28": "First live show (Manchester)",
    "2022-06-01": "10M downloads/month milestone",
    "2023-09-01": "Book: The 33 Laws of Business and Life",
    "2024-12-01": "1 billion total streams",
    "2025-12-01": "#2 podcast globally on Spotify",
    "2026-03-01": "iHeart Podcast Award (Business & Finance)",
}

# ---- Load data ----
@st.cache_data
def load_videos():
    return pd.read_parquet(os.path.join(DATA_DIR, "videos.parquet"))

df = load_videos()

st.title("The Diary of a CEO — YouTube Channel Analysis")
st.markdown(
    "Comprehensive analysis of [@TheDiaryOfACEO](https://www.youtube.com/@TheDiaryOfACEO) "
    "growth, content strategy, and audience insights."
)

# ---- Hero Metrics ----
st.subheader("Key Metrics")

total_views = df["view_count"].sum()
total_videos = len(df)
avg_engagement = df["engagement_rate"].mean() * 100

metrics = [
    {"label": "Total Views", "value": format_number(total_views)},
    {"label": "Videos", "value": f"{total_videos:,}"},
    {"label": "Avg Views/Video", "value": format_number(df["view_count"].mean())},
    {"label": "Avg Engagement Rate", "value": f"{avg_engagement:.2f}%"},
]
metric_row(metrics)

metrics2 = [
    {"label": "Median Views/Video", "value": format_number(df["view_count"].median())},
    {"label": "Avg Duration", "value": format_duration(df["duration_seconds"].mean())},
    {"label": "Total Likes", "value": format_number(df["like_count"].sum())},
    {"label": "Total Comments", "value": format_number(df["comment_count"].sum())},
]
metric_row(metrics2)

st.markdown("---")

# ---- Publishing Heatmap ----
st.subheader("Publishing Frequency")

df_heatmap = df.copy()
df_heatmap["year"] = df_heatmap["published_at"].dt.year
df_heatmap["month_num"] = df_heatmap["published_at"].dt.month

pivot = df_heatmap.groupby(["year", "month_num"]).size().reset_index(name="count")
pivot_table = pivot.pivot(index="year", columns="month_num", values="count").fillna(0)
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
pivot_table.columns = [month_names[m - 1] for m in pivot_table.columns]

fig_heat = go.Figure(data=go.Heatmap(
    z=pivot_table.values,
    x=pivot_table.columns.tolist(),
    y=[str(y) for y in pivot_table.index.tolist()],
    colorscale="YlOrRd",
    text=pivot_table.values.astype(int),
    texttemplate="%{text}",
    hoverongaps=False,
))
fig_heat.update_layout(title="Videos Published per Month", height=350, template="plotly_white")
st.plotly_chart(fig_heat, use_container_width=True)

# ---- Long vs Clip publishing ----
df_pub = df.copy()
df_pub["month_key"] = df_pub["published_at"].dt.to_period("M").dt.to_timestamp()
monthly_long = df_pub[~df_pub["is_clips"]].groupby("month_key").size().reset_index(name="long_videos")
monthly_clip = df_pub[df_pub["is_clips"]].groupby("month_key").size().reset_index(name="clip_videos")
monthly_both = monthly_long.merge(monthly_clip, on="month_key", how="outer").fillna(0).sort_values("month_key")

fig_dual = go.Figure()
fig_dual.add_trace(go.Scatter(
    x=monthly_both["month_key"], y=monthly_both["long_videos"],
    name="Long Videos (5+ min)", mode="lines+markers",
    line=dict(color="#42A5F5", width=2), marker=dict(size=5), yaxis="y",
))
fig_dual.add_trace(go.Scatter(
    x=monthly_both["month_key"], y=monthly_both["clip_videos"],
    name="Clips (< 5 min)", mode="lines+markers",
    line=dict(color="#FF7043", width=2), marker=dict(size=5), yaxis="y2",
))
fig_dual.update_layout(
    title="Monthly Publishing: Long Videos vs Clips",
    template="plotly_white", height=400, hovermode="x unified",
    xaxis=dict(title="Month"),
    yaxis=dict(title=dict(text="Long Videos", font=dict(color="#42A5F5")), tickfont=dict(color="#42A5F5")),
    yaxis2=dict(title=dict(text="Clips", font=dict(color="#FF7043")), tickfont=dict(color="#FF7043"),
                overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
st.plotly_chart(fig_dual, use_container_width=True)

# ---- Milestones ----
st.subheader("Key Milestones")
milestones_df = pd.DataFrame([
    {"date": pd.Timestamp(d), "event": e} for d, e in MILESTONES.items()
]).sort_values("date")
for _, row in milestones_df.iterrows():
    st.markdown(f"**{row['date'].strftime('%b %Y')}** — {row['event']}")

st.markdown("---")

# ---- Era Breakdown ----
st.subheader("Era Definitions")
st.markdown(
    "We divide the channel's history into **four eras** based on distinct phases of "
    "growth and strategy shifts:"
)

era_defs = {
    "Early": "Channel launch and early experimentation. Finding the format and audience.",
    "Growth": "Rapid growth driven by Dragons' Den and viral episodes. Long-form interviews solidified.",
    "Scale": "Consistent cadence, high-profile guests, book launch. Major subscriber milestones crossed.",
    "Dominant": "Market-leading position. #1-2 podcast globally, 1B+ streams, award-winning.",
}
era_table = [{"Era": k, "Start": v[0], "End": v[1], "Description": era_defs[k]} for k, v in ERAS.items()]
st.dataframe(pd.DataFrame(era_table), use_container_width=True, hide_index=True)

st.markdown("---")

# ---- Era Metrics ----
st.subheader("Key Metrics by Era")

era_stats = df.groupby("era").agg(
    videos=("video_id", "count"),
    total_views=("view_count", "sum"),
    avg_views=("view_count", "mean"),
    median_views=("view_count", "median"),
    max_views=("view_count", "max"),
    avg_engagement=("engagement_rate", "mean"),
    avg_duration_sec=("duration_seconds", "mean"),
).reset_index()

era_order = ["Early", "Growth", "Scale", "Dominant"]
era_stats["era"] = pd.Categorical(era_stats["era"], categories=era_order, ordered=True)
era_stats = era_stats.sort_values("era")

display_era = pd.DataFrame({
    "Era": era_stats["era"],
    "Videos": era_stats["videos"],
    "Total Views": era_stats["total_views"].apply(format_number),
    "Avg Views": era_stats["avg_views"].apply(lambda x: format_number(int(x))),
    "Median Views": era_stats["median_views"].apply(lambda x: format_number(int(x))),
    "Max Views": era_stats["max_views"].apply(format_number),
    "Avg Engagement %": (era_stats["avg_engagement"] * 100).round(2).astype(str) + "%",
    "Avg Duration": era_stats["avg_duration_sec"].apply(format_duration),
})
st.dataframe(display_era, use_container_width=True, hide_index=True)

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(era_stats, x="era", y="avg_views", title="Average Views by Era",
                 template="plotly_white", color="era", color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.bar(era_stats, x="era", y="avg_engagement", title="Avg Engagement Rate by Era",
                 template="plotly_white", color="era", color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(yaxis_tickformat=".2%")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Data snapshot collected via YouTube Data API v3. Dashboard built with Streamlit.")
