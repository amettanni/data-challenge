from __future__ import annotations

import pandas as pd
from pipeline_anomaly.infrastructure.detectors.base import PandasDetector


class EnsembleDetector(PandasDetector):
    def __init__(self, detectors: list[PandasDetector], min_votes: int = None):
        super().__init__("ensemble")
        self._detectors = detectors
        self._min_votes = min_votes or len(detectors) // 2 + 1

    def fit_predict(self, dataframe: pd.DataFrame) -> pd.Series:
        preds = [d.fit_predict(dataframe) for d in self._detectors]
        votes = sum(preds)
        return (votes >= self._min_votes).astype(int)
