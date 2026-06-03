import os
import pandas as pd
import streamlit as st

from utils.categorizer import BUCKET_ORDER
from utils.facade import PortfolioFacade

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "data", "portfolio_sample.csv")
REQUIRED_COLUMNS = {"ticker", "name", "sector", "asset_type", "shares", "purchase_price", "current_price"}

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="Portfolio Risk Analyzer", layout="wide", page_icon="📈")

# ── Session state — inputs only ───────────────────────────────────────────────
# Only raw inputs are persisted; PortfolioFacade is derived on every run.

if "raw_df" not in st.session_state:
    st.session_state["raw_df"] = pd.read_csv(SAMPLE_CSV)
    st.session_state["targets"] = None

# ── Sidebar — data management + filters ──────────────────────────────────────

with st.sidebar:
    st.title("📈 Portfolio Risk Analyzer")
    st.divider()

    uploaded = st.file_uploader("Upload your own CSV", type="csv")
    if uploaded:
        try:
            raw = pd.read_csv(uploaded)
            missing = REQUIRED_COLUMNS - set(raw.columns)
            if missing:
                st.error(f"CSV missing columns: {', '.join(sorted(missing))}")
            else:
                st.session_state["raw_df"] = raw
                st.session_state["targets"] = None
                st.success("Portfolio loaded!")
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

    if st.button("Use Sample Portfolio"):
        st.session_state["raw_df"] = pd.read_csv(SAMPLE_CSV)
        st.session_state["targets"] = None

    st.divider()

    # Derive facade once per run from raw inputs
    facade = PortfolioFacade(st.session_state["raw_df"])
    df = facade.portfolio

    bucket_filter = st.multiselect("Filter by Risk Bucket", BUCKET_ORDER, default=BUCKET_ORDER)
    sector_filter = st.multiselect("Filter by Sector", sorted(df["sector"].unique()),
                                   default=sorted(df["sector"].unique()))

filters = {"bucket_filter": bucket_filter, "sector_filter": sector_filter}

# ── Tab navigation ────────────────────────────────────────────────────────────

from views import overview, allocation, rebalancing, sector, gainloss

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Portfolio Overview",
    "Allocation Dashboard",
    "Rebalancing Engine",
    "Sector Breakdown",
    "Gain / Loss",
])

with tab1:
    overview.render(facade, filters=filters)

with tab2:
    updated_targets = allocation.render(facade, targets=st.session_state["targets"])
    if updated_targets is not None:
        st.session_state["targets"] = updated_targets

with tab3:
    rebalancing.render(facade, targets=st.session_state["targets"])

with tab4:
    sector.render(facade)

with tab5:
    gainloss.render(facade, filters=filters)
