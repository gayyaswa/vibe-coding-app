import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.categorizer import assign_risk_bucket, BUCKET_ORDER
from utils.rebalancer import bucket_summary, compute_rebalancing, HOLD_THRESHOLD


def _make_portfolio():
    rows = [
        # Less Risk — $10,000 total
        {"ticker": "BIL", "name": "T-Bill", "sector": "Government", "asset_type": "ETF",
         "shares": 100, "purchase_price": 90.0, "current_price": 100.0},
        # Moderate — $5,000 total
        {"ticker": "GLD", "name": "Gold", "sector": "Commodities", "asset_type": "ETF",
         "shares": 50, "purchase_price": 90.0, "current_price": 100.0},
        # Growth — $20,000 total (AAPL $12k + MSFT $8k)
        {"ticker": "AAPL", "name": "Apple", "sector": "Technology", "asset_type": "Stock",
         "shares": 120, "purchase_price": 90.0, "current_price": 100.0},
        {"ticker": "MSFT", "name": "Microsoft", "sector": "Technology", "asset_type": "Stock",
         "shares": 80, "purchase_price": 90.0, "current_price": 100.0},
        # Aggressive — $5,000 total
        {"ticker": "COIN", "name": "Coinbase", "sector": "Financial", "asset_type": "Stock",
         "shares": 50, "purchase_price": 90.0, "current_price": 100.0},
    ]
    raw = pd.DataFrame(rows)
    return assign_risk_bucket(raw)


@pytest.fixture
def portfolio_df():
    return _make_portfolio()


@pytest.fixture
def equal_targets():
    return {"Less Risk": 25.0, "Moderate": 25.0, "Growth": 25.0, "Aggressive": 25.0}


@pytest.fixture
def current_alloc_targets(portfolio_df):
    total = portfolio_df["market_value"].sum()
    return {
        bucket: portfolio_df.loc[portfolio_df["risk_bucket"] == bucket, "market_value"].sum() / total * 100
        for bucket in BUCKET_ORDER
    }


class TestBucketSummary:
    def test_returns_one_row_per_bucket(self, portfolio_df, equal_targets):
        summary = bucket_summary(portfolio_df, equal_targets)
        assert len(summary) == len(BUCKET_ORDER)

    def test_current_pct_sums_to_100(self, portfolio_df, equal_targets):
        summary = bucket_summary(portfolio_df, equal_targets)
        assert summary["current_pct"].sum() == pytest.approx(100.0, abs=0.01)

    def test_delta_is_zero_when_targets_match_current(self, portfolio_df, current_alloc_targets):
        summary = bucket_summary(portfolio_df, current_alloc_targets)
        for _, row in summary.iterrows():
            assert abs(row["delta"]) < 1.0  # rounding tolerance

    def test_delta_positive_when_underweight(self, portfolio_df, equal_targets):
        # Moderate is at ~12.5% but target is 25% → should be positive delta
        summary = bucket_summary(portfolio_df, equal_targets)
        moderate = summary.loc[summary["risk_bucket"] == "Moderate", "delta"].iloc[0]
        assert moderate > 0

    def test_delta_negative_when_overweight(self, portfolio_df, equal_targets):
        # Growth is at 50% but target is 25% → should be negative delta
        summary = bucket_summary(portfolio_df, equal_targets)
        growth = summary.loc[summary["risk_bucket"] == "Growth", "delta"].iloc[0]
        assert growth < 0

    def test_target_values_sum_to_total_portfolio(self, portfolio_df, equal_targets):
        total = portfolio_df["market_value"].sum()
        summary = bucket_summary(portfolio_df, equal_targets)
        assert summary["target_value"].sum() == pytest.approx(total, rel=1e-6)


class TestComputeRebalancing:
    def test_returns_one_row_per_stock(self, portfolio_df, equal_targets):
        result = compute_rebalancing(portfolio_df, equal_targets)
        assert len(result) == len(portfolio_df)

    def test_action_column_only_valid_values(self, portfolio_df, equal_targets):
        result = compute_rebalancing(portfolio_df, equal_targets)
        assert set(result["action"]).issubset({"BUY", "SELL", "HOLD"})

    def test_hold_when_targets_match_current(self, portfolio_df, current_alloc_targets):
        result = compute_rebalancing(portfolio_df, current_alloc_targets)
        # All deltas should be near zero → all HOLD
        for _, row in result.iterrows():
            assert row["action"] == "HOLD"

    def test_buy_action_when_bucket_underweight(self, portfolio_df, equal_targets):
        # Moderate (GLD) is underweight → should BUY
        result = compute_rebalancing(portfolio_df, equal_targets)
        gld = result.loc[result["ticker"] == "GLD"]
        assert gld["action"].iloc[0] == "BUY"
        assert gld["delta"].iloc[0] > 0

    def test_sell_action_when_bucket_overweight(self, portfolio_df, equal_targets):
        # Growth (AAPL, MSFT) is overweight → should SELL
        result = compute_rebalancing(portfolio_df, equal_targets)
        for ticker in ["AAPL", "MSFT"]:
            row = result.loc[result["ticker"] == ticker]
            assert row["action"].iloc[0] == "SELL"
            assert row["delta"].iloc[0] < 0

    def test_hold_threshold_applied(self, portfolio_df):
        # Targets very close to current → deltas below HOLD_THRESHOLD → all HOLD
        total = portfolio_df["market_value"].sum()
        targets = {
            bucket: portfolio_df.loc[portfolio_df["risk_bucket"] == bucket, "market_value"].sum() / total * 100
            for bucket in BUCKET_ORDER
        }
        # Nudge one bucket by a tiny amount (< HOLD_THRESHOLD when distributed)
        result = compute_rebalancing(portfolio_df, targets)
        assert all(result["action"] == "HOLD")

    def test_delta_signs_consistent_with_action(self, portfolio_df, equal_targets):
        result = compute_rebalancing(portfolio_df, equal_targets)
        for _, row in result.iterrows():
            if row["action"] == "BUY":
                assert row["delta"] >= HOLD_THRESHOLD
            elif row["action"] == "SELL":
                assert row["delta"] <= -HOLD_THRESHOLD
            else:
                assert abs(row["delta"]) < HOLD_THRESHOLD

    def test_proportional_distribution_within_bucket(self, portfolio_df, equal_targets):
        result = compute_rebalancing(portfolio_df, equal_targets)
        # AAPL weight in Growth = 120/(120+80)=0.6, MSFT=0.4
        # Their deltas should be in 0.6:0.4 ratio
        aapl_delta = abs(result.loc[result["ticker"] == "AAPL", "delta"].iloc[0])
        msft_delta = abs(result.loc[result["ticker"] == "MSFT", "delta"].iloc[0])
        assert aapl_delta / msft_delta == pytest.approx(1.5, rel=0.01)
