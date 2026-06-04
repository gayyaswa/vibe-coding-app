from typing import Optional, Protocol

import pandas as pd


class ClassificationStrategy(Protocol):
    """Protocol defining the interface for risk bucket classification strategies (Strategy pattern)."""

    def classify(self, row: pd.Series) -> Optional[str]: ...
