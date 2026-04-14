"""Page 8: Competitor Benchmarking."""

import os

import json

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from components.metrics import format_number
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

st.set_page_config(page_title="Competitors", layout="wide")
st.title("Competitor Benchmarking")

# ---- Load competitor data ----
comp_file = os.path.join(RAW_DIR, "competitors_expanded.json")
if not os.path.exists(comp_file):
    st.error("Competitor data not found. Run data collection first.")
    st.stop()

with open(comp_file) as f:
    comp_data = json.load(f)

st.markdown(
    f"Comparing The Diary of a CEO against {len(comp_data) - 1} podcast channels across four size tiers on YouTube. "
    "Competitors selected based on format (single host interviewing guests), episode length, "
    "and topic overlap (health, business, self-improvement, psychology)."
)

# ---- Competitor selection rationale ----
st.header("Competitor Selection")
st.caption("Channels selected based on: similar format (host + guest interviews), long-form episodes, and topic overlap with DOAC.")

COMPETITOR_INFO = {
    # === DOAC ===
    "The Diary Of A CEO": {"host": "Steven Bartlett", "format": "1-on-1 interviews", "topics": "Health, business, psychology, relationships", "region": "UK", "tier": "Subject", "note": "Subject of this analysis"},
    # === Tier 1: Large (5M+ subs) ===
    "Joe Rogan (PowerfulJRE)": {"host": "Joe Rogan", "format": "1-on-1 interviews", "topics": "Everything (health, politics, culture, comedy)", "region": "US", "tier": "Large (5M+)", "note": "Industry benchmark, largest podcast on YouTube"},
    "Jordan Peterson": {"host": "Jordan Peterson", "format": "Interviews + lectures", "topics": "Psychology, philosophy, culture, politics", "region": "Canada", "tier": "Large (5M+)", "note": "Overlapping guests, similar audience"},
    "Andrew Huberman": {"host": "Andrew Huberman", "format": "Solo + interviews", "topics": "Neuroscience, health, performance", "region": "US", "tier": "Large (5M+)", "note": "Biggest overlap in health/science topics and guests"},
    "Patrick Bet-David (Valuetainment)": {"host": "Patrick Bet-David", "format": "Interviews + panel", "topics": "Business, politics, entrepreneurship", "region": "US", "tier": "Large (5M+)", "note": "Business-focused, high volume"},
    "Jay Shetty Podcast": {"host": "Jay Shetty", "format": "1-on-1 interviews", "topics": "Mindset, relationships, purpose", "region": "US/UK", "tier": "Large (5M+)", "note": "Similar audience demographic"},
    # === Tier 2: Medium (1M-5M subs) ===
    "Lex Fridman": {"host": "Lex Fridman", "format": "1-on-1 interviews", "topics": "Science, AI, philosophy, business", "region": "US", "tier": "Medium (1M-5M)", "note": "Long-form intellectual interviews, overlapping guests"},
    "Lewis Howes": {"host": "Lewis Howes", "format": "1-on-1 interviews", "topics": "Business, health, relationships", "region": "US", "tier": "Medium (1M-5M)", "note": "Same format, similar guests, launched earlier"},
    "Tom Bilyeu (Impact Theory)": {"host": "Tom Bilyeu", "format": "1-on-1 interviews", "topics": "Mindset, health, business, AI", "region": "US", "tier": "Medium (1M-5M)", "note": "Same format, same guest pool"},
    "Chris Williamson": {"host": "Chris Williamson", "format": "1-on-1 interviews", "topics": "Psychology, health, relationships, business", "region": "UK", "tier": "Medium (1M-5M)", "note": "Closest direct competitor: UK-based, same era, same guests"},
    "Alex Hormozi": {"host": "Alex Hormozi", "format": "Solo + interviews", "topics": "Business, marketing, scaling", "region": "US", "tier": "Medium (1M-5M)", "note": "Business-focused, shorter format, high engagement"},
    "Jocko Willink": {"host": "Jocko Willink", "format": "Solo + interviews", "topics": "Leadership, discipline, military, mindset", "region": "US", "tier": "Medium (1M-5M)", "note": "Long-form, discipline/leadership niche"},
    "Tim Ferriss": {"host": "Tim Ferriss", "format": "1-on-1 interviews", "topics": "Productivity, health, business, performance", "region": "US", "tier": "Medium (1M-5M)", "note": "Pioneer of long-form interview format"},
    "Rich Roll": {"host": "Rich Roll", "format": "1-on-1 interviews", "topics": "Health, wellness, endurance, plant-based", "region": "US", "tier": "Medium (1M-5M)", "note": "Health/wellness focus, deep conversations"},
    "Dr Rangan Chatterjee": {"host": "Dr Rangan Chatterjee", "format": "1-on-1 interviews", "topics": "Health, wellness, medicine, lifestyle", "region": "UK", "tier": "Medium (1M-5M)", "note": "UK-based, health-focused, overlapping guests"},
    "Silicon Valley Girl": {"host": "Marina Mogilko", "format": "1-on-1 interviews + vlogs", "topics": "Tech, entrepreneurship, Silicon Valley", "region": "US", "tier": "Medium (1M-5M)", "note": "Tech/startup interview format"},
    # === Tier 3: Small (100K-1M subs) ===
    "Bryce Crawford Podcast": {"host": "Bryce Crawford", "format": "1-on-1 interviews", "topics": "Health, fitness, mindset", "region": "US", "tier": "Small (100K-1M)", "note": "Fast-growing health podcast, launched 2024"},
    "FoundMyFitness (Rhonda Patrick)": {"host": "Rhonda Patrick", "format": "Solo + interviews", "topics": "Nutrition, health, longevity, science", "region": "US", "tier": "Small (100K-1M)", "note": "Frequent DOAC guest, deep science content"},
    "Robinson Erhardt": {"host": "Robinson Erhardt", "format": "1-on-1 interviews", "topics": "Philosophy, culture, intellectual deep dives", "region": "US", "tier": "Small (100K-1M)", "note": "Long-form philosophical conversations"},
    "Farzad": {"host": "Farzad", "format": "1-on-1 interviews", "topics": "Finance, tech, investing, macro", "region": "US", "tier": "Small (100K-1M)", "note": "Finance/tech interview format"},
    "The Jordan Harbinger Show": {"host": "Jordan Harbinger", "format": "1-on-1 interviews", "topics": "Psychology, business, social dynamics", "region": "US", "tier": "Small (100K-1M)", "note": "Long-running interview show, overlapping guest pool"},
    "Armchair Expert with Dax Shepard": {"host": "Dax Shepard", "format": "1-on-1 interviews", "topics": "Celebrity, psychology, culture", "region": "US", "tier": "Small (100K-1M)", "note": "Celebrity-driven long-form, massive audio audience"},
    "Johnathan Bi": {"host": "Johnathan Bi", "format": "1-on-1 interviews + lectures", "topics": "Philosophy, Girard, mimetic theory", "region": "US", "tier": "Small (100K-1M)", "note": "Deep intellectual long-form (2+ hrs)"},
    "Norges Bank Investment Mgmt": {"host": "Various", "format": "Interviews + panels", "topics": "Investing, macro, sovereign wealth", "region": "Norway", "tier": "Small (100K-1M)", "note": "Institutional investing perspective"},
    "Sammi Cohen Talks": {"host": "Sammi Cohen", "format": "1-on-1 interviews", "topics": "Culture, relationships, identity", "region": "US", "tier": "Small (100K-1M)", "note": "Emerging interview format"},
    # === Tier 4: Micro (<100K subs) ===
    "Kevin Rose": {"host": "Kevin Rose", "format": "1-on-1 interviews", "topics": "Tech, wellness, investing, startups", "region": "US", "tier": "Micro (<100K)", "note": "Tech legend, smaller YouTube presence despite fame"},
    "Every": {"host": "Dan Shipper", "format": "1-on-1 interviews", "topics": "AI, writing, productivity, startups", "region": "US", "tier": "Micro (<100K)", "note": "AI-focused interview podcast from media company"},
    "Mind & Matter Podcast": {"host": "Nick Jikomes", "format": "1-on-1 interviews", "topics": "Science, health, neuroscience", "region": "US", "tier": "Micro (<100K)", "note": "Deep science interviews, DOAC guest overlap"},
    "Newcomer Pod": {"host": "Eric Newcomer", "format": "1-on-1 interviews", "topics": "Tech, startups, venture capital", "region": "US", "tier": "Micro (<100K)", "note": "Tech journalism interview format"},
    "Michael Coppola": {"host": "Michael Coppola", "format": "1-on-1 interviews", "topics": "Business, entrepreneurship", "region": "US", "tier": "Micro (<100K)", "note": "Micro channel, early stage"},
    "A Connection TV": {"host": "Various", "format": "1-on-1 interviews", "topics": "Business, leadership, culture", "region": "US", "tier": "Small (100K-1M)", "note": "Interview format, diverse guest range"},
    # === New additions: survived but never broke out ===
    "Preston Pysh": {"host": "Preston Pysh", "format": "1-on-1 interviews", "topics": "Finance, Bitcoin, macro", "region": "US", "tier": "Small (100K-1M)", "note": "Finance + Bitcoin focus, 14 years old, established but plateaued"},
    "Machine Learning Street Talk": {"host": "Various", "format": "1-on-1 interviews", "topics": "Technical AI/ML research", "region": "UK", "tier": "Small (100K-1M)", "note": "Deep technical AI interviews, niche audience"},
    "The Origins Podcast": {"host": "Lawrence Krauss", "format": "1-on-1 interviews", "topics": "Science, physics, cosmology", "region": "US", "tier": "Small (100K-1M)", "note": "Science-focused with prominent physicist host"},
    "The Investors Podcast Network": {"host": "Various", "format": "1-on-1 interviews", "topics": "Investing, value investing, macro", "region": "US", "tier": "Micro (<100K)", "note": "12+ year investing podcast, never broke 100K on YouTube"},
    "TechTechPotato": {"host": "Ian Cutress", "format": "Solo + interviews", "topics": "Semiconductors, chips, hardware", "region": "UK", "tier": "Small (100K-1M)", "note": "Niche semiconductor/tech analysis"},
    "Cool Worlds Podcast": {"host": "David Kipping", "format": "Solo + interviews", "topics": "Astronomy, exoplanets, frontier science", "region": "US", "tier": "Medium (1M-5M)", "note": "Science channel with 1M+ subs, deep astronomy content"},
    "Alex Kantrowitz (Big Technology)": {"host": "Alex Kantrowitz", "format": "1-on-1 interviews", "topics": "Tech industry, platforms", "region": "US", "tier": "Micro (<100K)", "note": "Tech journalism podcast, 12 years, 52K subs"},
    "The Cipher Brief": {"host": "Various", "format": "1-on-1 interviews", "topics": "National security, intelligence", "region": "US", "tier": "Micro (<100K)", "note": "Niche national security focus, 10+ years"},
    "What Bitcoin Did": {"host": "Peter McCormack", "format": "1-on-1 interviews", "topics": "Bitcoin, crypto, macro", "region": "UK", "tier": "Micro (<100K)", "note": "Bitcoin-focused interview show"},
    "TWIML AI Podcast": {"host": "Sam Charrington", "format": "1-on-1 interviews", "topics": "ML, AI research, industry", "region": "US", "tier": "Micro (<100K)", "note": "Long-running ML/AI podcast, 9 years"},
    "threadguy": {"host": "threadguy", "format": "Solo + interviews", "topics": "Crypto culture, DeFi", "region": "US", "tier": "Micro (<100K)", "note": "Crypto culture podcast, 12 years"},
    "Unsupervised Learning (Redpoint)": {"host": "Various", "format": "1-on-1 interviews", "topics": "AI, venture capital", "region": "US", "tier": "Micro (<100K)", "note": "AI/VC podcast from Redpoint Ventures"},
    "Relentless": {"host": "Various", "format": "1-on-1 interviews", "topics": "Founder stories, startups", "region": "US", "tier": "Micro (<100K)", "note": "Founder interview podcast, 8+ years"},
    "Cleaning Up Podcast": {"host": "Various", "format": "1-on-1 interviews", "topics": "Energy, climate, clean tech", "region": "UK", "tier": "Micro (<100K)", "note": "Energy/climate niche, 5+ years"},
    "Bay Bridge Bio": {"host": "Various", "format": "1-on-1 interviews", "topics": "Biotech, founders, science", "region": "US", "tier": "Micro (<100K)", "note": "Biotech founder interviews, 7+ years"},
    "Rational VC Podcast": {"host": "Various", "format": "1-on-1 interviews", "topics": "VC, history, investing", "region": "US", "tier": "Micro (<100K)", "note": "VC + history deep dives, 150+ min median episodes"},
    "Searching for Mana": {"host": "Various", "format": "1-on-1 interviews", "topics": "Technology, capital, institutions", "region": "US", "tier": "Micro (<100K)", "note": "Tech/capital long-form, 6 years, 3.2K subs"},
    "Around The Coin": {"host": "Various", "format": "1-on-1 interviews", "topics": "Fintech, payments", "region": "US", "tier": "Micro (<100K)", "note": "12 years of fintech interviews, still 2.2K subs"},
    "Prime Movers Lab": {"host": "Various", "format": "1-on-1 interviews", "topics": "Frontier tech, deep tech VC", "region": "US", "tier": "Micro (<100K)", "note": "Deep tech VC interviews, minimal YouTube growth"},
}

