from typing import Dict

BENCHMARK_REGISTRY: Dict[str, Dict[str, float]] = {
    "Conservative":      {"Less Risk": 50, "Moderate": 30, "Growth": 15, "Aggressive": 5},
    "Balanced":          {"Less Risk": 25, "Moderate": 25, "Growth": 35, "Aggressive": 15},
    "Aggressive Growth": {"Less Risk": 10, "Moderate": 10, "Growth": 50, "Aggressive": 30},
}
