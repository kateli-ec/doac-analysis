"""Clip Analysis — impact of short clips on episode performance."""

import os

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy.stats import mannwhitneyu

from components.metrics import format_number

st.set_page_config(page_title="Clip Analysis", layout="wide")
st.title("Clip Analysis")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

st.markdown("""
Since mid-2025, The Diary of a CEO has experienced a sharp acceleration in both subscriber
growth and viewership
(see [live SocialBlade dashboard](https://socialblade.com/youtube/handle/thediaryofaceo)).
This inflection point aligns with a notable shift in content strategy: on **July 5, 2025**,
the channel published its first short-form clip — a sub-3-minute vertical video designed to
tease full-length interviews. Since then, clips have become a consistent part of the
publishing cadence, averaging roughly 3 clips per full episode.

The natural question is whether these clips are *driving* the channel's growth or simply
*coinciding* with it. This analysis compares episode performance before and after the
introduction of clips, examines whether episodes paired with clips outperform those
without, and quantifies the additional reach that clips generate.
""")

st.caption(
    "Methodology: Clips are matched to their parent episode by identifying the guest's name "
    "in the clip description and linking it to the corresponding full-length interview. "
    "This yields an 81% match rate with a 0% false positive rate on verified pairs."
)

# ---- Load data ----
all_longs_path = os.path.join(DATA_DIR, "all_long_videos.parquet")
if not os.path.exists(all_longs_path):
    st.error("Long video data not found.")
    st.stop()

all_longs = pd.read_parquet(all_longs_path)
all_longs["published_at"] = pd.to_datetime(all_longs["published_date"])

CLIP_ERA_START = "2025-07-01"
PRE_CLIP_START = "2024-09-01"
PRE_CLIP_END = "2025-06-30"

_clip_era = all_longs[all_longs["published_date"] >= CLIP_ERA_START]
_pre_clip = all_longs[
    (all_longs["published_date"] >= PRE_CLIP_START)
    & (all_longs["published_date"] <= PRE_CLIP_END)
]
_clip_with = _clip_era[_clip_era["matched_clip_count"] > 0]

_avg_pre = _pre_clip["view_count"].mean()
_avg_clip = _clip_era["view_count"].mean()
_clip_add_pct = _clip_with["clip_total_views"].mean() / _clip_with["view_count"].mean() * 100 if len(_clip_with) > 0 else 0

# ============================================================
# THE ANSWER
# ============================================================
st.markdown("---")
st.subheader("Do videos with clips get more views?")

st.markdown(f"""
**No — clips do not directly increase episode views, but they significantly expand total reach.**

Comparing two matched 10-month windows (86 episodes pre-clip vs 80 episodes in the clip era):

| Metric | Pre-Clip (Sep 2024 — Jun 2025) | Clip Era (Jul 2025 — Apr 2026) |
|--------|:------------------------------:|:------------------------------:|
| Avg episode views | {format_number(_avg_pre)} | {format_number(_avg_clip)} |
| Median episode views | {format_number(_pre_clip["view_count"].median())} | {format_number(_clip_era["view_count"].median())} |

Episode views are **virtually identical** between the two periods (p = 0.90, not significant).
Introducing clips did not cause episodes themselves to get more views.

**However, clips add {_clip_add_pct:.0f}% extra reach on top of the episode.** For the 75 episodes with
matched clips, the average combined reach (episode + clips) is **{format_number(_clip_with["combined_views"].mean())}**
vs **{format_number(_clip_with["view_count"].mean())}** for the episode alone.

**Key takeaway:** Clips serve as a **reach multiplier**, not a view driver. They don't funnel viewers
to the full episode — instead, they act as standalone content that exposes the brand and guest to
audiences who may never watch a 2-hour interview. The clips strategy is about **audience acquisition
and brand awareness**, not boosting individual episode metrics.
""")

st.markdown("---")

# Redefine for sections below
clip_era = _clip_era
pre_clip = _pre_clip
clip_with = _clip_with
clip_without = clip_era[clip_era["matched_clip_count"] == 0]

