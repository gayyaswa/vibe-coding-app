from typing import Optional

import plotly.graph_objects as go
import streamlit as st

from portfolio.facade import PortfolioFacade
from views import apply_theme


def fmt_usd(val: float) -> str:
    return f"${val:,.2f}"


def style_action(val):
    colors = {"BUY": "background-color: #c8f0c8", "SELL": "background-color: #f0c8c8"}
    return colors.get(val, "")


def render(facade: PortfolioFacade, targets: Optional[dict], **kwargs) -> None:
    st.header("Rebalancing Engine")

    if not targets:
        st.info("Set and confirm target allocations in the Allocation Dashboard first.")
        return

    df = facade.portfolio
    rebal_df = facade.compute_rebalancing(targets)
    total_value = df["market_value"].sum()
    total_buy = rebal_df.loc[rebal_df["action"] == "BUY", "delta"].sum()
    total_sell = abs(rebal_df.loc[rebal_df["action"] == "SELL", "delta"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Portfolio Value", fmt_usd(total_value))
    c2.metric("Total to BUY", fmt_usd(total_buy))
    c3.metric("Total to SELL", fmt_usd(total_sell))

    st.divider()

    display_cols = ["ticker", "name", "risk_bucket", "current_value", "target_value", "delta", "action"]
    styled_rebal = (
        rebal_df[display_cols].style
        .format({"current_value": "${:,.2f}", "target_value": "${:,.2f}", "delta": "${:,.2f}"})
        .applymap(style_action, subset=["action"])
    )
    st.dataframe(styled_rebal, use_container_width=True, height=480)

    st.subheader("Delta by Ticker")
    rebal_df["color"] = rebal_df["action"].map({"BUY": "#4CAF50", "SELL": "#F44336", "HOLD": "#9E9E9E"})
    bar_fig = go.Figure(go.Bar(
        x=rebal_df["delta"],
        y=rebal_df["ticker"],
        orientation="h",
        marker_color=rebal_df["color"],
        text=rebal_df["action"],
        textposition="outside",
    ))
    bar_fig.update_layout(xaxis_title="Delta ($)", yaxis_title="Ticker", height=500)
    apply_theme(bar_fig)
    st.plotly_chart(bar_fig, use_container_width=True)