CHANNEL_URLS = {name: f"https://www.youtube.com/channel/{comp_data.get(name, {}).get('channel_id', '')}" for name in COMPETITOR_INFO}

info_rows = []
for name, info in COMPETITOR_INFO.items():
    cd = comp_data.get(name, {})
    has_shorts = cd.get("has_shorts", False)
    sc = cd.get("shorts_count_in_50", 0)
    lc = cd.get("long_count_in_50", 0)
    created = cd.get("created_at", "")
    subs = cd.get("subscriber_count", 0)
    age_years = round((pd.Timestamp("2026-04-10") - pd.Timestamp(created)).days / 365.25, 1) if created else 0
    long_cadence = cd.get("long_eps_per_month", 0)
    long_dur = cd.get("recent_long_avg_duration_min", 0)

    info_rows.append({
        "Channel": name,
        "Link": CHANNEL_URLS.get(name, ""),
        "Tier": info.get("tier", ""),
        "Host": info["host"],
        "Region": info["region"],
        "Format": info["format"],
        "Topics": info["topics"],
        "Launched": created,
        "Age (yrs)": age_years,
        "Subscribers": subs,
        "Has Clips?": "Yes" if has_shorts else "No",
        "Clip Ratio (last 50)": f"{sc} clips / {lc} long" if (sc + lc) > 0 else "",
        "Long Eps/Month": long_cadence,
        "Avg Ep Duration (min)": int(long_dur) if long_dur > 0 else 0,
        "Why Included": info["note"],
    })

