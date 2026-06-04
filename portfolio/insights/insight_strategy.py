from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generator, Optional

import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


class InsightStrategy(ABC):
    """Abstract base for LangChain-powered AI insight strategies; each subclass targets one type of portfolio analysis (Strategy pattern)."""

    def __init__(self, llm) -> None:
        # LCEL chain: prompt template | LLM | parser — enables token streaming via .stream()
        # The chain is built once at init so LangChain can apply prompt caching to the prefix
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
