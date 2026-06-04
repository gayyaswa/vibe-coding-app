from dataclasses import dataclass, field
from typing import Dict


@dataclass
class HealthScore:
    """Immutable value object holding a portfolio's alignment score against a single benchmark."""

    benchmark_name: str
    score: int
    label: str
    deviations: Dict[str, float] = field(default_factory=dict)