info_df = pd.DataFrame(info_rows)
st.dataframe(
    info_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Link": st.column_config.LinkColumn("Link", display_text="YouTube"),
        "Subscribers": st.column_config.NumberColumn(format="%,d"),
    },
)

st.markdown("---")

# ---- Build comparison DataFrame ----
comp_rows = []
for name, data in comp_data.items():
    tier = COMPETITOR_INFO.get(name, {}).get("tier", "Unknown")
    comp_rows.append({
        "channel_name": name,
        "tier": tier,
        "subscriber_count": data["subscriber_count"],
        "total_views": data["total_views"],
        "video_count": data["video_count"],
        "avg_views_per_video": data.get("avg_views_per_video", data["total_views"] / max(data["video_count"], 1)),
        "created_at": data["created_at"],
        "recent_long_count": data.get("recent_long_count", 0),
        "recent_long_avg_views": data.get("recent_long_avg_views", 0),
        "recent_long_median_views": data.get("recent_long_median_views", 0),
        "recent_long_avg_likes": data.get("recent_long_avg_likes", 0),
        "recent_long_engagement_pct": data.get("recent_long_engagement_pct", 0),
        "recent_long_avg_duration_min": data.get("recent_long_avg_duration_min", 0),
    })

comparison_all = pd.DataFrame(comp_rows).sort_values("subscriber_count", ascending=False)

