import pandas as pd

from portfolio.classification import BUCKET_ORDER

HOLD_THRESHOLD = 50.0  # Prevents micro-transactions; deltas below this dollar amount stay as HOLD


def bucket_summary(df: pd.DataFrame, targets: dict) -> pd.DataFrame:
    total = df["market_value"].sum()
    rows = []
    for bucket in BUCKET_ORDER:
        current_value = df.loc[df["risk_bucket"] == bucket, "market_value"].sum()
        current_pct = (current_value / total * 100) if total > 0 else 0.0
        target_pct = targets.get(bucket, 0.0)
        target_value = target_pct / 100 * total
        delta = target_value - current_value
        rows.append({
            "risk_bucket": bucket,
            "current_value": current_value,
            "current_pct": current_pct,
            "target_pct": target_pct,
            "target_value": target_value,
            "delta": delta,
        })
    return pd.DataFrame(rows)


def compute_rebalancing(df: pd.DataFrame, targets: dict) -> pd.DataFrame:
    total = df["market_value"].sum()
    result_rows = []

    for bucket in BUCKET_ORDER:
        bucket_df = df[df["risk_bucket"] == bucket].copy()
        bucket_current = bucket_df["market_value"].sum()
        target_pct = targets.get(bucket, 0.0)
        bucket_target = target_pct / 100 * total
        bucket_delta = bucket_target - bucket_current

        for _, row in bucket_df.iterrows():
            # Distributes bucket delta proportionally by current stock weight within the bucket,
            # not equally — preserves relative position sizes when rebalancing
            if bucket_current > 0:
                weight = row["market_value"] / bucket_current
            else:
                weight = 1.0 / len(bucket_df) if len(bucket_df) > 0 else 0.0
            stock_delta = bucket_delta * weight
            if abs(stock_delta) < HOLD_THRESHOLD:
                action = "HOLD"
            elif stock_delta > 0:
                action = "BUY"
            else:
                action = "SELL"
            result_rows.append({
                "ticker": row["ticker"],
                "name": row["name"],
                "risk_bucket": bucket,
                "current_value": row["market_value"],
                "target_value": row["market_value"] + stock_delta,
                "delta": stock_delta,
                "action": action,
            })

    return pd.DataFrame(result_rows)
