import pandas as pd

from portfolio.classification.composite_classifier import CompositeClassifier, DEFAULT_CLASSIFIER


def assign_risk_bucket(df: pd.DataFrame, classifier: CompositeClassifier = DEFAULT_CLASSIFIER) -> pd.DataFrame:
    df = df.copy()
    df["risk_bucket"] = df.apply(classifier.classify, axis=1)
    df["market_value"] = df["shares"] * df["current_price"]
    df["cost_basis"] = df["shares"] * df["purchase_price"]
    df["unrealized_pnl"] = df["market_value"] - df["cost_basis"]
    df["pnl_pct"] = (df["unrealized_pnl"] / df["cost_basis"]) * 100
    return df
