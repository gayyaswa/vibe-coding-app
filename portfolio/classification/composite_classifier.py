import pandas as pd

from portfolio.classification.classification_strategy import ClassificationStrategy
from portfolio.classification.ticker_override_strategy import TickerOverrideStrategy
from portfolio.classification.sector_rule_strategy import SectorRuleStrategy


class CompositeClassifier:
    """Chains multiple ClassificationStrategy instances; returns the first non-None result (Composite + Strategy pattern)."""

    def __init__(self, strategies: list[ClassificationStrategy]):
        self.strategies = strategies

    def classify(self, row: pd.Series) -> str:
        # Ticker override is checked before sector rule — allows explicit exceptions
        # (e.g. MSTR is in Technology but classified Aggressive due to Bitcoin exposure)
        for strategy in self.strategies:
            result = strategy.classify(row)
            if result:
                return result
        return "Uncategorized"


DEFAULT_CLASSIFIER = CompositeClassifier([TickerOverrideStrategy(), SectorRuleStrategy()])
