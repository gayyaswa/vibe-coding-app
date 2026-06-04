from typing import Callable

import pandas as pd

PipelineStep = Callable[[pd.DataFrame], pd.DataFrame]


class PortfolioPipeline:
    """Runs a sequence of DataFrame transform steps in order (Pipeline pattern); each step receives the output of the previous."""

    def __init__(self, steps: list[PipelineStep]):
        self.steps = steps

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        # Steps run sequentially; each receives the DataFrame returned by the previous step.
        # Failure in any step propagates immediately — no partial state is returned.
        for step in self.steps:
            df = step(df)
        return df
