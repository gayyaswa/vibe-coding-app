import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.categorizer import BUCKET_COLORS, BUCKET_ORDER
from utils.facade import PortfolioFacade
from views import apply_theme


def fmt_usd(val: float) -> str:
    return f"${val:,.2f}"


def color_pnl(val):
    color = "green" if val >= 0 else "red"
    return f"color: {color}"


def render(facade: PortfolioFacade, filters: dict, **kwargs) -> None:
    st.header("Gain / Loss Summary")

    df = facade.portfolio
    bucket_filter = filters.get("bucket_filter", list(df["risk_bucket"].unique()))
    sector_filter = filters.get("sector_filter", list(df["sector"].unique()))
    filtered_df = df[df["risk_bucket"].isin(bucket_filter) & df["sector"].isin(sector_filter)]

    sorted_df = filtered_df.sort_values("unrealized_pnl", ascending=True)
    sorted_df["bar_color"] = sorted_df["unrealized_pnl"].apply(lambda v: "#4CAF50" if v >= 0 else "#F44336")

    st.subheader("Unrealized P&L by Ticker")
    pnl_bar = go.Figure(go.Bar(
        x=sorted_df["unrealized_pnl"],
        y=sorted_df["ticker"],
        orientation="h",
        marker_color=sorted_df["bar_color"],
        text=sorted_df["unrealized_pnl"].apply(fmt_usd),
        textposition="outside",
    ))
    pnl_bar.update_layout(xaxis_title="Unrealized P&L ($)", yaxis_title="Ticker", height=520)
    apply_theme(pnl_bar)
    st.plotly_chart(pnl_bar, use_container_width=True)

    st.divider()

    display_cols = ["ticker", "name", "risk_bucket", "cost_basis", "market_value", "unrealized_pnl", "pnl_pct"]
    table_df = filtered_df[display_cols].sort_values("pnl_pct", ascending=False)
    styled_gl = (
        table_df.style
        .format({"cost_basis": "${:,.2f}", "market_value": "${:,.2f}",
                 "unrealized_pnl": "${:,.2f}", "pnl_pct": "{:.1f}%"})
        .applymap(color_pnl, subset=["unrealized_pnl", "pnl_pct"])
    )
    st.dataframe(styled_gl, use_container_width=True)

    st.subheader("Cost Basis vs Market Value by Risk Bucket")
    bucket_gl = df.groupby("risk_bucket", as_index=False).agg(
        cost_basis=("cost_basis", "sum"),
        market_value=("market_value", "sum"),
    )
    bucket_gl["risk_bucket"] = pd.Categorical(bucket_gl["risk_bucket"], categories=BUCKET_ORDER, ordered=True)
    bucket_gl = bucket_gl.sort_values("risk_bucket")

    bucket_bar = go.Figure()
    bucket_bar.add_trace(go.Bar(
        name="Cost Basis", x=bucket_gl["risk_bucket"], y=bucket_gl["cost_basis"],
        marker_color=[BUCKET_COLORS.get(b, "#999") for b in bucket_gl["risk_bucket"]], opacity=0.6,
    ))
    bucket_bar.add_trace(go.Bar(
        name="Market Value", x=bucket_gl["risk_bucket"], y=bucket_gl["market_value"],
        marker_color=[BUCKET_COLORS.get(b, "#999") for b in bucket_gl["risk_bucket"]],
    ))
    bucket_bar.update_layout(barmode="group", yaxis_title="Value ($)", xaxis_title="Risk Bucket")
    apply_theme(bucket_bar)
    st.plotly_chart(bucket_bar, use_container_width=True)