# Compute derived metrics
comparison_all["views_per_subscriber"] = (comparison_all["total_views"] / comparison_all["subscriber_count"].clip(lower=1)).round(1)
comparison_all["channel_age_years"] = ((pd.Timestamp("2026-04-10") - pd.to_datetime(comparison_all["created_at"])).dt.days / 365.25).round(1)
comparison_all["subs_per_year"] = (comparison_all["subscriber_count"] / comparison_all["channel_age_years"].clip(lower=0.1)).astype(int)
comparison_all["is_doac"] = comparison_all["channel_name"] == "The Diary Of A CEO"

# ---- Tier filter (applies to all sections below) ----
all_tiers = ["Subject", "Large (5M+)", "Medium (1M-5M)", "Small (100K-1M)", "Micro (<100K)", "Unknown"]
available_tiers = [t for t in all_tiers if t in comparison_all["tier"].unique()]
selected_tiers = st.multiselect(
    "Filter by tier (applies to all sections below):",
    available_tiers,
    default=available_tiers,
    key="tier_filter",
)
comparison = comparison_all[comparison_all["tier"].isin(selected_tiers)].copy()
comparison["bar_color"] = comparison["is_doac"].map({True: "#F44336", False: "#42A5F5"})
st.caption(f"Showing {len(comparison)} of {len(comparison_all)} channels.")

