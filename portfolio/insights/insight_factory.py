from typing import Dict, Type

from portfolio.insights.insight_strategy import InsightStrategy
from portfolio.insights.rebalancing_rationale_insight import RebalancingRationaleInsight
from portfolio.insights.sector_concentration_insight import SectorConcentrationInsight

INSIGHT_REGISTRY: Dict[str, Type[InsightStrategy]] = {
    "rebalancing_rationale": RebalancingRationaleInsight,
    "sector_concentration": SectorConcentrationInsight,
}


class InsightFactory:
    """Creates InsightStrategy instances by type key using INSIGHT_REGISTRY (Factory + Registry pattern)."""

    @staticmethod
    def create(insight_type: str, llm) -> InsightStrategy:
        cls = INSIGHT_REGISTRY.get(insight_type)
        if cls is None:
            raise ValueError(f"Unknown insight type: {insight_type!r}")
        return cls(llm)
