import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio.classification import BUCKET_COLORS, BUCKET_ORDER
from portfolio.facade import PortfolioFacade
from views import apply_theme


def render(facade: PortfolioFacade, **kwargs) -> None:
    st.header("Sector Breakdown")

    df = facade.portfolio
    sector_df = df.groupby(["sector", "risk_bucket"], as_index=False)["market_value"].sum()
    sector_df["risk_bucket"] = pd.Categorical(sector_df["risk_bucket"], categories=BUCKET_ORDER, ordered=True)
    sector_df = sector_df.sort_values("risk_bucket")

    bar_fig = px.bar(
        sector_df, x="sector", y="market_value", color="risk_bucket",
        color_discrete_map=BUCKET_COLORS, barmode="group",
        labels={"market_value": "Market Value ($)", "sector": "Sector", "risk_bucket": "Risk Bucket"},
    )
    bar_fig.update_layout(xaxis_tickangle=-30)
    apply_theme(bar_fig)
    st.plotly_chart(bar_fig, use_container_width=True)

    st.subheader("Concentration Heatmap (Sector × Risk Bucket)")
    pivot = df.pivot_table(index="sector", columns="risk_bucket", values="market_value",
                           aggfunc="sum", fill_value=0)
    pivot = pivot.reindex(columns=[b for b in BUCKET_ORDER if b in pivot.columns])
    heatmap_fig = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        labels={"color": "Market Value ($)"},
        aspect="auto",
        text_auto=".0f",
    )
    heatmap_fig.update_layout(xaxis_title="Risk Bucket", yaxis_title="Sector")
    apply_theme(heatmap_fig)
    st.plotly_chart(heatmap_fig, use_container_width=True)
