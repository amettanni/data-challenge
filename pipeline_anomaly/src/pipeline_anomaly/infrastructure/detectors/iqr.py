from __future__ import annotations

import pandas as pd
from pipeline_anomaly.infrastructure.detectors.base import PandasDetector


class IQRDetector(PandasDetector):
    def __init__(self, multiplier: float = 1.5):
        super().__init__("iqr")
        self._multiplier = multiplier

    def fit_predict(self, dataframe: pd.DataFrame) -> pd.Series:
        q1 = dataframe["value"].quantile(0.25)
        q3 = dataframe["value"].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - self._multiplier * iqr
        upper = q3 + self._multiplier * iqr
        return ((dataframe["value"] < lower) | (dataframe["value"] > upper)).astype(int)
