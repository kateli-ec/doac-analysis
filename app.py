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

MILESTONES = {
    "2017-09-29": "First episode launched",
    "2022-01-06": "Steven Bartlett's Dragons' Den debut (youngest ever Dragon)",
    "2022-05-01": "10M downloads in a single month (first time)",
    "2023-01-06": "1M YouTube subscribers",
    "2023-03-01": "Viral growth month (avg 4.8M views/episode)",
    "2023-08-29": "Book launch: The 33 Laws of Business and Life (#1 Sunday Times bestseller)",
    "2024-05-01": "Samsung TV deal (first podcast on Samsung TV Plus 24/7)",
    "2024-11-21": "1 billion total streams (first UK podcast to hit this milestone)",
    "2025-06-01": "10M YouTube subscribers",
    "2025-07-05": "First short-form clip published (clip strategy begins)",
    "2025-07-01": "TIME100 Creators list (Leaders category)",
    "2025-12-01": "#2 podcast globally on Spotify Wrapped 2025",
    "2026-03-01": "iHeart Podcast Award (Best Business & Finance)",
}

# ---- Load data ----
@st.cache_data
def load_videos():
    return pd.read_parquet(os.path.join(DATA_DIR, "videos.parquet"))

df = load_videos()

# Subscriber count snapshot
sub_count = 15_700_000  # From API collection on 2026-04-08

df_episodes = df[~df["is_clips"]]
df_clips = df[df["is_clips"]]

# ==================================================================
# TITLE
# ==================================================================
st.title("The Diary of a CEO — YouTube Channel Analysis")
st.markdown(
    "Comprehensive analysis of [@TheDiaryOfACEO](https://www.youtube.com/@TheDiaryOfACEO) "
    "growth, content strategy, and audience insights."
)
st.markdown("---")

# ==================================================================
# CHANNEL OVERVIEW (Episodes + Clips)
# ==================================================================
st.header("Channel Overview (Episodes + Clips)")

total_views = df["view_count"].sum()
total_videos = len(df)
avg_engagement = df["engagement_rate"].mean() * 100

metrics = [
    {"label": "Subscribers", "value": format_number(sub_count)},
    {"label": "Total Views", "value": format_number(total_views)},
    {"label": "Videos (all)", "value": f"{total_videos:,}"},
    {"label": "Avg Engagement Rate", "value": f"{avg_engagement:.2f}%"},
]
metric_row(metrics)

metrics2 = [
    {"label": "Avg Views/Video", "value": format_number(df["view_count"].mean())},
    {"label": "Median Views/Video", "value": format_number(df["view_count"].median())},
    {"label": "Avg Duration", "value": format_duration(df["duration_seconds"].mean())},
    {"label": "Total Likes", "value": format_number(df["like_count"].sum())},
]
metric_row(metrics2)

st.markdown("---")

# ==================================================================
# CHANNEL OVERVIEW (Episodes Only, No Clips)
# ==================================================================
st.header("Channel Overview (Episodes Only, No Clips)")

metrics_ep = [
    {"label": "Subscribers", "value": format_number(sub_count)},
    {"label": "Total Views", "value": format_number(df_episodes["view_count"].sum())},
    {"label": "Videos", "value": f"{len(df_episodes):,}"},
    {"label": "Avg Engagement Rate", "value": f"{df_episodes['engagement_rate'].mean() * 100:.2f}%"},
]
metric_row(metrics_ep)

metrics_ep2 = [
    {"label": "Avg Views/Video", "value": format_number(df_episodes["view_count"].mean())},
    {"label": "Median Views/Video", "value": format_number(df_episodes["view_count"].median())},
    {"label": "Avg Duration", "value": format_duration(df_episodes["duration_seconds"].mean())},
    {"label": "Total Likes", "value": format_number(df_episodes["like_count"].sum())},
]
metric_row(metrics_ep2)

st.caption(f"Clips excluded: {len(df_clips)} short videos (< 5 min) removed from this section.")

st.markdown("---")

# ==================================================================
# CHANNEL OVERVIEW (Clips Only, No Episodes)
# ==================================================================
st.header("Channel Overview (Clips Only, No Episodes)")

