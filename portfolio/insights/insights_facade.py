from __future__ import annotations

from typing import Generator, Optional

from portfolio.insights.insight_factory import InsightFactory


class InsightsFacade:
    """Orchestrates LangChain-based AI insights; coordinates PortfolioFacade with the insight strategy pipeline (Facade pattern)."""

    def __init__(self, portfolio_facade, targets: Optional[dict], llm) -> None:
        self._facade = portfolio_facade
        self._targets = targets
        self._llm = llm

    def stream_insight(self, insight_type: str) -> Generator:
        rebal_df = self._facade.compute_rebalancing(self._targets) if self._targets else None
        strategy = InsightFactory.create(insight_type, self._llm)
        yield from strategy.stream(self._facade.portfolio, rebal_df, self._targets)
