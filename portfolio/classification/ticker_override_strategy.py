from typing import Optional

import pandas as pd

from portfolio.classification.registries import TICKER_OVERRIDE


class TickerOverrideStrategy:
    """Classifies a holding by explicit ticker lookup; returns None if the ticker is not in the override registry."""

    def classify(self, row: pd.Series) -> Optional[str]:
        return TICKER_OVERRIDE.get(str(row.get("ticker", "")).upper())