# ---- Channel Comparison Table with bars ----
st.header("Episode Performance Comparison (Long Episodes Only)")
st.caption(
    "Based on the most recent long-form episodes (5+ min) from each channel. "
    "Clips/shorts excluded. Sorted by avg views/episode."
)

# Build raw data for bar rendering
perf_rows = []
for _, row in comparison.sort_values("recent_long_avg_views", ascending=False).iterrows():
    cd = comp_data.get(row["channel_name"], {})
    perf_rows.append({
        "Channel": row["channel_name"],
        "Avg Long Eps/Mo": cd.get("long_eps_per_month", 0),
        "Avg Views/Ep": row["recent_long_avg_views"],
        "Median Views/Ep": row["recent_long_median_views"],
        "Avg Likes/Ep": row["recent_long_avg_likes"],
        "Engagement %": row["recent_long_engagement_pct"],
        "Views/Sub": float(row["views_per_subscriber"]),
        "Subs/Year": int(row["subs_per_year"]),
    })

perf_df = pd.DataFrame(perf_rows)

bar_cols = ["Avg Long Eps/Mo", "Avg Views/Ep", "Median Views/Ep", "Avg Likes/Ep",
            "Engagement %", "Views/Sub", "Subs/Year"]

col_maxes = {col: float(perf_df[col].max()) for col in bar_cols if col in perf_df.columns}

def fmt_val(col, val):
    if col == "Engagement %":
        return f"{val:.2f}%"
    elif col == "Avg Long Eps/Mo":
        return f"{val:.1f}"
    elif col == "Views/Sub":
        return f"{val:.1f}"
    elif val >= 1000:
        return f"{val:,.0f}"
    else:
        return f"{val:,.0f}"

html = '<table class="perf-table"><thead><tr>'
for col in ["Channel"] + bar_cols:
    html += f"<th>{col}</th>"
html += "</tr></thead><tbody>"

for _, row in perf_df.iterrows():
    is_doac = row["Channel"] == "The Diary Of A CEO"
    row_style = "background:rgba(244,67,54,0.05);" if is_doac else ""
    name_weight = "font-weight:bold; color:#F44336;" if is_doac else "font-weight:bold;"
    html += f'<tr style="{row_style}">'
    html += f'<td style="padding:6px 8px; {name_weight}">{row["Channel"]}</td>'
    for col in bar_cols:
        val = float(row[col])
        cmax = col_maxes.get(col, 1)
        pct = val / cmax * 100 if cmax > 0 else 0
        bar_color = "rgba(244,67,54,0.2)" if is_doac else "rgba(66,165,245,0.15)"
        html += (
            f'<td style="position:relative; padding:6px 8px;">'
            f'<div style="position:absolute; left:0; top:0; bottom:0; width:{pct:.0f}%; '
            f'background:{bar_color}; z-index:0;"></div>'
            f'<span style="position:relative; z-index:1;">{fmt_val(col, val)}</span></td>'
        )
    html += "</tr>"
html += "</tbody></table>"

