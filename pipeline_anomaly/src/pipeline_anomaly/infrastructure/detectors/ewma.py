from __future__ import annotations

import pandas as pd
from pipeline_anomaly.infrastructure.detectors.base import PandasDetector


class EWMADetector(PandasDetector):
    def __init__(self, threshold: float, alpha: float = 0.3):
        super().__init__("ewma")
        self._threshold = threshold
        self._alpha = alpha

    def fit_predict(self, dataframe: pd.DataFrame) -> pd.Series:
        ewma = dataframe["value"].ewm(alpha=self._alpha).mean()
        diff = (dataframe["value"] - ewma).abs()
        return (diff > self._threshold).astype(int)
