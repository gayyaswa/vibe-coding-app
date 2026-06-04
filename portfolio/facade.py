from typing import Dict

import pandas as pd

from portfolio.classification import assign_risk_bucket
from portfolio.health import HealthScoreFactory, HealthScore
from portfolio.pipeline import PortfolioPipeline
from portfolio.rebalancing import bucket_summary, compute_rebalancing


class PortfolioFacade:
    """Single entry point for all views (Facade pattern); wraps classification, rebalancing, health, and insights subsystems."""

    def __init__(self, raw_df: pd.DataFrame):
        pipeline = PortfolioPipeline([assign_risk_bucket])
        self._df = pipeline.run(raw_df)

    @classmethod
    def from_csv(cls, path: str) -> "PortfolioFacade":
        return cls(pd.read_csv(path))

    @property
    def portfolio(self) -> pd.DataFrame:
        return self._df

    def bucket_summary(self, targets: dict) -> pd.DataFrame:
        return bucket_summary(self._df, targets)

    def compute_rebalancing(self, targets: dict) -> pd.DataFrame:
        return compute_rebalancing(self._df, targets)

    def health_scores(self) -> Dict[str, HealthScore]:
        return HealthScoreFactory.create_all(self._df)
