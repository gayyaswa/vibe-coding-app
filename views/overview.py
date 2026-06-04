import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.categorizer import BUCKET_COLORS
from utils.facade import PortfolioFacade
from views import apply_theme


def fmt_usd(val: float) -> str:
    return f"${val:,.2f}"


def color_pnl(val):
    color = "green" if val >= 0 else "red"
    return f"color: {color}"


def render(facade: PortfolioFacade, filters: dict) -> None:
    st.header("Portfolio Overview")

    df = facade.portfolio
    bucket_filter = filters.get("bucket_filter", list(df["risk_bucket"].unique()))
    sector_filter = filters.get("sector_filter", list(df["sector"].unique()))

    total_value = df["market_value"].sum()
    total_cost = df["cost_basis"].sum()
    total_pnl = df["unrealized_pnl"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Market Value", fmt_usd(total_value))
    c2.metric("Total Cost Basis", fmt_usd(total_cost))
    c3.metric("Total Unrealized P&L", fmt_usd(total_pnl), delta=f"{total_pnl / total_cost * 100:.1f}%")

    st.divider()

    # ── Sunburst — dominant view ──────────────────────────────────────────────
    st.subheader("Portfolio Composition")
    sunburst_fig = px.sunburst(
        df,
        path=[px.Constant("Portfolio"), "risk_bucket", "ticker"],
        values="market_value",
        color="risk_bucket",
        color_discrete_map=BUCKET_COLORS,
        custom_data=["name", "unrealized_pnl", "pnl_pct"],
    )
    sunburst_fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "%{customdata[0]}<br>"
            "Value: $%{value:,.0f}<br>"
            "P&L: $%{customdata[1]:,.0f} (%{customdata[2]:.1f}%)"
            "<extra></extra>"
        ),
        textfont=dict(size=13),
    )
    sunburst_fig.update_layout(margin=dict(t=30, l=0, r=0, b=0), height=520)
    apply_theme(sunburst_fig)
    st.plotly_chart(sunburst_fig, use_container_width=True)

    # ── Health Score cards ────────────────────────────────────────────────────
    st.subheader("Portfolio Health vs Benchmarks")
    scores = facade.health_scores()
    cols = st.columns(3)
    label_colors = {"Well Aligned": "✅", "Moderate Drift": "⚠️", "Needs Rebalancing": "🔴"}

    for col, (name, hs) in zip(cols, scores.items()):
        with col:
            st.metric(
                label=f"{label_colors.get(hs.label, '')} {name}",
                value=f"{hs.score} / 100",
                delta=hs.label,
            )
            for bucket, dev in hs.deviations.items():
                sign = "+" if dev >= 0 else ""
                st.caption(f"{bucket}: {sign}{dev:.1f}%")

    # ── Holdings Detail ───────────────────────────────────────────────────────
    st.divider()
    filtered_df = df[df["risk_bucket"].isin(bucket_filter) & df["sector"].isin(sector_filter)]

    with st.expander("Holdings Detail", expanded=False):
        display_cols = [
            "ticker", "name", "sector", "risk_bucket", "asset_type",
            "shares", "purchase_price", "current_price",
            "market_value", "unrealized_pnl", "pnl_pct",
        ]
        styled = (
            filtered_df[display_cols].style
            .format({
                "purchase_price": "${:.2f}", "current_price": "${:.2f}",
                "market_value": "${:,.2f}", "unrealized_pnl": "${:,.2f}", "pnl_pct": "{:.1f}%",
            })
            .applymap(color_pnl, subset=["unrealized_pnl", "pnl_pct"])
        )
        st.dataframe(styled, use_container_width=True, height=400)
