from typing import Optional

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate

from portfolio.insights.insight_strategy import InsightStrategy


class SectorConcentrationInsight(InsightStrategy):
    """Identifies sector concentration risks: overweight sectors, missing sectors, and single-stock dominance within buckets."""

    def build_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "You are a financial advisor reviewing portfolio sector exposure. Be direct and specific — name the actual sectors and tickers involved."),
            ("human", "{context}\n\n{question}"),
        ])

    def build_context(self, df: pd.DataFrame, rebal_df: Optional[pd.DataFrame], targets: Optional[dict]) -> str:
        total = df["market_value"].sum()
        lines = [f"PORTFOLIO HOLDINGS — total value ${total:,.0f}\n"]

        lines.append("SECTOR BREAKDOWN:")
        sector_totals = df.groupby("sector")["market_value"].sum().sort_values(ascending=False)
        for sector, val in sector_totals.items():
            pct = val / total * 100
            tickers = df.loc[df["sector"] == sector, "ticker"].tolist()
            lines.append(f"  {sector}: {pct:.1f}% (${val:,.0f}) — {', '.join(tickers)}")

        lines.append("\nHOLDINGS BY RISK BUCKET:")
        for bucket in df["risk_bucket"].unique():
            bucket_df = df[df["risk_bucket"] == bucket]
            bucket_total = bucket_df["market_value"].sum()
            lines.append(f"  {bucket} (${bucket_total:,.0f}):")
            for _, row in bucket_df.iterrows():
                pct_of_bucket = row["market_value"] / bucket_total * 100
                lines.append(f"    {row['ticker']} ({row['sector']}): {pct_of_bucket:.1f}% of bucket")

        return "\n".join(lines)

    def build_question(self) -> str:
        return (
            "Identify concentration risks in this portfolio. Cover: "
            "1) Any sector making up more than 25% of the total portfolio, "
            "2) Important sectors that are completely missing (e.g. Healthcare, Energy, Real Estate), "
            "3) Any single stock making up more than 15% of its own risk bucket. "
            "Format your response under three headings: Overweight Sectors / Missing Sectors / Concentration Alerts. "
            "Max 150 words."
        )