if len(df_clips) > 0:
    metrics_cl = [
        {"label": "Subscribers", "value": format_number(sub_count)},
        {"label": "Total Views", "value": format_number(df_clips["view_count"].sum())},
        {"label": "Videos", "value": f"{len(df_clips):,}"},
        {"label": "Avg Engagement Rate", "value": f"{df_clips['engagement_rate'].mean() * 100:.2f}%"},
    ]
    metric_row(metrics_cl)

    metrics_cl2 = [
        {"label": "Avg Views/Video", "value": format_number(df_clips["view_count"].mean())},
        {"label": "Median Views/Video", "value": format_number(df_clips["view_count"].median())},
        {"label": "Avg Duration", "value": format_duration(df_clips["duration_seconds"].mean())},
        {"label": "Total Likes", "value": format_number(df_clips["like_count"].sum())},
    ]
    metric_row(metrics_cl2)

    st.caption(f"Episodes excluded: {len(df_episodes)} long videos (5+ min) removed from this section.")
else:
    st.info("No clips found in the dataset.")

st.markdown("---")

# ==================================================================
# VIEWS OVER TIME
# ==================================================================
st.header("Views Over Time")

df_monthly = df.copy()
df_monthly["month"] = df_monthly["published_at"].dt.to_period("M").dt.to_timestamp()

monthly_views = df_monthly.groupby("month").agg(
    total_views=("view_count", "sum"),
    avg_views=("view_count", "mean"),
    video_count=("video_id", "count"),
).reset_index()

monthly_views["rolling_avg"] = monthly_views["total_views"].rolling(3, min_periods=1).mean()

fig_views = go.Figure()
fig_views.add_trace(go.Bar(
    x=monthly_views["month"], y=monthly_views["total_views"],
    name="Monthly Total Views", marker_color="#42A5F5", opacity=0.7,
))
fig_views.add_trace(go.Scatter(
    x=monthly_views["month"], y=monthly_views["rolling_avg"],
    name="3-Month Rolling Avg", mode="lines",
    line=dict(color="#F44336", width=3),
))

for date_str, event in MILESTONES.items():
    m_date = pd.Timestamp(date_str)
    if monthly_views["month"].min() <= m_date <= monthly_views["month"].max():
        fig_views.add_vline(x=m_date, line_dash="dot", line_color="gray", opacity=0.4)
        fig_views.add_annotation(
            x=m_date, y=monthly_views["total_views"].max() * 0.95,
            text=event, showarrow=False, textangle=-90,
            font=dict(size=8, color="gray"),
        )

