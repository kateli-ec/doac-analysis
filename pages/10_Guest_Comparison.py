"""Page 10: Same Guest, Different Show — Conversation Style Comparison."""

import os

import json
import re
from collections import Counter

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

st.set_page_config(page_title="Guest Comparison", layout="wide")
st.title("Same Guest, Different Show")

st.markdown("""
When the same guest appears on two different podcasts, the differences in the conversation
reveal the host's style, editorial choices, and what each show optimizes for.

**Casey Handmer** (Caltech PhD, ex-NASA JPL, founder of Terraform Industries) appeared on both
**Relentless** and **Dwarkesh Patel** within two weeks of each other in August 2025. This is
a rare natural experiment: same person, same time period, same company stage, but two very
different conversations.
""")

st.markdown("---")

# ==================================================================
# SECTION 1: Episode Overview
# ==================================================================
st.header("Episode Overview")

comp = pd.DataFrame({
    "Metric": [
        "Watch",
        "Title",
        "Host",
        "Published",
        "Duration",
        "Views",
        "Likes",
        "Comments",
        "Engagement %",
        "Timestamps",
        "Avg Segment Length",
        "Word Count (transcript)",
        "Words per Minute",
        "Channel Subscribers",
    ],
    "Relentless": [
        "https://www.youtube.com/watch?v=rmmvqkNPo6A",
        "#42 - Why Ancient Rome Didn't Industrialize | Casey Handmer, CEO Terraform Industries",
        "Ti Morse",
        "Aug 29, 2025",
        "105 min",
        "7,594",
        "262",
        "11",
        "3.6%",
        "17",
        "6.2 min",
        "22,314",
        "213",
        "17,800",
    ],
    "Dwarkesh Patel": [
        "https://www.youtube.com/watch?v=3cDHx2_QbPE",
        "China is killing the US on energy. Does that mean they'll win AGI? — Casey Handmer",
        "Dwarkesh Patel",
        "Aug 15, 2025",
        "68 min",
        "92,935",
        "2,045",
        "126",
        "2.3%",
        "8",
        "8.5 min",
        "~13,500 (est.)",
        "~199 (est.)",
        "1,260,000",
    ],
    "Ratio (Dwarkesh / Relentless)": [
        "",
        "",
        "",
        "14 days earlier",
        "0.65x",
        "12.2x",
        "7.8x",
        "11.5x",
        "0.64x",
        "0.47x",
        "1.37x",
        "~0.60x",
        "~0.93x",
        "70.8x",
    ],
})

# Render as HTML table so links are clickable
comp_html = comp.copy()
# Make the Watch row clickable
comp_html.loc[comp_html["Metric"] == "Watch", "Relentless"] = '<a href="https://www.youtube.com/watch?v=rmmvqkNPo6A" target="_blank">Watch on YouTube</a>'
comp_html.loc[comp_html["Metric"] == "Watch", "Dwarkesh Patel"] = '<a href="https://www.youtube.com/watch?v=3cDHx2_QbPE" target="_blank">Watch on YouTube</a>'
comp_html.loc[comp_html["Metric"] == "Watch", "Ratio (Dwarkesh / Relentless)"] = ""