st.markdown(f'<div style="max-height:600px; overflow-y:auto;">{html}</div>', unsafe_allow_html=True)
st.markdown(
    """<style>
    .perf-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .perf-table th { background: #f5f5f5; padding: 6px 8px; text-align: left; border-bottom: 2px solid #ddd; white-space: nowrap; position: sticky; top: 0; z-index: 1; }
    .perf-table td { border-bottom: 1px solid #eee; vertical-align: top; white-space: nowrap; }
    </style>""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ---- Efficiency & Performance Analysis ----
st.header("Efficiency & Performance Analysis")
st.caption(
    "\"Recent\" = last 50 uploads per channel (filtered to long episodes only). "
    "This covers roughly the last 2-6 months depending on each channel's posting frequency."
)

doac_color = "#F44336"
other_color = "#42A5F5"


def ranked_bar(df, x_col, title, ticksuffix=""):
    """Horizontal bar chart sorted by value with DOAC in red at its natural rank."""
    sorted_df = df.sort_values(x_col, ascending=True)
    fig = go.Figure(go.Bar(
        x=sorted_df[x_col],
        y=sorted_df["channel_name"],
        orientation="h",
        marker_color=sorted_df["bar_color"].tolist(),
    ))
    fig.update_layout(
        title=title, template="plotly_white", showlegend=False,
        xaxis=dict(ticksuffix=ticksuffix),
    )
    return fig


# 1. Avg Views/Episode
st.plotly_chart(ranked_bar(comparison, "recent_long_avg_views", "Avg Views per Long Episode (recent)"), use_container_width=True)

# 2. Scatter: subscribers vs avg views (with channel selector)
st.subheader("Subscribers vs Avg Views/Episode")
scatter1_exclude = st.multiselect(
    "Exclude channels to zoom into the cluster:",
    comparison["channel_name"].tolist(),
    default=[],
    key="scatter1_exclude",
)
scatter1_df = comparison[~comparison["channel_name"].isin(scatter1_exclude)]
fig = go.Figure()
for _, row in scatter1_df.iterrows():
    fig.add_trace(go.Scatter(
        x=[row["subscriber_count"]], y=[row["recent_long_avg_views"]],
        mode="markers+text", text=[row["channel_name"]],
        textposition="top center", textfont_size=9,
        marker=dict(size=10, color=doac_color if row["is_doac"] else other_color),
        showlegend=False,
    ))
fig.update_layout(
    title="Subscribers vs Avg Views/Episode (who punches above their weight?)",
    xaxis_title="Subscribers", yaxis_title="Avg Views/Episode",
    template="plotly_white", height=500,
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ranked_bar(comparison, "views_per_subscriber", "Views per Subscriber (content leverage)"), use_container_width=True)
with col2:
    st.plotly_chart(ranked_bar(comparison, "subs_per_year", "Subscribers per Year (growth velocity)"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(ranked_bar(comparison, "recent_long_engagement_pct", "Avg Engagement Rate on Long Episodes", ticksuffix="%"), use_container_width=True)

# 6. Scatter: engagement vs views (with channel selector)
with col4:
    scatter2_exclude = st.multiselect(
        "Exclude channels:",
        comparison["channel_name"].tolist(),
        default=[],
        key="scatter2_exclude",
    )
    scatter2_df = comparison[~comparison["channel_name"].isin(scatter2_exclude)]
    fig = go.Figure()
    for _, row in scatter2_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["recent_long_avg_views"]], y=[row["recent_long_engagement_pct"]],
            mode="markers+text", text=[row["channel_name"]],
            textposition="top center", textfont_size=9,
            marker=dict(size=10, color=doac_color if row["is_doac"] else other_color),
            showlegend=False,
        ))
    fig.update_layout(
        title="Avg Views vs Engagement (reach vs quality)",
        xaxis_title="Avg Views/Episode", yaxis_title="Engagement %",
        template="plotly_white", height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

# 7. Scatter: subscribers vs channel age
st.subheader("Subscribers vs Channel Age")
scatter3_exclude = st.multiselect(
    "Exclude channels:",
    comparison["channel_name"].tolist(),
    default=[],
    key="scatter3_exclude",
)
scatter3_df = comparison[~comparison["channel_name"].isin(scatter3_exclude)]
fig = go.Figure()
for _, row in scatter3_df.iterrows():
    fig.add_trace(go.Scatter(
        x=[row["channel_age_years"]], y=[row["subscriber_count"]],
        mode="markers+text", text=[row["channel_name"]],
        textposition="top center", textfont_size=9,
        marker=dict(size=10, color=doac_color if row["is_doac"] else other_color),
        showlegend=False,
    ))
fig.update_layout(
    title="Channel Age vs Subscribers (who grew fastest relative to age?)",
    xaxis_title="Channel Age (years)", yaxis_title="Subscribers",
    template="plotly_white", height=500,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---- Radar Chart ----
st.header("Multi-Dimensional Comparison")
st.caption("All metrics normalized to 0-100 scale (100 = highest among all channels).")

radar_metrics = ["subscriber_count", "total_views", "video_count", "avg_views_per_video", "views_per_subscriber", "subs_per_year"]
radar_labels = ["Subscribers", "Total Views", "Videos", "Avg Views/Video", "Views/Subscriber", "Subs/Year"]

# Select which channels to show on radar (too many is unreadable)
available_names = comparison["channel_name"].tolist()
default_radar = [n for n in ["The Diary Of A CEO", "Joe Rogan (PowerfulJRE)", "Chris Williamson", "Andrew Huberman", "Lex Fridman"] if n in available_names]
radar_channels = st.multiselect(
    "Select channels for radar chart",
    available_names,
    default=default_radar,
)

if radar_channels:
    radar_df = comparison[comparison["channel_name"].isin(radar_channels)].copy()

    # Normalize to 0-100
    for col in radar_metrics:
        radar_df[col] = pd.to_numeric(radar_df[col], errors="coerce").fillna(0).astype(float)
        col_max = float(radar_df[col].max())
        if col_max > 0:
            radar_df[col] = radar_df[col].apply(lambda x: round(float(x) / col_max * 100, 1))

    fig = go.Figure()
    for _, row in radar_df.iterrows():
        values = [float(row[m]) for m in radar_metrics] + [float(row[radar_metrics[0]])]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=radar_labels + [radar_labels[0]],
            name=row["channel_name"],
            fill="toself",
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Channel Comparison (normalized to 0-100)",
        template="plotly_white",
        height=550,
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==================================================================
# SECRET SAUCE ANALYSIS
# ==================================================================
st.header("The Secret Sauce: What Makes DOAC Outperform?")

st.markdown(
    "The Diary of a CEO gets **6.3x more views per episode** than the average competitor. "
    "It is the youngest channel in this set (launched 2019), yet ranks #1 in avg views and #1 in subscriber growth velocity. "
    "What explains this?"
)

# ---- DOAC vs field summary ----
doac_data = comp_data.get("The Diary Of A CEO", {})
# Field averages based on currently filtered channels (excluding DOAC itself)
field_channels = comparison[~comparison["is_doac"]]
field_avg_views = field_channels["recent_long_avg_views"].mean() if len(field_channels) > 0 else 1
field_avg_dur = field_channels["recent_long_avg_duration_min"].mean() if len(field_channels) > 0 else 0
field_avg_cadence = field_channels["channel_name"].apply(lambda n: comp_data.get(n, {}).get("long_eps_per_month", 0)).mean() if len(field_channels) > 0 else 0
field_avg_eng = field_channels["recent_long_engagement_pct"].mean() if len(field_channels) > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("DOAC Avg Views/Ep", format_number(doac_data.get("recent_long_avg_views", 0)),
            delta=f"{doac_data.get('recent_long_avg_views', 0) / max(field_avg_views, 1):.1f}x field avg")
col2.metric("DOAC Ep Duration", f"{doac_data.get('recent_long_avg_duration_min', 0):.0f}m",
            delta=f"+{doac_data.get('recent_long_avg_duration_min', 0) - field_avg_dur:.0f}m vs field")
col3.metric("DOAC Long Eps/Mo", f"{doac_data.get('long_eps_per_month', 0):.0f}",
            delta=f"{doac_data.get('long_eps_per_month', 0) - field_avg_cadence:+.0f} vs field")
col4.metric("DOAC Engagement", f"{doac_data.get('recent_long_engagement_pct', 0):.2f}%",
            delta=f"{doac_data.get('recent_long_engagement_pct', 0) - field_avg_eng:+.2f}pp vs field")

st.markdown("---")

# ---- Correlation analysis ----
st.subheader("What Metrics Correlate with Views?")
st.caption(f"Pearson correlation across all {len(comparison)} channels. Positive = associated with higher views.")

if len(comparison) >= 5:
    corr_rows = []
    for col, label in [
        ("subscriber_count", "Subscribers"),
        ("recent_long_avg_duration_min", "Episode Duration"),
        ("recent_long_engagement_pct", "Engagement Rate"),
        ("long_eps_per_month", "Posting Cadence"),
        ("channel_age_years", "Channel Age"),
        ("video_count", "Total Videos Published"),
    ]:
        if col == "long_eps_per_month":
            vals = comparison["channel_name"].apply(lambda n: comp_data.get(n, {}).get("long_eps_per_month", 0)).astype(float)
        else:
            vals = comparison[col].astype(float)
        r = vals.corr(comparison["recent_long_avg_views"].astype(float))
        if pd.isna(r):
            r = 0.0
        corr_rows.append({"Metric": label, "Correlation with Avg Views": round(r, 3), "Interpretation": (
            "Strong positive" if r > 0.5 else "Moderate positive" if r > 0.2 else
            "Weak" if abs(r) <= 0.2 else "Moderate negative" if r > -0.5 else "Strong negative"
        )})
    st.dataframe(pd.DataFrame(corr_rows), use_container_width=True, hide_index=True)
else:
    st.info("Select more tiers to see correlation analysis (need at least 5 channels).")

st.markdown("---")

# ---- DOAC percentile rank ----
st.subheader("Where DOAC Ranks Among Competitors")

doac_comp = comparison[comparison["channel_name"] == "The Diary Of A CEO"]
if doac_comp.empty:
    st.info("Select the 'Subject' tier to see DOAC ranking.")
elif len(comparison) < 3:
    st.info("Select more tiers to see rankings.")
else:
    doac_row = doac_comp.iloc[0]
    cadence_val = comp_data.get("The Diary Of A CEO", {}).get("long_eps_per_month", 0)

    rank_rows = []
    for col, label, val, fmt in [
        ("recent_long_avg_views", "Avg Views/Episode", doac_row["recent_long_avg_views"], lambda v: f"{v:,.0f}"),
        ("subscriber_count", "Subscribers", doac_row["subscriber_count"], lambda v: f"{v:,.0f}"),
        ("recent_long_avg_duration_min", "Episode Duration (min)", doac_row["recent_long_avg_duration_min"], lambda v: f"{v:.0f}"),
        ("recent_long_engagement_pct", "Engagement Rate", doac_row["recent_long_engagement_pct"], lambda v: f"{v:.2f}%"),
        ("channel_age_years", "Channel Age (yrs)", doac_row["channel_age_years"], lambda v: f"{v:.1f}"),
    ]  :
        pct = (comparison[col].astype(float) < float(val)).mean() * 100
        rank = int((comparison[col].astype(float) >= float(val)).sum())
        rank_rows.append({
            "Metric": label,
            "DOAC Value": fmt(val),
            "Rank": f"#{rank} of {len(comparison)}",
            "Percentile": f"{pct:.0f}th",
        })

    # Add cadence separately
    all_cadences = [comp_data.get(n, {}).get("long_eps_per_month", 0) for n in comparison["channel_name"]]
    pct = sum(1 for c in all_cadences if c < cadence_val) / len(all_cadences) * 100
    rank = sum(1 for c in all_cadences if c >= cadence_val)
    rank_rows.append({
        "Metric": "Long Eps/Month",
        "DOAC Value": f"{cadence_val:.1f}",
        "Rank": f"#{rank} of {len(comparison)}",
        "Percentile": f"{pct:.0f}th",
    })

    st.dataframe(pd.DataFrame(rank_rows), use_container_width=True, hide_index=True)

st.markdown("---")

# ---- The Secret Sauce ----
st.subheader("Key Findings")

n_channels = len(comparison)
n_micro = len(comparison[comparison["tier"] == "Micro (<100K)"])

st.markdown(f"""
**1. Episode duration correlates with per-episode views across {n_channels} channels.**
DOAC episodes average 120 minutes. Across the competitive set, longer episodes correlate with
higher views per episode. Channels that went shorter (Valuetainment at 11 min, Alex Hormozi at
27 min) have significantly lower per-episode performance. Many Micro-tier channels also run
shorter episodes (25-55 min), which may limit algorithmic reach.

**2. DOAC achieved more with less.**
With only {doac_data.get('video_count', 0):,} total videos, DOAC generated the highest avg views
per video of any channel in the set. It publishes ~9 long episodes per month, well below
high-volume channels like Valuetainment (205 eps/mo) or Chris Williamson (32 eps/mo). The
strategy is fewer, higher-quality episodes.

**3. Channel age does not predict success.**
DOAC launched in 2019. Multiple channels in this set have been producing content for 10-15+ years
(Around The Coin: 12 years at 2.2K subs; threadguy: 12 years at 24K; Tim Ferriss: 20 years at
1.76M). Longevity alone does not compound. The channels that broke through had specific catalysts
(DOAC: Dragons' Den; Huberman: pandemic health interest; Lex Fridman: viral tech interviews).

**4. Most podcast channels plateau below 100K subscribers.**
{n_micro} of {n_channels} channels in this set are below 100K subs despite years of consistent output.
The gap between Small and Large tiers is massive (10-1000x in avg views). Breaking through requires
something beyond steady publishing: a topic-market fit, a distribution event, or production quality
that triggers algorithmic recommendation.

**5. Topic selection separates tiers.**
Large-tier channels (DOAC, Rogan, Huberman, Peterson) cover broad topics that appeal to mainstream
audiences: health, psychology, self-improvement. Micro-tier channels tend toward niche verticals
(fintech, semiconductors, biotech, crypto) that cap their addressable audience.

**6. The clip strategy adds reach without diluting quality.**
DOAC publishes ~37 clips per 50 uploads (74%). As shown in the Clip Analysis, these clips add
~22% incremental reach. Many micro and small channels publish zero clips, missing this lever entirely.
""")

st.markdown("---")
st.caption("Data collected via YouTube Data API v3 on April 10, 2026. Subscriber counts are rounded by YouTube.")
