from typing import Callable
import pandas as pd

PipelineStep = Callable[[pd.DataFrame], pd.DataFrame]


class PortfolioPipeline:
    def __init__(self, steps: list[PipelineStep]):
        self.steps = steps

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        for step in self.steps:
            df = step(df)
        return df
