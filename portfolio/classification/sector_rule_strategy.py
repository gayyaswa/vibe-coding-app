from typing import Optional

import pandas as pd

from portfolio.classification.registries import SECTOR_RULES


class SectorRuleStrategy:
    """Classifies a holding by sector using the sector-to-bucket rule registry; returns None if the sector is unknown."""

    def classify(self, row: pd.Series) -> Optional[str]:
        return SECTOR_RULES.get(str(row.get("sector", "")))
