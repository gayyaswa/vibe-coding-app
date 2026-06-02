import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.categorizer import assign_risk_bucket, BUCKET_ORDER, BUCKET_COLORS
from utils.rebalancer import bucket_summary, compute_rebalancing

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "data", "portfolio_sample.csv")
REQUIRED_COLUMNS = {"ticker", "name", "sector", "asset_type", "shares", "purchase_price", "current_price"}


# ── helpers ──────────────────────────────────────────────────────────────────

def load_sample() -> pd.DataFrame:
    return assign_risk_bucket(pd.read_csv(SAMPLE_CSV))


def fmt_usd(val: float) -> str:
    return f"${val:,.2f}"


def color_pnl(val):
    color = "green" if val >= 0 else "red"
    return f"color: {color}"


def style_action(val):
    colors = {"BUY": "background-color: #c8f0c8", "SELL": "background-color: #f0c8c8"}
    return colors.get(val, "")


# ── sidebar ──────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Portfolio Risk Analyzer", layout="wide", page_icon="📈")

with st.sidebar:
    st.title("📈 Portfolio Risk Analyzer")
    section = st.radio(
        "Navigate",
        ["Portfolio Overview", "Allocation Dashboard", "Rebalancing Engine", "Sector Breakdown", "Gain/Loss Summary"],
    )
    st.divider()

    # Data load
    if "df" not in st.session_state:
        st.session_state["df"] = load_sample()
        st.session_state["targets"] = None

    uploaded = st.file_uploader("Upload your own CSV", type="csv")
    if uploaded:
        try:
            raw = pd.read_csv(uploaded)
            missing = REQUIRED_COLUMNS - set(raw.columns)
            if missing:
                st.error(f"CSV missing columns: {', '.join(sorted(missing))}")
            else:
                st.session_state["df"] = assign_risk_bucket(raw)
                st.session_state["targets"] = None
                st.success("Portfolio loaded!")
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

    if st.button("Use Sample Portfolio"):
        st.session_state["df"] = load_sample()
        st.session_state["targets"] = None

    st.divider()

    # Global filters (applied in Overview and Gain/Loss)
    df_all = st.session_state["df"]
    bucket_filter = st.multiselect("Filter by Risk Bucket", BUCKET_ORDER, default=BUCKET_ORDER)
    sector_filter = st.multiselect("Filter by Sector", sorted(df_all["sector"].unique()),
                                   default=sorted(df_all["sector"].unique()))

df = st.session_state["df"]
filtered_df = df[df["risk_bucket"].isin(bucket_filter) & df["sector"].isin(sector_filter)]


# ── section 1: Portfolio Overview ─────────────────────────────────────────────

if section == "Portfolio Overview":
    st.header("Portfolio Overview")

    total_value = df["market_value"].sum()
    total_cost = df["cost_basis"].sum()
    total_pnl = df["unrealized_pnl"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Market Value", fmt_usd(total_value))
    c2.metric("Total Cost Basis", fmt_usd(total_cost))
    c3.metric("Total Unrealized P&L", fmt_usd(total_pnl), delta=f"{total_pnl / total_cost * 100:.1f}%")

    st.divider()

    display_cols = ["ticker", "name", "sector", "risk_bucket", "asset_type", "shares",
                    "purchase_price", "current_price", "market_value", "unrealized_pnl", "pnl_pct"]
    display_df = filtered_df[display_cols].copy()

    styled = (
        display_df.style
        .format({
            "purchase_price": "${:.2f}", "current_price": "${:.2f}",
            "market_value": "${:,.2f}", "unrealized_pnl": "${:,.2f}", "pnl_pct": "{:.1f}%",
        })
        .applymap(color_pnl, subset=["unrealized_pnl", "pnl_pct"])
    )
    st.dataframe(styled, use_container_width=True, height=500)


# ── section 2: Allocation Dashboard ──────────────────────────────────────────

elif section == "Allocation Dashboard":
    st.header("Allocation Dashboard")

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
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_sliders:
        st.subheader("Set Target Allocation (%)")
        saved = st.session_state.get("targets") or {}
        sliders = {}
        for bucket in BUCKET_ORDER:
            default = int(round(saved.get(bucket, current_pcts[bucket])))
            sliders[bucket] = st.slider(
                bucket, min_value=0, max_value=100, value=default, step=1,
                key=f"slider_{bucket}",
            )

        total_slider = sum(sliders.values())
        if total_slider != 100:
            st.warning(f"Allocations sum to {total_slider}% — must equal 100% to confirm.")
            confirm_disabled = True
        else:
            st.success("Allocations sum to 100% ✓")
            confirm_disabled = False

        if st.button("Confirm Targets", disabled=confirm_disabled):
            st.session_state["targets"] = {b: float(v) for b, v in sliders.items()}
            st.success("Targets saved! Go to Rebalancing Engine to see actions.")

    if not confirm_disabled:
        st.divider()
        st.subheader("Current vs Target Allocation")
        summary = bucket_summary(df, {b: float(v) for b, v in sliders.items()})
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
        st.plotly_chart(bar_fig, use_container_width=True)


# ── section 3: Rebalancing Engine ─────────────────────────────────────────────

elif section == "Rebalancing Engine":
    st.header("Rebalancing Engine")

    targets = st.session_state.get("targets")
    if not targets:
        st.info("Set and confirm target allocations in the Allocation Dashboard first.")
    else:
        rebal_df = compute_rebalancing(df, targets)
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
        st.plotly_chart(bar_fig, use_container_width=True)


# ── section 4: Sector Breakdown ──────────────────────────────────────────────

elif section == "Sector Breakdown":
    st.header("Sector Breakdown")

    sector_df = df.groupby(["sector", "risk_bucket"], as_index=False)["market_value"].sum()
    sector_df["risk_bucket"] = pd.Categorical(sector_df["risk_bucket"], categories=BUCKET_ORDER, ordered=True)
    sector_df = sector_df.sort_values("risk_bucket")

    bar_fig = px.bar(
        sector_df, x="sector", y="market_value", color="risk_bucket",
        color_discrete_map=BUCKET_COLORS, barmode="group",
        labels={"market_value": "Market Value ($)", "sector": "Sector", "risk_bucket": "Risk Bucket"},
    )
    bar_fig.update_layout(xaxis_tickangle=-30)
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
    st.plotly_chart(heatmap_fig, use_container_width=True)


# ── section 5: Gain/Loss Summary ─────────────────────────────────────────────

elif section == "Gain/Loss Summary":
    st.header("Gain / Loss Summary")

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
    st.plotly_chart(bucket_bar, use_container_width=True)