fig_views.update_layout(
    title="Total Views per Month (all videos) with Milestones",
    template="plotly_white", height=450,
    yaxis_title="Total Views", xaxis_title="Month",
    hovermode="x unified", barmode="overlay",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
st.plotly_chart(fig_views, use_container_width=True)

# Key milestones — compact
milestones_df = pd.DataFrame([
    {"date": pd.Timestamp(d), "event": e} for d, e in MILESTONES.items()
]).sort_values("date")

milestone_lines = " | ".join(
    f"**{row['date'].strftime('%b %Y')}:** {row['event']}"
    for _, row in milestones_df.iterrows()
)
st.caption(milestone_lines)

st.markdown("---")

# Average views per video per month — dual y-axis episodes vs clips
df_monthly_type = df.copy()
df_monthly_type["month"] = df_monthly_type["published_at"].dt.to_period("M").dt.to_timestamp()
df_monthly_type["type"] = df_monthly_type["is_clips"].map({False: "Episodes", True: "Clips"})

monthly_by_type = df_monthly_type.groupby(["month", "type"]).agg(
    avg_views=("view_count", "mean"),
).reset_index()

episodes_monthly = monthly_by_type[monthly_by_type["type"] == "Episodes"]
clips_monthly = monthly_by_type[(monthly_by_type["type"] == "Clips") & (monthly_by_type["month"] >= "2025-07-01")]

fig_avg = go.Figure()
fig_avg.add_trace(go.Scatter(
    x=episodes_monthly["month"], y=episodes_monthly["avg_views"],
    mode="lines+markers", name="Episodes",
    line=dict(color="#42A5F5", width=2), marker=dict(size=5),
    yaxis="y",
))
fig_avg.add_trace(go.Scatter(
    x=clips_monthly["month"], y=clips_monthly["avg_views"],
    mode="lines+markers", name="Clips",
    line=dict(color="#FF7043", width=2), marker=dict(size=5),
    yaxis="y2",
))

fig_avg.add_vline(x=pd.Timestamp("2025-07-05"), line_dash="dash", line_color="red", opacity=0.5)
fig_avg.add_annotation(
    x=pd.Timestamp("2025-07-05"),
    y=episodes_monthly["avg_views"].max() * 0.9 if not episodes_monthly.empty else 0,
    text="Clips introduced", showarrow=False, font=dict(color="red", size=10),
)

fig_avg.update_layout(
    title="Average Views per Video by Month (Episodes vs Clips)",
    template="plotly_white", height=400, hovermode="x unified",
    xaxis=dict(title="Month"),
    yaxis=dict(title=dict(text="Avg Views (Episodes)", font=dict(color="#42A5F5")),
               tickfont=dict(color="#42A5F5")),
    yaxis2=dict(title=dict(text="Avg Views (Clips)", font=dict(color="#FF7043")),
                tickfont=dict(color="#FF7043"), overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
st.plotly_chart(fig_avg, use_container_width=True)

st.markdown("---")

# ==================================================================
# MONTHLY PUBLISHING: LONG VIDEOS vs CLIPS
# ==================================================================
st.header("Monthly Publishing: Long Videos vs Clips")

df_pub = df.copy()
df_pub["month_key"] = df_pub["published_at"].dt.to_period("M").dt.to_timestamp()
monthly_long = df_pub[~df_pub["is_clips"]].groupby("month_key").size().reset_index(name="long_videos")
monthly_clip = df_pub[df_pub["is_clips"] & (df_pub["month_key"] >= "2025-07-01")].groupby("month_key").size().reset_index(name="clip_videos")
monthly_both = monthly_long.merge(monthly_clip, on="month_key", how="outer").sort_values("month_key")

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
    template="plotly_white", height=400, hovermode="x unified",
    xaxis=dict(title="Month"),
    yaxis=dict(title=dict(text="Long Videos", font=dict(color="#42A5F5")), tickfont=dict(color="#42A5F5")),
    yaxis2=dict(title=dict(text="Clips", font=dict(color="#FF7043")), tickfont=dict(color="#FF7043"),
                overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
st.plotly_chart(fig_dual, use_container_width=True)

st.markdown("---")

# ==================================================================
# VIDEOS PUBLISHED PER MONTH — HEATMAPS
# ==================================================================
st.header("Videos Published per Month (Episodes + Clips)")

month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def make_pivot(source_df):
    hm = source_df.copy()
    hm["year"] = hm["published_at"].dt.year
    hm["month_num"] = hm["published_at"].dt.month
    pivot = hm.groupby(["year", "month_num"]).size().reset_index(name="count")
    pivot_table = pivot.pivot(index="year", columns="month_num", values="count").fillna(0)
    pivot_table.columns = [month_names[m - 1] for m in pivot_table.columns]
    return pivot_table


pivot_all = make_pivot(df)
pivot_episodes = make_pivot(df_episodes)

shared_max = max(pivot_all.values.max(), pivot_episodes.values.max())


def make_heatmap(pivot_table, title, zmax):
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns.tolist(),
        y=[str(y) for y in pivot_table.index.tolist()],
        colorscale="YlOrRd",
        zmin=0, zmax=zmax,
        text=pivot_table.values.astype(int),
        texttemplate="%{text}",
        hoverongaps=False,
    ))
    fig.update_layout(title=title, height=350, template="plotly_white")
    return fig


st.plotly_chart(make_heatmap(pivot_all, "All Videos (Episodes + Clips) Published per Month", shared_max), use_container_width=True)

st.markdown("---")

st.header("Videos Published per Month (Episodes Only)")

st.plotly_chart(make_heatmap(pivot_episodes, "Episodes Only (No Clips) Published per Month", shared_max), use_container_width=True)

st.markdown("---")
st.caption("Data snapshot collected via YouTube Data API v3 on April 8, 2026. Dashboard built with Streamlit.")
