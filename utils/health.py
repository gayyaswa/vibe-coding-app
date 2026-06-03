from dataclasses import dataclass, field
from typing import Dict

import pandas as pd

BENCHMARK_REGISTRY: Dict[str, Dict[str, float]] = {
    "Conservative":      {"Less Risk": 50, "Moderate": 30, "Growth": 15, "Aggressive": 5},
    "Balanced":          {"Less Risk": 25, "Moderate": 25, "Growth": 35, "Aggressive": 15},
    "Aggressive Growth": {"Less Risk": 10, "Moderate": 10, "Growth": 50, "Aggressive": 30},
}


@dataclass
class HealthScore:
    benchmark_name: str
    score: int
    label: str
    deviations: Dict[str, float] = field(default_factory=dict)


class HealthScoreFactory:
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