st.markdown(
    comp_html.to_html(index=False, escape=False, classes="comp-table"),
    unsafe_allow_html=True,
)
st.markdown(
    """<style>
    .comp-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .comp-table th { background: #f5f5f5; padding: 8px; text-align: left; border-bottom: 2px solid #ddd; }
    .comp-table td { padding: 8px; border-bottom: 1px solid #eee; vertical-align: top; }
    .comp-table td:first-child { font-weight: bold; white-space: nowrap; }
    .comp-table a { color: #1976D2; text-decoration: none; }
    .comp-table a:hover { text-decoration: underline; }
    </style>""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ==================================================================
# SECTION 2: Topic Comparison
# ==================================================================
st.header("What Each Show Chose to Talk About")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Relentless Topics (17 segments):**")
    relentless_topics = [
        ("0:27", "Terraforming Mars"),
        ("3:14", "Why solar will be our main power source"),
        ("5:42", "How to create more Elons"),
        ("8:37", "Starting companies that won't be built if you don't"),
        ("19:55", "Playing Factorio IRL"),
        ("22:17", "What role suffering plays in greatness"),
        ("24:47", "How to succeed at MrBeast"),
        ("34:21", "How Elon makes things happen"),
        ("50:58", "Industrializing Rome"),
        ("55:50", "We're still using leaded gasoline"),
        ("1:00:10", "China's looming demographic catastrophe"),
        ("1:07:42", "Creating incentives to have more kids"),
        ("1:12:16", "O'Neill Cylinders, Building a Mars base"),
        ("1:19:54", "Government strangling innovation"),
        ("1:33:48", "Chewing glass for the love of it"),
        ("1:39:17", "Closer to critical infrastructure than he hoped"),
    ]
    for ts, topic in relentless_topics:
        st.caption(f"{ts} — {topic}")

with col2:
    st.markdown("**Dwarkesh Topics (8 segments):**")
    dwarkesh_topics = [
        ("00:00", "Why doesn't China win by default?"),
        ("08:28", "Why hyperscalers choose natural gas over solar"),
        ("18:01", "Solar's astonishing learning rates"),
        ("27:02", "How to build 50,000 acre solar-powered data centers"),
        ("40:24", "Environmental regulations blocking clean energy"),
        ("44:04", "Batteries replacing the grid"),
        ("49:14", "GDP is broken, AGI's true value in total energy use"),
        ("58:45", "Silicon wafers in space"),
    ]
    for ts, topic in dwarkesh_topics:
        st.caption(f"{ts} — {topic}")

st.markdown("---")

# ==================================================================
# SECTION 3: Style Analysis
# ==================================================================
st.header("How the Conversations Differ")

st.subheader("1. Scope: Narrow vs Wide")
st.markdown("""
**Dwarkesh** keeps the entire 68 minutes tightly focused on **one thesis**: solar energy will
power AI infrastructure, and here's why. Every segment builds on the previous one. The conversation
is essentially a structured argument with evidence, counterarguments, and resolution.

**Relentless** covers **16 different topics** in 105 minutes, ranging from terraforming Mars to
Ancient Rome to MrBeast to demographic collapse. The conversation follows the guest's interests
wherever they lead. It's an exploration of how Casey Handmer *thinks*, not just what he knows
about energy.
""")

st.subheader("2. Question Depth: Deep Drill vs Rapid Fire")
st.markdown("""
**Dwarkesh** spends an average of **8.5 minutes per topic**. Each segment goes deep: "Why don't
hyperscalers choose solar?", then "What are solar's learning rates?", then "Okay, so how do you
actually build a 50,000-acre facility?". The host follows the logical thread and pushes back on
each claim before moving forward.

**Relentless** changes topic every **6.2 minutes**. The host covers more ground but at lower
depth per topic. Topics like "Playing Factorio IRL" and "What role suffering plays in greatness"
are explored for 2-5 minutes each, enough to surface an interesting insight but not enough to
fully interrogate it.
""")

st.subheader("3. Title Framing: Thesis vs Story")
st.markdown("""
**Dwarkesh:** *"China is killing the US on energy. Does that mean they'll win AGI?"*
This is a **thesis title**. It makes a provocative claim and promises an answer. The viewer knows
exactly what argument they're about to hear.

**Relentless:** *"#42 - Why Ancient Rome Didn't Industrialize | Casey Handmer, CEO Terraform Industries"*
This is a **curiosity title**. "Why Ancient Rome Didn't Industrialize" is an unexpected angle
that makes you click to find out the connection to a modern energy CEO. The episode number and
guest credentialing follow the standard Relentless formula.
""")

st.subheader("4. Views: 12.2x Difference")
st.markdown("""
Dwarkesh got **12.2x more views** on the same guest (92.9K vs 7.6K). This reflects the channel
size difference (1.26M vs 17.8K subs), but the *engagement rate* tells a different story:
Relentless scored **3.6%** vs Dwarkesh's **2.3%**. The smaller audience engages more intensely.

This pattern is common across podcast tiers: smaller channels trade reach for depth of audience
connection. Relentless viewers are more likely to be founders and engineers who find direct
operational value in the wider-ranging conversation.
""")

st.markdown("---")

# ==================================================================
# SECTION 4: Script Analysis (Relentless only — we have the transcript)
# ==================================================================
st.header("Script Analysis (Relentless Episode)")
st.caption("Based on the auto-generated transcript of the Relentless episode (22,314 words).")

transcript_file = os.path.join(RAW_DIR, "relentless_transcripts.json")
if os.path.exists(transcript_file):
    with open(transcript_file) as f:
        transcripts = json.load(f)

    rel_transcript = transcripts.get("rmmvqkNPo6A", {})
    if rel_transcript:
        text = rel_transcript["text"]
        words = text.lower().split()
        word_count = len(words)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Word Count", f"{word_count:,}")
            st.metric("Words per Minute", f"{word_count / 105:.0f}")

        with col2:
            st.metric("Unique Words", f"{len(set(words)):,}")
            st.metric("Vocabulary Richness", f"{len(set(words))/word_count*100:.1f}%")

        # Tone analysis
        tone_categories = {
            "Action/Build": ["build", "built", "building", "scale", "scaling", "ship", "launch", "deploy", "manufacture"],
            "Technical": ["solar", "energy", "power", "grid", "battery", "industrial", "manufacturing", "infrastructure", "technology", "engineering"],
            "Historical/Philosophical": ["rome", "roman", "history", "civilization", "ancient", "empire", "industrial", "revolution"],
            "Personal/Motivational": ["love", "passion", "suffering", "greatness", "hard", "struggle", "dream", "crazy"],
        }

        tone_rows = []
        for cat, kws in tone_categories.items():
            count = sum(text.lower().count(w) for w in kws)
            per_1k = count / (word_count / 1000)
            tone_rows.append({"Category": cat, "Occurrences": count, "Per 1K Words": round(per_1k, 1)})

        st.dataframe(pd.DataFrame(tone_rows), use_container_width=True, hide_index=True)

        # Key phrases
        stop = {"that","this","with","have","from","they","been","were","what","when","would","could",
            "their","there","about","which","just","like","more","than","them","some","other",
            "into","then","also","these","your","will","know","think","going","really","actually",
            "right","because","people","thing","things","much","very","want","said","make",
            "getting","doing","something","being","yeah","even","kind","time","dont","cant",
            "thats","youre","well","good","come","take","work","back","over"}

        filtered = [w for w in re.findall(r"[a-z]+", text.lower()) if w not in stop and len(w) > 3]
        bigrams = Counter()
        for i in range(len(filtered) - 1):
            bigrams[(filtered[i], filtered[i+1])] += 1

        bg_df = pd.DataFrame(
            [(f"{w1} {w2}", c) for (w1, w2), c in bigrams.most_common(15)],
            columns=["Phrase", "Count"],
        )
        fig = px.bar(bg_df, x="Count", y="Phrase", orientation="h",
                     title="Most Common Phrases in the Relentless Casey Handmer Episode",
                     template="plotly_white", color_discrete_sequence=["#42A5F5"])
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==================================================================
# SECTION 5: Takeaways
# ==================================================================
st.header("What This Comparison Reveals")

st.markdown("""
**1. Same guest, same expertise, completely different value delivered.**
The Dwarkesh episode is an argument about energy and AI. The Relentless episode is a window into
how a deep-tech founder thinks about the world. Both are valuable, but to different audiences.

**2. Tight focus drives views; wide exploration drives engagement.**
Dwarkesh's thesis-driven structure (one topic, 68 min) converts better for YouTube's algorithm:
clear title, clear promise, clear payoff. Relentless's meandering style (16 topics, 105 min)
creates deeper connection with a smaller audience who values the journey.

**3. Segment density is a strategic choice.**
Relentless averaging 6.2 min/segment with 17 timestamps creates a "choose your own adventure"
experience. Dwarkesh's 8.5 min/segment with 8 chapters creates a linear narrative. Both work,
but for different viewer intentions (browsing vs committing).

**4. Title engineering matters enormously.**
"China is killing the US on energy" (Dwarkesh) directly targets the AI/tech audience's anxieties.
"Why Ancient Rome Didn't Industrialize" (Relentless) targets curiosity. The Dwarkesh title is
more searchable and shareable; the Relentless title is more memorable and distinctive.

**5. The 12x view gap is about distribution, not quality.**
Relentless's higher engagement rate (3.6% vs 2.3%) suggests the content quality is comparable.
The view difference is almost entirely explained by Dwarkesh's 70x larger subscriber base (1.26M
vs 17.8K). For a channel Relentless's size, getting 7.6K views on a deep-tech interview is
strong performance.
""")

st.markdown("---")
st.caption("Comparison based on Casey Handmer episodes published Aug 15 (Dwarkesh) and Aug 29 (Relentless), 2025.")
