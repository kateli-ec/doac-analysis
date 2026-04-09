"""The Diary of a CEO — YouTube Channel Analysis (Public Dashboard)."""

import streamlit as st

st.set_page_config(
    page_title="DOAC YouTube Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("The Diary of a CEO — YouTube Channel Analysis")
st.markdown(
    "Comprehensive analysis of [@TheDiaryOfACEO](https://www.youtube.com/@TheDiaryOfACEO) "
    "growth, content strategy, and audience insights."
)
st.markdown("---")
st.markdown("Select a page from the sidebar to explore the analysis.")
st.markdown("---")
st.caption("Data snapshot collected via YouTube Data API v3 on April 8, 2026. Dashboard built with Streamlit.")
