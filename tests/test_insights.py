from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from utils.insights import (
    INSIGHT_REGISTRY,
    InsightFactory,
    InsightsFacade,
    RebalancingRationaleInsight,
    SectorConcentrationInsight,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {"ticker": "AAPL", "name": "Apple", "sector": "Technology", "risk_bucket": "Growth",
         "market_value": 10000, "unrealized_pnl": 1000, "pnl_pct": 11.0},
        {"ticker": "GLD", "name": "Gold ETF", "sector": "Commodities", "risk_bucket": "Moderate",
         "market_value": 5000, "unrealized_pnl": 200, "pnl_pct": 4.2},
        {"ticker": "BIL", "name": "T-Bill ETF", "sector": "Government", "risk_bucket": "Less Risk",
         "market_value": 3000, "unrealized_pnl": 50, "pnl_pct": 1.7},
    ])


@pytest.fixture
def sample_rebal_df():
    return pd.DataFrame([
        {"ticker": "AAPL", "risk_bucket": "Growth", "action": "SELL", "delta": -2000},
        {"ticker": "GLD",  "risk_bucket": "Moderate", "action": "HOLD", "delta": 10},
        {"ticker": "BIL",  "risk_bucket": "Less Risk", "action": "BUY", "delta": 1500},
    ])


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.__or__ = MagicMock(return_value=MagicMock())
    return llm


def test_factory_dispatch():
    mock_llm = MagicMock()
    with patch.object(RebalancingRationaleInsight, "__init__", return_value=None):
        strategy = InsightFactory.create("rebalancing_rationale", mock_llm)
    assert isinstance(strategy, RebalancingRationaleInsight)

    with patch.object(SectorConcentrationInsight, "__init__", return_value=None):
        strategy = InsightFactory.create("sector_concentration", mock_llm)
    assert isinstance(strategy, SectorConcentrationInsight)


def test_factory_unknown_type():
    with pytest.raises(ValueError, match="Unknown insight type"):
        InsightFactory.create("nonexistent_type", MagicMock())


def test_rebalancing_context_contains_actions(sample_df, sample_rebal_df):
    mock_llm = MagicMock()
    with patch("utils.insights.RebalancingRationaleInsight.__init__", return_value=None):
        strategy = RebalancingRationaleInsight.__new__(RebalancingRationaleInsight)
    targets = {"Growth": 35.0, "Moderate": 30.0, "Less Risk": 25.0, "Aggressive": 10.0}
    context = strategy.build_context(sample_df, sample_rebal_df, targets)
    assert "SELL" in context
    assert "BUY" in context
    assert "AAPL" in context
    assert "BIL" in context


def test_sector_context_contains_sectors(sample_df):
    mock_llm = MagicMock()
    with patch("utils.insights.SectorConcentrationInsight.__init__", return_value=None):
        strategy = SectorConcentrationInsight.__new__(SectorConcentrationInsight)
    context = strategy.build_context(sample_df, None, None)
    assert "Technology" in context
    assert "Commodities" in context
    assert "Government" in context
    assert "AAPL" in context


def test_missing_targets_raises(sample_df):
    with patch("utils.insights.RebalancingRationaleInsight.__init__", return_value=None):
        strategy = RebalancingRationaleInsight.__new__(RebalancingRationaleInsight)
    with pytest.raises(ValueError, match="Targets must be set"):
        strategy.build_context(sample_df, None, None)


def test_insight_registry_completeness():
    assert "rebalancing_rationale" in INSIGHT_REGISTRY
    assert "sector_concentration" in INSIGHT_REGISTRY
    assert len(INSIGHT_REGISTRY) == 2
