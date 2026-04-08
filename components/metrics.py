"""Reusable metric card components."""

import streamlit as st


def metric_row(metrics: list[dict]):
    """Display a row of metric cards."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        col.metric(label=m["label"], value=m["value"], delta=m.get("delta"))


def format_number(n: float | int) -> str:
    """Format large numbers with K/M/B suffixes."""
    if n is None:
        return "N/A"
    if abs(n) >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{n:,.0f}"


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    if seconds is None or seconds == 0:
        return "N/A"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
