from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.categorizer import BUCKET_COLORS, BUCKET_ORDER
from utils.facade import PortfolioFacade
from views import apply_theme


def render(facade: PortfolioFacade, targets: Optional[dict], **kwargs) -> Optional[dict]:
    """Returns updated targets if user confirms, otherwise returns None."""
    st.header("Allocation Dashboard")

    df = facade.portfolio
    total_value = df["market_value"].sum()
    current_pcts = {
        b: df.loc[df["risk_bucket"] == b, "market_value"].sum() / total_value * 100
        for b in BUCKET_ORDER
    }

    col_pie, col_sliders = st.columns([1, 1])

    with col_pie:
        st.subheader("Current Allocation")
        pie_data = pd.DataFrame({
            "Bucket": BUCKET_ORDER,
            "Value": [df.loc[df["risk_bucket"] == b, "market_value"].sum() for b in BUCKET_ORDER],
        })
        fig_pie = px.pie(
            pie_data, values="Value", names="Bucket",
            color="Bucket", color_discrete_map=BUCKET_COLORS,
            hole=0.4,
        )
        fig_pie.update_traces(textinfo="percent+label")
        apply_theme(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_sliders:
        st.subheader("Set Target Allocation (%)")
        saved = targets or {}
        sliders = {}
        for bucket in BUCKET_ORDER:
            default = int(round(saved.get(bucket, current_pcts[bucket])))
            sliders[bucket] = st.slider(
                bucket, min_value=0, max_value=100, value=default, step=1,
                key=f"slider_{bucket}",
            )
            delta = sliders[bucket] - current_pcts[bucket]
            if abs(delta) >= 0.5:
                icon, color = ("▲", "#1565C0") if delta > 0 else ("▼", "#F44336")
                st.markdown(
                    f"<span style='font-weight:700;font-size:13px;color:{color}'>"
                    f"{icon} {delta:+.1f}% from current ({current_pcts[bucket]:.1f}%)"
                    f"</span>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<span style='font-size:12px;color:#888'>● At current allocation "
                    f"({current_pcts[bucket]:.1f}%)</span>",
                    unsafe_allow_html=True,
                )

        total_slider = sum(sliders.values())
        if total_slider != 100:
            st.warning(f"Allocations sum to {total_slider}% — must equal 100% to confirm.")
            confirm_disabled = True
        else:
            st.success("Allocations sum to 100% ✓")
            confirm_disabled = False

        if st.button("Confirm Targets", disabled=confirm_disabled):
            targets = {b: float(v) for b, v in sliders.items()}
            st.success("Targets saved! Go to Rebalancing Engine to see actions.")
            return targets

    if not confirm_disabled:
        st.divider()
        st.subheader("Current vs Target Allocation")
        summary = facade.bucket_summary({b: float(v) for b, v in sliders.items()})
        bar_fig = go.Figure()
        bar_fig.add_trace(go.Bar(
            name="Current %", x=summary["risk_bucket"], y=summary["current_pct"],
            marker_color=[BUCKET_COLORS[b] for b in summary["risk_bucket"]],
            opacity=0.6,
        ))
        bar_fig.add_trace(go.Bar(
            name="Target %", x=summary["risk_bucket"], y=summary["target_pct"],
            marker_color=[BUCKET_COLORS[b] for b in summary["risk_bucket"]],
            marker_pattern_shape="x",
        ))
        bar_fig.update_layout(barmode="group", yaxis_title="Allocation %", xaxis_title="Risk Bucket")
        apply_theme(bar_fig)
        st.plotly_chart(bar_fig, use_container_width=True)

    return targets
