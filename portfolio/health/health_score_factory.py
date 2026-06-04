from typing import Dict

import pandas as pd

from portfolio.health.benchmarks import BENCHMARK_REGISTRY
from portfolio.health.health_score import HealthScore


class HealthScoreFactory:
    """Creates HealthScore instances by comparing a portfolio's allocation to predefined benchmarks (Factory pattern)."""

    @staticmethod
    def create(df: pd.DataFrame, benchmark_name: str) -> HealthScore:
        benchmark = BENCHMARK_REGISTRY[benchmark_name]
        total = df["market_value"].sum()
        deviations: Dict[str, float] = {}
        total_deviation = 0.0

        for bucket, target_pct in benchmark.items():
            actual_pct = (
                df.loc[df["risk_bucket"] == bucket, "market_value"].sum() / total * 100
                if total > 0 else 0.0
            )
            dev = actual_pct - target_pct
            deviations[bucket] = dev
            total_deviation += abs(dev)

        # Score = 100 − (sum of absolute deviations / 2), clamped to [0, 100]
        # Dividing by 2 normalises: a perfectly inverse allocation would score 0, not −100
        score = max(0, int(100 - total_deviation / 2))

        if score >= 80:
            label = "Well Aligned"
        elif score >= 60:
            label = "Moderate Drift"
        else:
            label = "Needs Rebalancing"

        return HealthScore(
            benchmark_name=benchmark_name,
            score=score,
            label=label,
            deviations=deviations,
        )

    @staticmethod
    def create_all(df: pd.DataFrame) -> Dict[str, HealthScore]:
        return {name: HealthScoreFactory.create(df, name) for name in BENCHMARK_REGISTRY}
