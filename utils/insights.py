from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Generator, Optional, Type

import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from utils.facade import PortfolioFacade


class InsightStrategy(ABC):
    def __init__(self, llm) -> None:
        self._llm = llm
        self._chain = self.build_prompt_template() | llm | StrOutputParser()

    @abstractmethod
    def build_prompt_template(self) -> ChatPromptTemplate:
        ...

    @abstractmethod
    def build_context(
        self,
        df: pd.DataFrame,
        rebal_df: Optional[pd.DataFrame],
        targets: Optional[dict],
    ) -> str:
        ...

    @abstractmethod
    def build_question(self) -> str:
        ...

    def stream(self, df: pd.DataFrame, rebal_df: Optional[pd.DataFrame], targets: Optional[dict]) -> Generator:
        yield from self._chain.stream({
            "context": self.build_context(df, rebal_df, targets),
            "question": self.build_question(),
        })


class RebalancingRationaleInsight(InsightStrategy):
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


class SectorConcentrationInsight(InsightStrategy):
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


INSIGHT_REGISTRY: Dict[str, Type[InsightStrategy]] = {
    "rebalancing_rationale": RebalancingRationaleInsight,
    "sector_concentration": SectorConcentrationInsight,
}


class InsightFactory:
    @staticmethod
    def create(insight_type: str, llm) -> InsightStrategy:
        cls = INSIGHT_REGISTRY.get(insight_type)
        if cls is None:
            raise ValueError(f"Unknown insight type: {insight_type!r}")
        return cls(llm)


class InsightsFacade:
    """Orchestrates LangChain-based AI insights. LLM is injected for testability and model portability."""

    def __init__(self, portfolio_facade: PortfolioFacade, targets: Optional[dict], llm) -> None:
        self._facade = portfolio_facade
        self._targets = targets
        self._llm = llm

    def stream_insight(self, insight_type: str) -> Generator:
        rebal_df = self._facade.compute_rebalancing(self._targets) if self._targets else None
        strategy = InsightFactory.create(insight_type, self._llm)
        yield from strategy.stream(self._facade.portfolio, rebal_df, self._targets)
