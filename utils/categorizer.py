import pandas as pd

TICKER_OVERRIDE = {
    "JNJ": "Less Risk", "PG": "Less Risk", "MMF": "Less Risk", "BIL": "Less Risk", "VGSH": "Less Risk",
    "GLD": "Moderate", "IAU": "Moderate", "WMT": "Moderate", "COST": "Moderate", "NEE": "Moderate", "DUK": "Moderate",
    "AAPL": "Growth", "MSFT": "Growth", "NVDA": "Growth", "UNH": "Growth", "ABT": "Growth",
    "AMZN": "Growth", "TSLA": "Growth",
    "MSTR": "Aggressive", "COIN": "Aggressive", "EEM": "Aggressive", "ARKG": "Aggressive", "SOXS": "Aggressive",
}

SECTOR_RULES = {
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


def _assign_bucket(row: pd.Series) -> str:
    ticker = str(row.get("ticker", "")).upper()
    if ticker in TICKER_OVERRIDE:
        return TICKER_OVERRIDE[ticker]
    sector = str(row.get("sector", ""))
    return SECTOR_RULES.get(sector, "Uncategorized")


def assign_risk_bucket(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["risk_bucket"] = df.apply(_assign_bucket, axis=1)
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
