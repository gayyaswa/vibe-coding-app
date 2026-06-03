from typing import Optional, Protocol
import pandas as pd

TICKER_OVERRIDE: dict[str, str] = {
    "JNJ": "Less Risk", "PG": "Less Risk", "MMF": "Less Risk", "BIL": "Less Risk", "VGSH": "Less Risk",
    "GLD": "Moderate", "IAU": "Moderate", "WMT": "Moderate", "COST": "Moderate", "NEE": "Moderate", "DUK": "Moderate",
    "AAPL": "Growth", "MSFT": "Growth", "NVDA": "Growth", "UNH": "Growth", "ABT": "Growth",
    "AMZN": "Growth", "TSLA": "Growth",
    "MSTR": "Aggressive", "COIN": "Aggressive", "EEM": "Aggressive", "ARKG": "Aggressive", "SOXS": "Aggressive",
}

SECTOR_RULES: dict[str, str] = {
    "Government": "Less Risk",
    "Money Market": "Less Risk",
    "Commodities": "Moderate",
    "Retail": "Moderate",
    "Utilities": "Moderate",
    "Consumer Staples": "Moderate",
    "Technology": "Growth",
    "Consumer Discretionary": "Growth",
    "Emerging Markets": "Aggressive",
    "Financial": "Aggressive",
}

BUCKET_ORDER = ["Less Risk", "Moderate", "Growth", "Aggressive"]

BUCKET_COLORS = {
    "Less Risk": "#2196F3",
    "Moderate": "#4CAF50",
    "Growth": "#FF9800",
    "Aggressive": "#F44336",
}


# ── Strategy pattern ──────────────────────────────────────────────────────────

class ClassificationStrategy(Protocol):
    def classify(self, row: pd.Series) -> Optional[str]: ...


class TickerOverrideStrategy:
    def classify(self, row: pd.Series) -> Optional[str]:
        return TICKER_OVERRIDE.get(str(row.get("ticker", "")).upper())


class SectorRuleStrategy:
    def classify(self, row: pd.Series) -> Optional[str]:
        return SECTOR_RULES.get(str(row.get("sector", "")))


class CompositeClassifier:
    def __init__(self, strategies: list[ClassificationStrategy]):
        self.strategies = strategies

    def classify(self, row: pd.Series) -> str:
        for strategy in self.strategies:
            result = strategy.classify(row)
            if result:
                return result
        return "Uncategorized"


DEFAULT_CLASSIFIER = CompositeClassifier([TickerOverrideStrategy(), SectorRuleStrategy()])


# ── Public API (unchanged) ────────────────────────────────────────────────────

def assign_risk_bucket(df: pd.DataFrame, classifier: CompositeClassifier = DEFAULT_CLASSIFIER) -> pd.DataFrame:
    df = df.copy()
    df["risk_bucket"] = df.apply(classifier.classify, axis=1)
    df["market_value"] = df["shares"] * df["current_price"]
    df["cost_basis"] = df["shares"] * df["purchase_price"]
    df["unrealized_pnl"] = df["market_value"] - df["cost_basis"]
    df["pnl_pct"] = (df["unrealized_pnl"] / df["cost_basis"]) * 100
    return df


if __name__ == "__main__":
    import os
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "portfolio_sample.csv")
    raw = pd.read_csv(csv_path)
    enriched = assign_risk_bucket(raw)
    print(enriched[["ticker", "risk_bucket", "market_value", "unrealized_pnl"]].to_string())
