from typing import Dict

TICKER_OVERRIDE: Dict[str, str] = {
    "JNJ": "Less Risk", "PG": "Less Risk", "MMF": "Less Risk", "BIL": "Less Risk", "VGSH": "Less Risk",
    "GLD": "Moderate", "IAU": "Moderate", "WMT": "Moderate", "COST": "Moderate", "NEE": "Moderate", "DUK": "Moderate",
    "AAPL": "Growth", "MSFT": "Growth", "NVDA": "Growth", "UNH": "Growth", "ABT": "Growth",
    "AMZN": "Growth", "TSLA": "Growth",
    "MSTR": "Aggressive", "COIN": "Aggressive", "EEM": "Aggressive", "ARKG": "Aggressive", "SOXS": "Aggressive",
}

SECTOR_RULES: Dict[str, str] = {
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
