from typing import Optional

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate

from portfolio.insights.insight_strategy import InsightStrategy


class RebalancingRationaleInsight(InsightStrategy):
    """Generates plain-English explanation of BUY/SELL/HOLD actions grouped by risk bucket."""

    def build_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "You are a financial advisor explaining a portfolio rebalancing plan to a retail investor. Be clear, specific, and use simple language — no jargon."),
            ("human", "{context}\n\n{question}"),
        ])

    def build_context(self, df: pd.DataFrame, rebal_df: Optional[pd.DataFrame], targets: Optional[dict]) -> str:
        if targets is None or rebal_df is None:
            raise ValueError("Targets must be set before generating rebalancing rationale.")

        total = df["market_value"].sum()
        lines = [f"PORTFOLIO SUMMARY — total value ${total:,.0f}\n"]

        lines.append("BUCKET ALLOCATION:")
        for bucket in df["risk_bucket"].unique():
            pct = df.loc[df["risk_bucket"] == bucket, "market_value"].sum() / total * 100
            target = targets.get(bucket, 0)
            lines.append(f"  {bucket}: current {pct:.1f}%, target {target:.1f}%")

        lines.append("\nREBALANCING ACTIONS:")
        for _, row in rebal_df.iterrows():
            lines.append(
                f"  {row['ticker']} ({row['risk_bucket']}): {row['action']} ${abs(row['delta']):,.0f}"
            )

        return "\n".join(lines)

    def build_question(self) -> str:
        return (
            "Explain in plain English why each BUY, SELL, and HOLD action is being recommended. "
            "Group your explanation by risk bucket. Be specific about which buckets are over or underweight "
            "and what that means for the investor. Max 200 words."
        )