# ============================================================
# Section 1: Clip Era vs Pre-Clip Era
# ============================================================
st.subheader("Clip Era vs Pre-Clip Era (matched 10-month windows)")
st.markdown(
    f"Comparing two equal-length periods:  \n"
    f"- **Pre-Clip:** Sep 2024 — Jun 2025 ({len(pre_clip)} episodes, no clips published)  \n"
    f"- **Clip Era:** Jul 2025 — Apr 2026 ({len(clip_era)} episodes, clips published alongside)"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pre-Clip Episodes", len(pre_clip))
col2.metric("Clip-Era Episodes", len(clip_era))
col3.metric("Avg Views (Pre-Clip)", format_number(pre_clip["view_count"].mean()))
pct_change = (clip_era["view_count"].mean() / pre_clip["view_count"].mean() - 1) * 100 if pre_clip["view_count"].mean() > 0 else 0
col4.metric("Avg Views (Clip Era)", format_number(clip_era["view_count"].mean()),
            delta=f"+{pct_change:.0f}%")

col1, col2 = st.columns(2)
with col1:
    comp = pd.DataFrame({
        "Period": ["Pre-Clip\n(Sep 2024 — Jun 2025)", "Clip Era\n(Jul 2025 — Apr 2026)"],
        "Avg Views": [pre_clip["view_count"].mean(), clip_era["view_count"].mean()],
    })
    fig = px.bar(comp, x="Period", y="Avg Views", title="Average Episode Views",
                 template="plotly_white", text_auto=",.0f",
                 color="Period", color_discrete_sequence=["#BDBDBD", "#42A5F5"])
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    comp_med = pd.DataFrame({
        "Period": ["Pre-Clip\n(Sep 2024 — Jun 2025)", "Clip Era\n(Jul 2025 — Apr 2026)"],
        "Median Views": [pre_clip["view_count"].median(), clip_era["view_count"].median()],
    })
    fig = px.bar(comp_med, x="Period", y="Median Views", title="Median Episode Views",
                 template="plotly_white", text_auto=",.0f",
                 color="Period", color_discrete_sequence=["#BDBDBD", "#42A5F5"])
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

if len(pre_clip) >= 5 and len(clip_era) >= 5:
    stat, p_val = mannwhitneyu(clip_era["view_count"], pre_clip["view_count"], alternative="two-sided")
    st.markdown(
        f"**Mann-Whitney U test:** p = {p_val:.6f} "
        f"({'Statistically significant' if p_val < 0.05 else 'Not significant'} at 0.05)"
    )

st.caption(
    "Note: Pre-clip era videos have had ~10 months more time to accumulate views. "
    "Despite this bias against the clip era, clip-era episodes still show higher view counts."
)

st.markdown("---")

# ============================================================
# Section 2: Views per Day
# ============================================================
st.subheader("Views per Day — Episode Only, No Clips")
st.markdown(
    "**Caution: this metric is inherently biased toward newer content.** "
    "Views/day = total views / days since publish. YouTube videos get most views in the first "
    "few weeks, so newer videos always have a higher views/day than older videos with the same "
    "total views — simply because the denominator is smaller."
)
st.markdown(
    "The large difference below is **primarily a recency artifact, not a clip effect.** "
    "The total views comparison in Section 1 (p = 0.90) is the more reliable measure."
)

col1, col2 = st.columns(2)
col1.metric("Avg Views/Day (Pre-Clip)", format_number(pre_clip["views_per_day"].mean()))
vpd_ratio = clip_era["views_per_day"].mean() / pre_clip["views_per_day"].mean() if pre_clip["views_per_day"].mean() > 0 else 0
col2.metric("Avg Views/Day (Clip Era)", format_number(clip_era["views_per_day"].mean()),
            delta=f"{vpd_ratio:.1f}x")

both = pd.concat([
    pre_clip.assign(period="Pre-Clip (Sep 2024 — Jun 2025)"),
    clip_era.assign(period="Clip Era (Jul 2025 — Apr 2026)"),
])
fig = px.box(both, x="period", y="views_per_day",
             title="Views per Day Distribution (biased by recency — see caveat above)",
             template="plotly_white", color="period",
             color_discrete_sequence=["#BDBDBD", "#42A5F5"])
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# Section 3: Monthly trend
# ============================================================
st.subheader("Monthly View Trend Across Both Periods — Episode Only, No Clips")

both_monthly = both.copy()
both_monthly["month"] = both_monthly["published_at"].dt.to_period("M").dt.to_timestamp()
monthly_agg = both_monthly.groupby(["month", "period"]).agg(
    avg_views=("view_count", "mean"),
    episode_count=("video_id", "count"),
).reset_index()

fig = px.line(monthly_agg, x="month", y="avg_views", color="period",
              title="Average Episode Views by Month (episode only, no clips)",
              template="plotly_white", markers=True,
              color_discrete_sequence=["#BDBDBD", "#42A5F5"])
fig.add_vline(x=pd.Timestamp("2025-07-01"), line_dash="dash", line_color="red", opacity=0.5)
fig.add_annotation(x=pd.Timestamp("2025-07-01"), y=monthly_agg["avg_views"].max() * 0.95,
                   text="Clips introduced", showarrow=False, font=dict(color="red", size=11))
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# Section 4: Within Clip Era
# ============================================================
st.subheader("Within Clip Era: Episodes With vs Without Matched Clips")

col1, col2, col3 = st.columns(3)
col1.metric("With Clips", f"{len(clip_with)} episodes")
col2.metric("Without Clips", f"{len(clip_without)} episodes")
if len(clip_with) > 0 and len(clip_without) > 0:
    r = clip_with["view_count"].mean() / clip_without["view_count"].mean()
    col3.metric("Episode View Ratio", f"{r:.2f}x")

st.markdown("##### Episode Views Only (excluding clip views)")
st.caption("Comparing the long-form episode view counts — clips are not included here.")

if len(clip_with) >= 5 and len(clip_without) >= 5:
    col1, col2 = st.columns(2)
    with col1:
        cmp = pd.DataFrame({
            "Group": ["With Clips", "Without Clips"],
            "Avg Episode Views": [clip_with["view_count"].mean(), clip_without["view_count"].mean()],
        })
        fig = px.bar(cmp, x="Group", y="Avg Episode Views",
                     title="Avg Episode Views (episode only)",
                     template="plotly_white", text_auto=",.0f",
                     color="Group", color_discrete_map={"With Clips": "#42A5F5", "Without Clips": "#BDBDBD"})
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cmp_med = pd.DataFrame({
            "Group": ["With Clips", "Without Clips"],
            "Median Episode Views": [clip_with["view_count"].median(), clip_without["view_count"].median()],
        })
        fig = px.bar(cmp_med, x="Group", y="Median Episode Views",
                     title="Median Episode Views (episode only)",
                     template="plotly_white", text_auto=",.0f",
                     color="Group", color_discrete_map={"With Clips": "#42A5F5", "Without Clips": "#BDBDBD"})
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    s3, p3 = mannwhitneyu(clip_with["view_count"], clip_without["view_count"], alternative="two-sided")
    st.markdown(
        f"**Mann-Whitney U test (episode only):** p = {p3:.4f} "
        f"({'Statistically significant' if p3 < 0.05 else 'Not significant'} at 0.05)"
    )

    st.markdown("##### Total Reach: Episode + Clip Views Combined")
    st.caption("Adding clip views on top of episode views for episodes that have clips.")

    col1, col2 = st.columns(2)
    with col1:
        cmp2 = pd.DataFrame({
            "Group": ["With Clips (episode + clips)", "Without Clips (episode only)"],
            "Avg Total Views": [clip_with["combined_views"].mean(), clip_without["view_count"].mean()],
        })
        fig = px.bar(cmp2, x="Group", y="Avg Total Views",
                     title="Avg Total Reach (episode + clips vs episode only)",
                     template="plotly_white", text_auto=",.0f",
                     color="Group", color_discrete_map={
                         "With Clips (episode + clips)": "#42A5F5",
                         "Without Clips (episode only)": "#BDBDBD"})
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cmp2_med = pd.DataFrame({
            "Group": ["With Clips (episode + clips)", "Without Clips (episode only)"],
            "Median Total Views": [
                (clip_with["view_count"] + clip_with["clip_total_views"]).median(),
                clip_without["view_count"].median(),
            ],
        })
        fig = px.bar(cmp2_med, x="Group", y="Median Total Views",
                     title="Median Total Reach (episode + clips vs episode only)",
                     template="plotly_white", text_auto=",.0f",
                     color="Group", color_discrete_map={
                         "With Clips (episode + clips)": "#42A5F5",
                         "Without Clips (episode only)": "#BDBDBD"})
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    s4, p4 = mannwhitneyu(clip_with["combined_views"], clip_without["view_count"], alternative="two-sided")
    st.markdown(
        f"**Mann-Whitney U test (combined reach):** p = {p4:.4f} "
        f"({'Statistically significant' if p4 < 0.05 else 'Not significant'} at 0.05)"
    )

else:
    st.info(
        f"Only {len(clip_without)} episodes without matched clips in the clip era — "
        "too few for robust statistical comparison within this period."
    )

st.markdown("---")

# ============================================================
# Section 5: Combined Reach
# ============================================================
st.subheader("Combined Reach: Episode + Clips")

if len(clip_with) > 0:
    reach = clip_with.copy()
    reach["combined_views"] = reach["view_count"] + reach["clip_total_views"]
    clip_pct = reach["clip_total_views"].mean() / reach["view_count"].mean() * 100

    st.markdown(
        f"For episodes with matched clips, clips add **{clip_pct:.0f}% extra views** "
        f"on top of the episode, bringing average combined reach to "
        f"**{format_number(reach['combined_views'].mean())}**."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Episode Views", format_number(reach["view_count"].mean()))
    col2.metric("Avg Clip Views Added", format_number(reach["clip_total_views"].mean()))
    col3.metric("Avg Combined Reach", format_number(reach["combined_views"].mean()))

    fig = px.scatter(
        reach, x="view_count", y="clip_total_views",
        hover_data=["title", "matched_clip_count"],
        title="Episode Views vs Total Clip Views",
        labels={"view_count": "Episode Views", "clip_total_views": "Total Clip Views"},
        template="plotly_white", height=400,
        trendline="ols", color_discrete_sequence=["#42A5F5"],
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# Section 6: Full data table
# ============================================================
st.subheader("Episode-Clip Matching Table (Jul 2025+)")
display = clip_era[["title", "guest", "published_date", "view_count",
                     "matched_clip_count", "clip_total_views", "combined_views"]].copy()
display.columns = ["Title", "Guest", "Published", "Episode Views",
                    "Clip Count", "Clip Total Views", "Combined Views"]
st.dataframe(display.sort_values("Published", ascending=False),
             use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Data snapshot collected via YouTube Data API v3. Dashboard built with Streamlit.")
