import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.categorizer import assign_risk_bucket, BUCKET_ORDER, BUCKET_COLORS


def _make_row(ticker, sector, shares=10, purchase_price=100.0, current_price=110.0):
    return {
        "ticker": ticker,
        "name": ticker,
        "sector": sector,
        "asset_type": "Stock",
        "shares": shares,
        "purchase_price": purchase_price,
        "current_price": current_price,
    }


@pytest.fixture
def sample_df():
    rows = [
        _make_row("BIL", "Government"),
        _make_row("JNJ", "Healthcare"),
        _make_row("GLD", "Commodities"),
        _make_row("WMT", "Retail"),
        _make_row("AAPL", "Technology"),
        _make_row("MSTR", "Technology"),
        _make_row("EEM", "Emerging Markets"),
        _make_row("UNKNOWN", "Unknown Sector"),
    ]
    return pd.DataFrame(rows)


class TestBucketAssignment:
    def test_ticker_override_beats_sector(self, sample_df):
        df = assign_risk_bucket(sample_df)
        # JNJ sector is Healthcare which has no sector rule → should be "Less Risk" via ticker override
        assert df.loc[df.ticker == "JNJ", "risk_bucket"].iloc[0] == "Less Risk"

    def test_government_sector_is_less_risk(self, sample_df):
        df = assign_risk_bucket(sample_df)
        assert df.loc[df.ticker == "BIL", "risk_bucket"].iloc[0] == "Less Risk"

    def test_commodities_sector_is_moderate(self, sample_df):
        df = assign_risk_bucket(sample_df)
        assert df.loc[df.ticker == "GLD", "risk_bucket"].iloc[0] == "Moderate"

    def test_retail_sector_is_moderate(self, sample_df):
        df = assign_risk_bucket(sample_df)
        assert df.loc[df.ticker == "WMT", "risk_bucket"].iloc[0] == "Moderate"

    def test_technology_ticker_override_growth(self, sample_df):
        df = assign_risk_bucket(sample_df)
        assert df.loc[df.ticker == "AAPL", "risk_bucket"].iloc[0] == "Growth"

    def test_mstr_aggressive_overrides_technology_sector(self, sample_df):
        # MSTR sector is Technology (Growth by sector rule), but ticker override → Aggressive
        df = assign_risk_bucket(sample_df)
        assert df.loc[df.ticker == "MSTR", "risk_bucket"].iloc[0] == "Aggressive"

    def test_emerging_markets_sector_is_aggressive(self, sample_df):
        df = assign_risk_bucket(sample_df)
        assert df.loc[df.ticker == "EEM", "risk_bucket"].iloc[0] == "Aggressive"

    def test_unknown_ticker_and_sector_is_uncategorized(self, sample_df):
        df = assign_risk_bucket(sample_df)
        assert df.loc[df.ticker == "UNKNOWN", "risk_bucket"].iloc[0] == "Uncategorized"


class TestDerivedColumns:
    def test_market_value_computed(self, sample_df):
        df = assign_risk_bucket(sample_df)
        row = df.iloc[0]
        assert row["market_value"] == pytest.approx(row["shares"] * row["current_price"])

    def test_cost_basis_computed(self, sample_df):
        df = assign_risk_bucket(sample_df)
        row = df.iloc[0]
        assert row["cost_basis"] == pytest.approx(row["shares"] * row["purchase_price"])

    def test_unrealized_pnl_computed(self, sample_df):
        df = assign_risk_bucket(sample_df)
        row = df.iloc[0]
        assert row["unrealized_pnl"] == pytest.approx(row["market_value"] - row["cost_basis"])

    def test_pnl_pct_computed(self, sample_df):
        df = assign_risk_bucket(sample_df)
        row = df.iloc[0]
        expected_pct = (row["unrealized_pnl"] / row["cost_basis"]) * 100
        assert row["pnl_pct"] == pytest.approx(expected_pct)

    def test_does_not_mutate_input(self, sample_df):
        original_cols = list(sample_df.columns)
        assign_risk_bucket(sample_df)
        assert list(sample_df.columns) == original_cols


class TestConstants:
    def test_bucket_order_has_four_buckets(self):
        assert len(BUCKET_ORDER) == 4

    def test_bucket_colors_covers_all_buckets(self):
        for bucket in BUCKET_ORDER:
            assert bucket in BUCKET_COLORS

    def test_bucket_colors_are_hex(self):
        for color in BUCKET_COLORS.values():
            assert color.startswith("#") and len(color) == 7
