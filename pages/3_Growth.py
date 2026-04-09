"""Growth Analysis. Era deep dive, inflection points, viral videos."""

import os

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from components.metrics import metric_row, format_number, format_duration

ERAS = {
    "Pre-Growth": ("2020-10-01", "2021-12-31"),
    "Early Growth": ("2022-01-01", "2023-01-31"),
    "Breakout": ("2023-02-01", "2023-12-31"),
    "Established": ("2024-01-01", "2025-06-30"),
    "Clip Era": ("2025-07-01", "2026-03-31"),
}

ERA_DESCRIPTIONS = {
    "Pre-Growth": "Channel launch on YouTube. Small audience, experimenting with format. ~523K avg views/episode.",
    "Early Growth": "Dragons\' Den debut (Jan 2022) drove a 2x lift. Posting cadence increased to ~8 episodes/month. ~1.1M avg views.",
    "Breakout": "Viral growth starting Feb 2023. Book launch Aug 2023. Average views 3x\'d to ~3.3M. Fastest-growing podcast in the world on YouTube.",
    "Established": "Sustained high performance. Samsung TV deal, 1B total streams, 10M YouTube subscribers. ~3.4M avg views.",
    "Clip Era": "Short-form clip strategy introduced Jul 2025. Episode views stable at ~3.3M. Clips add ~22% additional reach.",
}

MILESTONES = {}

st.set_page_config(page_title="Growth Analysis", layout="wide")
st.title("Growth Analysis")

st.markdown("""
The Diary of a CEO grew **6.5x** (523K to 3.4M avg views/episode) through two inflection points:

1. **Dragons' Den debut (Jan 2022):** BBC primetime exposure doubled views from 523K to 1.1M.
   Posting cadence also doubled from ~4 to ~8 episodes/month in this era.
2. **Broad viral breakout (Feb 2023):** Views tripled from 1.1M to 3.3M. This was a lift across
   all episodes, coinciding with crossing 1M YouTube subscribers in January 2023, which likely
   triggered stronger algorithmic recommendation. Since then, views have held steady at ~3.3M for
   over two years.

**Key growth drivers based on the data:**

- **Audience expansion events triggered the step changes.** The first inflection point came from
  Dragons' Den, which brought BBC TV audiences to the channel. The second came from crossing 1M
  YouTube subscribers, which likely unlocked stronger algorithmic recommendation within YouTube's
  own discovery system. Both events expanded the pool of people who saw the content.
- **Doubling posting cadence contributed to the first growth jump.** The channel went from ~4 to ~8
  episodes/month at the start of Early Growth, increasing total reach even before per-episode views rose.
- **Consistency, not virality, sustains the baseline.** ~10% of episodes go viral in every era, a
  constant rate. Viral episodes accounted for 32% of views early on, but only 14% in the most recent
  era. Growth came from lifting the floor across all episodes.
- **Guest, topic, and title determine performance.** Description length and formatting show no
  meaningful correlation with views within any era. What separates high-performing episodes is the
  content itself:
    - *Health and science topics are the strongest viral drivers.* Words like "doctor," "brain,"
      "cancer," and "expert" appear disproportionately in viral titles.
    - *Title formatting (ALL CAPS, clickbait phrasing) is uncorrelated with virality.* These patterns
      actually appear less in viral episodes than in non-viral ones.
""")

st.caption(
    "Methodology: Eras defined by changepoint analysis on monthly avg views/episode, "
    "aligned to real milestones. Viral = >2 standard deviations above era mean. Episodes only, no clips."
)


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

@st.cache_data
def load_videos():
    return pd.read_parquet(os.path.join(DATA_DIR, "videos.parquet"))

df = load_videos()
df_episodes = df[~df["is_clips"]]

ERA_ORDER = ["Pre-Growth", "Early Growth", "Breakout", "Established", "Clip Era"]
ERA_COLORS = {
    "Pre-Growth": "#BDBDBD",
    "Early Growth": "#90CAF9",
    "Breakout": "#42A5F5",
    "Established": "#1E88E5",
    "Clip Era": "#FF7043",
}

# ==================================================================
# SECTION 1: Channel Eras (chart + table)
# ==================================================================
st.header("Channel Eras")
st.markdown(
    "Eras are defined by **data-driven changepoint analysis** on monthly average views per episode, "
    "then aligned to the nearest real-world milestone. The chart below shows the inflection points clearly. "
    "the two major jumps were Dragons' Den debut (Jan 2022, **2x** lift) and the viral breakout (Feb 2023, **3x** lift)."
)

