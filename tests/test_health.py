import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from portfolio.classification import assign_risk_bucket
from portfolio.health import BENCHMARK_REGISTRY, HealthScore, HealthScoreFactory


def _make_portfolio(less_risk=10000, moderate=5000, growth=20000, aggressive=5000):
    rows = [
        {"ticker": "BIL",  "name": "T-Bill",    "sector": "Government",  "asset_type": "ETF",
         "shares": less_risk // 100, "purchase_price": 90.0, "current_price": 100.0},
        {"ticker": "GLD",  "name": "Gold",       "sector": "Commodities", "asset_type": "ETF",
         "shares": moderate // 100, "purchase_price": 90.0, "current_price": 100.0},
        {"ticker": "AAPL", "name": "Apple",      "sector": "Technology",  "asset_type": "Stock",
         "shares": growth // 100,   "purchase_price": 90.0, "current_price": 100.0},
        {"ticker": "COIN", "name": "Coinbase",   "sector": "Financial",   "asset_type": "Stock",
         "shares": aggressive // 100, "purchase_price": 90.0, "current_price": 100.0},
    ]
    return assign_risk_bucket(pd.DataFrame(rows))


@pytest.fixture
def portfolio_df():
    return _make_portfolio()


class TestBenchmarkRegistry:
    def test_registry_has_three_benchmarks(self):
        assert len(BENCHMARK_REGISTRY) == 3

    def test_each_benchmark_sums_to_100(self):
        for name, alloc in BENCHMARK_REGISTRY.items():
            assert sum(alloc.values()) == 100, f"{name} does not sum to 100"

    def test_registry_covers_all_buckets(self):
        buckets = {"Less Risk", "Moderate", "Growth", "Aggressive"}
        for alloc in BENCHMARK_REGISTRY.values():
            assert set(alloc.keys()) == buckets


class TestHealthScoreFactory:
    def test_returns_health_score_instance(self, portfolio_df):
        hs = HealthScoreFactory.create(portfolio_df, "Balanced")
        assert isinstance(hs, HealthScore)

    def test_score_is_100_when_perfectly_aligned(self):
        # Balanced: 25% / 25% / 35% / 15% — use exact share counts at $1 so proportions are exact
        rows = [
            {"ticker": "BIL",  "name": "T-Bill",  "sector": "Government",  "asset_type": "ETF",
             "shares": 25, "purchase_price": 1.0, "current_price": 1.0},
            {"ticker": "GLD",  "name": "Gold",    "sector": "Commodities", "asset_type": "ETF",
             "shares": 25, "purchase_price": 1.0, "current_price": 1.0},
            {"ticker": "AAPL", "name": "Apple",   "sector": "Technology",  "asset_type": "Stock",
             "shares": 35, "purchase_price": 1.0, "current_price": 1.0},
            {"ticker": "COIN", "name": "Coinbase","sector": "Financial",   "asset_type": "Stock",
             "shares": 15, "purchase_price": 1.0, "current_price": 1.0},
        ]
        df = assign_risk_bucket(pd.DataFrame(rows))
        hs = HealthScoreFactory.create(df, "Balanced")
        assert hs.score == 100

    def test_score_is_between_0_and_100(self, portfolio_df):
        for name in BENCHMARK_REGISTRY:
            hs = HealthScoreFactory.create(portfolio_df, name)
            assert 0 <= hs.score <= 100

    def test_label_well_aligned_at_high_score(self, portfolio_df):
        benchmark = BENCHMARK_REGISTRY["Aggressive Growth"]
        hs = HealthScoreFactory.create(portfolio_df, "Aggressive Growth")
        if hs.score >= 80:
            assert hs.label == "Well Aligned"

    def test_label_thresholds(self):
        for name in BENCHMARK_REGISTRY:
            hs = HealthScoreFactory.create(_make_portfolio(), name)
            if hs.score >= 80:
                assert hs.label == "Well Aligned"
            elif hs.score >= 60:
                assert hs.label == "Moderate Drift"
            else:
                assert hs.label == "Needs Rebalancing"

    def test_deviations_have_all_buckets(self, portfolio_df):
        hs = HealthScoreFactory.create(portfolio_df, "Balanced")
        assert set(hs.deviations.keys()) == {"Less Risk", "Moderate", "Growth", "Aggressive"}

    def test_deviation_sign_positive_when_overweight(self):
        # Portfolio is heavily Growth (50%) vs Conservative target (15%)
        df = _make_portfolio(less_risk=5000, moderate=5000, growth=20000, aggressive=10000)
        hs = HealthScoreFactory.create(df, "Conservative")
        assert hs.deviations["Growth"] > 0

    def test_deviation_sign_negative_when_underweight(self):
        # Less Risk is 12.5% vs Conservative target 50%
        df = _make_portfolio(less_risk=5000, moderate=5000, growth=20000, aggressive=10000)
        hs = HealthScoreFactory.create(df, "Conservative")
        assert hs.deviations["Less Risk"] < 0

    def test_create_all_returns_all_benchmarks(self, portfolio_df):
        scores = HealthScoreFactory.create_all(portfolio_df)
        assert set(scores.keys()) == set(BENCHMARK_REGISTRY.keys())
        for hs in scores.values():
            assert isinstance(hs, HealthScore)