# Build monthly data
df_ep_monthly = df_episodes.copy()
df_ep_monthly["month"] = df_ep_monthly["published_at"].dt.to_period("M").dt.to_timestamp()

monthly_era = df_ep_monthly.groupby(["month", "era"]).agg(
    avg_views=("view_count", "mean"),
    count=("video_id", "count"),
).reset_index()
monthly_era["era"] = pd.Categorical(monthly_era["era"], categories=ERA_ORDER, ordered=True)

# Compute era averages for horizontal reference lines
era_avgs = {}
for era_name in ERA_ORDER:
    era_eps = df_episodes[df_episodes["era"] == era_name]
    if not era_eps.empty:
        era_avgs[era_name] = era_eps["view_count"].mean()

# Chart: monthly avg views bars colored by era + horizontal era average lines
fig_era = go.Figure()

# Add bars per era
for era_name in ERA_ORDER:
    era_monthly = monthly_era[monthly_era["era"] == era_name]
    if era_monthly.empty:
        continue
    fig_era.add_trace(go.Bar(
        x=era_monthly["month"], y=era_monthly["avg_views"],
        name=era_name, marker_color=ERA_COLORS[era_name], opacity=0.8,
        hovertemplate="%{x|%b %Y}<br>Avg views: %{y:,.0f}<extra>" + era_name + "</extra>",
    ))

# Add horizontal lines for era averages
for era_name in ERA_ORDER:
    if era_name not in era_avgs:
        continue
    start = pd.Timestamp(ERAS[era_name][0])
    end = pd.Timestamp(ERAS[era_name][1])
    avg = era_avgs[era_name]
    fig_era.add_shape(
        type="line", x0=start, x1=end, y0=avg, y1=avg,
        line=dict(color=ERA_COLORS[era_name], width=3, dash="dot"),
    )
    # Label the era average
    mid = start + (end - start) / 2
    fig_era.add_annotation(
        x=mid, y=avg, text=f"{era_name}: {format_number(avg)} avg",
        showarrow=False, yshift=15,
        font=dict(size=10, color=ERA_COLORS[era_name], family="Arial Black"),
    )

fig_era.update_layout(
    title="Average Views per Episode by Month: Era Inflection Points",
    template="plotly_white", height=500, barmode="stack",
    yaxis_title="Avg Views/Episode", xaxis_title="Month",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
st.plotly_chart(fig_era, use_container_width=True)

st.caption(
    "Bars = monthly avg views per episode (colored by era). "
    "Dotted lines = era average. The step changes between eras are the inflection points."
)

# Era summary table
st.caption("Episodes only. Clips are excluded from all metrics below.")

era_data = []
for era_name in ERA_ORDER:
    start, end = ERAS[era_name]
    era_eps = df_episodes[df_episodes["era"] == era_name]
    if era_eps.empty:
        continue

    start_dt = pd.Timestamp(start)
    end_dt = pd.Timestamp(end)
    months = max(1, round((end_dt - start_dt).days / 30.44))

    prev_avg = None
    idx = ERA_ORDER.index(era_name)
    if idx > 0:
        prev_era = ERA_ORDER[idx - 1]
        prev_eps = df_episodes[df_episodes["era"] == prev_era]
        if not prev_eps.empty:
            prev_avg = prev_eps["view_count"].mean()

    multiplier = f"{era_eps['view_count'].mean() / prev_avg:.1f}x" if prev_avg else "—"

    growth_drivers = {
        "Pre-Growth": "Channel launched on YouTube (Oct 2020)<br>Experimenting with format and guests<br>Small but growing audience",
        "Early Growth": "Dragons' Den debut (Jan 2022), BBC primetime exposure<br>Posting cadence doubled (~4 to ~8 eps/month)<br>Views 2x'd from prior era",
        "Breakout": "1M YouTube subscribers (Jan 2023)<br>Viral month Mar 2023 (avg 4.8M views/ep)<br>Book launch Aug 2023 (#1 Sunday Times bestseller)<br>Stronger algorithmic recommendation + guest caliber step-up",
        "Established": "Samsung TV deal (May 2024), first podcast on Samsung TV Plus<br>1B total streams (Nov 2024), first UK podcast<br>Channel at sustainable ~3.3M ceiling",
        "Clip Era": "First clip published (Jul 2025)<br>TIME100 Creators list (Jul 2025)<br>Episode views stable; clips add ~22% incremental reach<br>10M YouTube subscribers (Jun 2025)",
    }

    era_data.append({
        "Era": era_name,
        "Period": f"{start[:7]} to {end[:7]}",
        "Duration (months)": months,
        "Total Episodes": len(era_eps),
        "Avg Episodes/Month": round(len(era_eps) / months, 1),
        "Avg Views": format_number(era_eps["view_count"].mean()),
        "Growth vs Prior": multiplier,
        "What Drove This Era": growth_drivers.get(era_name, ""),
    })

era_table = pd.DataFrame(era_data)

st.markdown(
    era_table.to_html(index=False, escape=False, classes="era-table"),
    unsafe_allow_html=True,
)
st.markdown(
    """<style>
    .era-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .era-table th { background: #f5f5f5; padding: 8px; text-align: left; border-bottom: 2px solid #ddd; }
    .era-table td { padding: 8px; border-bottom: 1px solid #eee; vertical-align: top; white-space: normal; word-wrap: break-word; }
    </style>""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ==================================================================
# SECTION 3: Detailed Era Comparison (table first)
# ==================================================================
st.header("Detailed Era Comparison")
st.caption("Episodes only. Clips excluded. All metrics computed per era.")

detail_rows_raw = []
for era_name in ERA_ORDER:
    era_eps = df_episodes[df_episodes["era"] == era_name]
    if era_eps.empty:
        continue

    start_dt = pd.Timestamp(ERAS[era_name][0])
    end_dt = pd.Timestamp(ERAS[era_name][1])
    months = max(1, round((end_dt - start_dt).days / 30.44))

    detail_rows_raw.append({
        "Era": era_name,
        "Episodes": len(era_eps),
        "Avg Views": era_eps["view_count"].mean(),
        "Median Views": era_eps["view_count"].median(),
        "Max Views": era_eps["view_count"].max(),
        "Min Views": era_eps["view_count"].min(),
        "Total Views": era_eps["view_count"].sum(),
        "Avg Likes": era_eps["like_count"].mean(),
        "Avg Comments": era_eps["comment_count"].mean(),
        "Avg Engagement %": era_eps["engagement_rate"].mean() * 100,
        "Avg Duration (min)": era_eps["duration_seconds"].mean() / 60,
        "Avg Eps/Month": len(era_eps) / months,
        "Views Std Dev": era_eps["view_count"].std(),
        "Top 10% Threshold": era_eps["view_count"].quantile(0.9),
    })

detail_raw = pd.DataFrame(detail_rows_raw)

# Build HTML with inline color bars for numeric columns
bar_color = "#42A5F5"
bar_cols = ["Avg Views", "Median Views", "Max Views", "Total Views",
            "Avg Likes", "Avg Comments", "Avg Engagement %",
            "Avg Duration (min)", "Avg Eps/Month", "Top 10% Threshold"]


def make_bar_cell(val, col_max, fmt_str):
    """Render a table cell with a background bar proportional to val/col_max."""
    pct = val / col_max * 100 if col_max > 0 else 0
    return (
        f'<td style="position:relative; padding:6px 8px;">'
        f'<div style="position:absolute; left:0; top:0; bottom:0; width:{pct:.0f}%; '
        f'background:rgba(66,165,245,0.15); z-index:0;"></div>'
        f'<span style="position:relative; z-index:1;">{fmt_str}</span></td>'
    )


# Build HTML table manually
html = '<table class="detail-table"><thead><tr>'
for col in detail_raw.columns:
    html += f"<th>{col}</th>"
html += "</tr></thead><tbody>"

col_maxes = {col: detail_raw[col].max() for col in bar_cols}

for _, row in detail_raw.iterrows():
    html += "<tr>"
    for col in detail_raw.columns:
        val = row[col]
        if col == "Era":
            html += f'<td style="padding:6px 8px; font-weight:bold;">{val}</td>'
        elif col in bar_cols:
            if col == "Avg Engagement %":
                fmt = f"{val:.2f}%"
            elif col == "Avg Duration (min)":
                fmt = f"{val:.0f}m"
            elif col == "Avg Eps/Month":
                fmt = f"{val:.1f}"
            elif val >= 1_000_000:
                fmt = f"{val:,.0f}"
            else:
                fmt = f"{val:,.0f}"
            html += make_bar_cell(val, col_maxes[col], fmt)
        else:
            fmt = f"{val:,.0f}" if isinstance(val, (int, float)) else str(val)
            html += f'<td style="padding:6px 8px;">{fmt}</td>'
    html += "</tr>"
html += "</tbody></table>"

st.markdown(html, unsafe_allow_html=True)
st.markdown(
    """<style>
    .detail-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .detail-table th { background: #f5f5f5; padding: 6px 8px; text-align: left; border-bottom: 2px solid #ddd; white-space: nowrap; }
    .detail-table td { border-bottom: 1px solid #eee; vertical-align: top; white-space: nowrap; }
    </style>""",
    unsafe_allow_html=True,
)

# View distribution box plot
df_ep_known = df_episodes[df_episodes["era"].isin(ERA_ORDER)]
df_ep_known["era"] = pd.Categorical(df_ep_known["era"], categories=ERA_ORDER, ordered=True)

fig_box = px.box(
    df_ep_known, x="era", y="view_count", color="era",
    title="View Count Distribution by Era (episodes only)",
    template="plotly_white", height=450,
    color_discrete_map=ERA_COLORS,
    category_orders={"era": ERA_ORDER},
)
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# ==================================================================
# SECTION 4: Viral Videos by Era
# ==================================================================
st.header("Viral Videos by Era")
st.caption("Videos that exceeded 2 standard deviations above their era's mean. Detected separately for views and engagement rate.")

df_viral = df_episodes.copy()

# Views-based viral detection
era_view_agg = df_viral.groupby("era")["view_count"].agg(["mean", "std"]).reset_index()
era_view_agg.columns = ["era", "era_view_mean", "era_view_std"]
df_viral = df_viral.merge(era_view_agg, on="era")
df_viral["view_z"] = (df_viral["view_count"] - df_viral["era_view_mean"]) / df_viral["era_view_std"].clip(lower=1)
df_viral["viral_views"] = df_viral["view_z"] > 2.0

# Engagement-based viral detection
era_eng_agg = df_viral.groupby("era")["engagement_rate"].agg(["mean", "std"]).reset_index()
era_eng_agg.columns = ["era", "era_eng_mean", "era_eng_std"]
df_viral = df_viral.merge(era_eng_agg, on="era")
df_viral["eng_z"] = (df_viral["engagement_rate"] - df_viral["era_eng_mean"]) / df_viral["era_eng_std"].clip(lower=0.0001)
df_viral["viral_engagement"] = df_viral["eng_z"] > 2.0

df_viral["is_viral_any"] = df_viral["viral_views"] | df_viral["viral_engagement"]


def add_era_boundaries(fig, y_max):
    """Add era boundary lines + labels to a figure."""
    for era_name in ERA_ORDER:
        start = pd.Timestamp(ERAS[era_name][0], tz="UTC")
        end = pd.Timestamp(ERAS[era_name][1], tz="UTC")
        fig.add_vline(x=start, line_dash="dash", line_color="gray", opacity=0.4)
        mid = start + (end - start) / 2
        fig.add_annotation(
            x=mid, y=y_max * 1.05,
            text=f"<b>{era_name}</b>", showarrow=False,
            font=dict(size=11, color=ERA_COLORS[era_name]),
        )


# --- Chart 1: Views-based viral detection ---
fig_v = go.Figure()
non_v = df_viral[~df_viral["viral_views"]]
vir_v = df_viral[df_viral["viral_views"]]

fig_v.add_trace(go.Scatter(
    x=non_v["published_at"], y=non_v["view_count"],
    mode="markers", name="Regular",
    marker=dict(size=6, color="#BDBDBD", opacity=0.5),
    hovertemplate="%{customdata[0]}<br>Views: %{y:,.0f}<extra>Regular</extra>",
    customdata=non_v[["title"]].values,
))
fig_v.add_trace(go.Scatter(
    x=vir_v["published_at"], y=vir_v["view_count"],
    mode="markers", name="Viral by Views (>2 std dev)",
    marker=dict(size=10, color="#F44336", symbol="diamond", opacity=0.9,
                line=dict(width=1, color="#B71C1C")),
    hovertemplate="%{customdata[0]}<br>Views: %{y:,.0f}<br>Z-score: %{customdata[1]:.1f}<extra>Viral</extra>",
    customdata=vir_v[["title", "view_z"]].values,
))
add_era_boundaries(fig_v, df_viral["view_count"].max())
fig_v.update_layout(
    title="Viral Detection by Views (>2 std dev above era mean)",
    template="plotly_white", height=450,
    yaxis_title="Views", xaxis_title="Date", hovermode="closest",
    legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
)
st.plotly_chart(fig_v, use_container_width=True)

# --- Chart 2: Engagement-based viral detection ---
fig_e = go.Figure()
non_e = df_viral[~df_viral["viral_engagement"]]
vir_e = df_viral[df_viral["viral_engagement"]]

fig_e.add_trace(go.Scatter(
    x=non_e["published_at"], y=non_e["engagement_rate"] * 100,
    mode="markers", name="Regular",
    marker=dict(size=6, color="#BDBDBD", opacity=0.5),
    hovertemplate="%{customdata[0]}<br>Engagement: %{y:.2f}%<extra>Regular</extra>",
    customdata=non_e[["title"]].values,
))
fig_e.add_trace(go.Scatter(
    x=vir_e["published_at"], y=vir_e["engagement_rate"] * 100,
    mode="markers", name="Viral by Engagement (>2 std dev)",
    marker=dict(size=10, color="#FF7043", symbol="diamond", opacity=0.9,
                line=dict(width=1, color="#BF360C")),
    hovertemplate="%{customdata[0]}<br>Engagement: %{y:.2f}%<br>Z-score: %{customdata[1]:.1f}<extra>Viral</extra>",
    customdata=vir_e[["title", "eng_z"]].values,
))
add_era_boundaries(fig_e, df_viral["engagement_rate"].max() * 100)
fig_e.update_layout(
    title="Viral Detection by Engagement Rate (>2 std dev above era mean)",
    template="plotly_white", height=450,
    yaxis_title="Engagement %", xaxis_title="Date", hovermode="closest",
    legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
)
st.plotly_chart(fig_e, use_container_width=True)

# --- Viral videos table (union of views-viral and engagement-viral) ---
viral_all = df_viral[df_viral["is_viral_any"]].sort_values("view_count", ascending=False).copy()
if not viral_all.empty:
    st.markdown(f"**{len(viral_all)} viral episodes detected** "
                f"({df_viral['viral_views'].sum()} by views, "
                f"{df_viral['viral_engagement'].sum()} by engagement, "
                f"{(df_viral['viral_views'] & df_viral['viral_engagement']).sum()} by both):")

    df_numbered = df_episodes.sort_values("published_at").reset_index(drop=True)
    df_numbered["episode_number"] = range(1, len(df_numbered) + 1)
    ep_num_map = dict(zip(df_numbered["video_id"], df_numbered["episode_number"]))

    viral_table = []
    for _, v in viral_all.iterrows():
        dur_s = v["duration_seconds"]
        h, rem = divmod(int(dur_s), 3600)
        m, s = divmod(rem, 60)

        if v["viral_views"] and v["viral_engagement"]:
            viral_type = "Both"
        elif v["viral_views"]:
            viral_type = "Views"
        else:
            viral_type = "Engagement"

        viral_table.append({
            "Ep #": ep_num_map.get(v["video_id"], ""),
            "Link": f"https://www.youtube.com/watch?v={v['video_id']}",
            "Title": v["title"][:70],
            "Viral By": viral_type,
            "Guest": v["guest_name"] if pd.notna(v.get("guest_name")) else "",
            "Published": v["published_at"].strftime("%Y-%m-%d"),
            "Duration": f"{h}h {m}m" if h else f"{m}m {s}s",
            "Era": v["era"],
            "Views": int(v["view_count"]),
            "Era Avg Views": int(v["era_view_mean"]),
            "View Std Dev Above Mean": round(v["view_z"], 1),
            "Likes": int(v["like_count"]),
            "Comments": int(v["comment_count"]),
            "Engagement %": round(v["engagement_rate"] * 100, 2),
            "Era Avg Engagement %": round(v["era_eng_mean"] * 100, 2),
            "Eng Std Dev Above Mean": round(v["eng_z"], 1),
        })

    viral_df_display = pd.DataFrame(viral_table)
    st.dataframe(
        viral_df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Watch"),
            "Views": st.column_config.NumberColumn(format="%,d"),
            "Era Avg Views": st.column_config.NumberColumn(format="%,d"),
            "Likes": st.column_config.NumberColumn(format="%,d"),
            "Comments": st.column_config.NumberColumn(format="%,d"),
            "Engagement %": st.column_config.NumberColumn(format="%.2f%%"),
            "Era Avg Engagement %": st.column_config.NumberColumn(format="%.2f%%"),
            "View Std Dev Above Mean": st.column_config.NumberColumn(format="%.1fx"),
            "Eng Std Dev Above Mean": st.column_config.NumberColumn(format="%.1fx"),
        },
    )

    # ==============================================================
    # Viral video analysis
    # ==============================================================
    st.markdown("---")
    st.subheader("What Do Viral Videos Have in Common?")

    import re
    from collections import Counter

    viral_eps = viral_all.copy()
    non_viral_eps = df_viral[~df_viral["is_viral_any"]].copy()

    # Duration comparison
    v_dur = viral_eps["duration_seconds"].mean() / 60
    nv_dur = non_viral_eps["duration_seconds"].mean() / 60

    # Title patterns
    patterns = {
        "Contains 'Doctor/Dr'": r"(?i)\bdr\b|doctor",
        "Contains 'Expert'": r"(?i)expert",
        "Contains 'Neuroscientist'": r"(?i)neuroscientist",
        "Health/science topic": r"(?i)brain|cancer|diet|vitamin|health|sleep|hormone|aging|gut|exercise|fasting",
        "Politics/geopolitics": r"(?i)america|war|iran|trump|president|cia|government",
        "Celebrity guest": r"(?i)obama|harris|peterson|robbins|mcconaughey|klopp|hart",
        "Contains ALL CAPS word": r"\b[A-Z]{3,}\b",
    }

    pattern_rows = []
    for name, pat in patterns.items():
        v_pct = viral_eps["title"].str.contains(pat, regex=True, na=False).mean() * 100
        nv_pct = non_viral_eps["title"].str.contains(pat, regex=True, na=False).mean() * 100
        pattern_rows.append({"Pattern": name, "Viral %": f"{v_pct:.0f}%", "Non-Viral %": f"{nv_pct:.0f}%", "Difference": f"{v_pct - nv_pct:+.0f}pp"})

    # Top words
    stop = {'the','a','an','is','are','was','in','on','at','to','for','of','and','or','with','by','from',
            'that','this','it','my','your','i','you','he','she','we','they','not','no','be','will','how',
            'why','what','do','if','about','has','his','her','our','can','all','but','just','more','than'}
    viral_words = []
    for t in viral_eps["title"]:
        viral_words.extend(w.lower() for w in re.findall(r'[a-zA-Z]+', str(t)) if w.lower() not in stop and len(w) > 2)
    top_words = Counter(viral_words).most_common(15)

    # Era distribution
    era_viral_rate = []
    for era_name in ERA_ORDER:
        all_n = (df_viral["era"] == era_name).sum()
        v_n = (viral_all["era"] == era_name).sum()
        era_viral_rate.append({"Era": era_name, "Viral": v_n, "Total": all_n, "Viral Rate": f"{v_n/all_n*100:.0f}%" if all_n > 0 else "0%"})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Title patterns: Viral vs Non-Viral**")
        st.dataframe(pd.DataFrame(pattern_rows), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Viral rate by era** (remarkably consistent at ~10%)")
        st.dataframe(pd.DataFrame(era_viral_rate), use_container_width=True, hide_index=True)

    st.markdown(f"""
**Key findings:**

- **Health & science topics dominate.** Words like "expert," "doctor," "brain," "cancer," "vitamin"
  appear much more frequently in viral titles. Health content is the channel's strongest viral driver.
- **Duration is similar.** Viral episodes average {v_dur:.0f} min vs {nv_dur:.0f} min for non-viral. Length is uncorrelated with virality.
- **Viral rate is consistent across eras (~10%).** Every era produces roughly the same proportion of
  outliers. The channel raised the baseline while maintaining the same variance.
- **Title formatting is uncorrelated with virality.** Viral episodes use fewer ALL CAPS words ({pattern_rows[6]['Viral %']}
  vs {pattern_rows[6]['Non-Viral %']}). Content quality drives virality.
- **Most common viral title words:** {', '.join(w for w, _ in top_words[:10])}
""")

st.markdown("---")

# ==================================================================
# SECTION 5: How Important Are Viral Videos to Growth?
# ==================================================================
st.header("How Important Are Viral Videos to Growth?")

df_viral_contrib = df_episodes.copy()
_era_va = df_viral_contrib.groupby("era")["view_count"].agg(["mean", "std"]).reset_index()
_era_va.columns = ["era", "_vm", "_vs"]
df_viral_contrib = df_viral_contrib.merge(_era_va, on="era")
df_viral_contrib["_vz"] = (df_viral_contrib["view_count"] - df_viral_contrib["_vm"]) / df_viral_contrib["_vs"].clip(lower=1)
df_viral_contrib["_viral"] = df_viral_contrib["_vz"] > 2.0

contrib_rows = []
for era_name in ERA_ORDER:
    era_all = df_viral_contrib[df_viral_contrib["era"] == era_name]
    era_v = era_all[era_all["_viral"]]
    era_nv = era_all[~era_all["_viral"]]
    total = era_all["view_count"].sum()
    v_total = era_v["view_count"].sum()
    contrib_rows.append({
        "Era": era_name,
        "Viral Episodes": len(era_v),
        "Total Episodes": len(era_all),
        "Viral Rate": f"{len(era_v)/len(era_all)*100:.0f}%" if len(era_all) > 0 else "0%",
        "Viral Views": int(v_total),
        "Total Views": int(total),
        "Viral Share of Views": f"{v_total/total*100:.0f}%" if total > 0 else "0%",
        "Non-Viral Avg Views": f"{era_nv['view_count'].mean():,.0f}" if len(era_nv) > 0 else "0",
    })

st.dataframe(pd.DataFrame(contrib_rows), use_container_width=True, hide_index=True,
    column_config={
        "Viral Views": st.column_config.NumberColumn(format="%,d"),
        "Total Views": st.column_config.NumberColumn(format="%,d"),
    },
)

st.markdown("""
**Viral videos contributed 32% of total views in Pre-Growth but only 14% in the Clip Era.**
As the channel grew, the baseline rose and viral hits became a smaller share of the total.
Growth was driven by lifting average performance across *all* episodes.
""")

st.markdown("---")

# ==================================================================
# SECTION 5b: Do Better Descriptions Lead to More Views?
# ==================================================================
st.header("Do Better Descriptions Lead to More Views?")

df_desc = df_episodes.copy()
df_desc["full_desc"] = df_desc["description"].fillna("")
df_desc["desc_len"] = df_desc["full_desc"].str.len()
df_desc["desc_word_count"] = df_desc["full_desc"].str.split().str.len().fillna(0).astype(int)
df_desc["has_bullet_points"] = df_desc["full_desc"].str.contains(r"[◼▪️•●■]|^\-\s", regex=True, na=False)

# Scatter: desc length vs views
fig_desc = px.scatter(
    df_desc, x="desc_len", y="view_count", color="era",
    hover_data=["title"],
    title="Description Length vs Views (each dot = one episode)",
    labels={"desc_len": "Description Length (characters)", "view_count": "Views"},
    template="plotly_white", height=400,
    color_discrete_map=ERA_COLORS,
    category_orders={"era": ERA_ORDER},
    opacity=0.6,
)
st.plotly_chart(fig_desc, use_container_width=True)

# Within-era correlations
era_corr_rows = []
for era_name in ERA_ORDER:
    era_df = df_desc[df_desc["era"] == era_name]
    if len(era_df) < 10:
        continue
    r = era_df["desc_len"].corr(era_df["view_count"])
    era_corr_rows.append({
        "Era": era_name,
        "Episodes": len(era_df),
        "Avg Desc Length": f"{era_df['desc_len'].mean():,.0f} chars",
        "Correlation (desc len vs views)": f"{r:.3f}",
    })

# Bullet points comparison
bp_with = df_desc[df_desc["has_bullet_points"]]
bp_without = df_desc[~df_desc["has_bullet_points"]]

st.markdown("**Within-era correlation between description length and views:**")
st.dataframe(pd.DataFrame(era_corr_rows), use_container_width=True, hide_index=True)

st.markdown(f"""
**No.** At first glance, longer descriptions appear to correlate with more views (r=0.26 overall).
But this is a spurious correlation driven by era: newer eras have both longer descriptions *and*
more views. Within each era, the correlation drops to near zero (ranging from -0.12 to +0.07 in
the three most recent eras).

Other description features show a similar pattern:
- Episodes with bullet point formatting average {bp_with['view_count'].mean()/1e6:.1f}M views vs
  {bp_without['view_count'].mean()/1e6:.1f}M without, but bullet points were adopted more in later
  (higher-view) eras.
- Viral and non-viral episodes have nearly identical description lengths (~2,100 chars each).

**The channel's descriptions have gotten more structured over time (longer, more formatted), but
this reflects a maturing production process, not a driver of views.** What gets views is the guest,
the topic, and the title. The description is read after someone has already clicked.
""")

st.markdown("---")

# ==================================================================
# SECTION 6: Monthly Growth Rate
# ==================================================================
st.header("Monthly Growth Rate")
st.caption("Month-over-month percentage change in total views. Shows acceleration and deceleration clearly.")

df_growth = df_episodes.copy()
df_growth["month"] = df_growth["published_at"].dt.to_period("M").dt.to_timestamp()
monthly_total = df_growth.groupby("month")["view_count"].sum().reset_index()
monthly_total.columns = ["month", "total_views"]
monthly_total = monthly_total.sort_values("month")
monthly_total["mom_pct"] = monthly_total["total_views"].pct_change() * 100
monthly_total["rolling_3m"] = monthly_total["mom_pct"].rolling(3, min_periods=1).mean()

# Assign era for coloring
def get_era(dt):
    for era_name in ERA_ORDER:
        s, e = ERAS[era_name]
        if s <= dt.strftime("%Y-%m-%d") <= e:
            return era_name
    return "Unknown"

monthly_total["era"] = monthly_total["month"].apply(get_era)
monthly_total = monthly_total[monthly_total["era"] != "Unknown"]

fig_gr = go.Figure()

# Bars colored by era
for era_name in ERA_ORDER:
    era_m = monthly_total[monthly_total["era"] == era_name]
    if era_m.empty:
        continue
    fig_gr.add_trace(go.Bar(
        x=era_m["month"], y=era_m["mom_pct"],
        name=era_name, marker_color=ERA_COLORS[era_name], opacity=0.7,
        hovertemplate="%{x|%b %Y}<br>MoM change: %{y:.0f}%<extra>" + era_name + "</extra>",
    ))

# Rolling average line
fig_gr.add_trace(go.Scatter(
    x=monthly_total["month"], y=monthly_total["rolling_3m"],
    mode="lines", name="3-Month Rolling Avg",
    line=dict(color="#F44336", width=3),
))

fig_gr.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.3)

fig_gr.update_layout(
    title="Month-over-Month Total Views Growth Rate (%) by Era",
    template="plotly_white", height=450,
    yaxis_title="MoM Growth %", xaxis_title="Month",
    hovermode="x unified", barmode="relative",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
st.plotly_chart(fig_gr, use_container_width=True)

st.caption(
    "Positive bars = month grew vs prior month. Negative = contracted. "
    "The red line smooths out noise. Notice the sustained positive growth during Breakout (2023) "
    "and the stabilization in Established/Clip Era."
)

# Same chart excluding Pre-Growth for better y-axis scale
monthly_post = monthly_total[monthly_total["era"] != "Pre-Growth"].copy()

fig_gr2 = go.Figure()
for era_name in ERA_ORDER[1:]:  # Skip Pre-Growth
    era_m = monthly_post[monthly_post["era"] == era_name]
    if era_m.empty:
        continue
    fig_gr2.add_trace(go.Bar(
        x=era_m["month"], y=era_m["mom_pct"],
        name=era_name, marker_color=ERA_COLORS[era_name], opacity=0.7,
        hovertemplate="%{x|%b %Y}<br>MoM change: %{y:.0f}%<extra>" + era_name + "</extra>",
    ))

monthly_post["rolling_3m"] = monthly_post["mom_pct"].rolling(3, min_periods=1).mean()
fig_gr2.add_trace(go.Scatter(
    x=monthly_post["month"], y=monthly_post["rolling_3m"],
    mode="lines", name="3-Month Rolling Avg",
    line=dict(color="#F44336", width=3),
))
fig_gr2.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.3)

fig_gr2.update_layout(
    title="Monthly Growth Rate: Excluding Pre-Growth (zoomed in)",
    template="plotly_white", height=450,
    yaxis_title="MoM Growth %", xaxis_title="Month",
    hovermode="x unified", barmode="relative",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
st.plotly_chart(fig_gr2, use_container_width=True)

st.caption(
    "Same chart as above but excluding Pre-Growth era (Oct 2020 to Dec 2021). "
    "so the y-axis scale is tighter and later movements are easier to read."
)
