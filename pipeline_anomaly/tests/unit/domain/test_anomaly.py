import pytest
import pandas as pd
from datetime import datetime

from pipeline_anomaly.domain.models.anomaly import Anomaly, AnomalyReport


class TestAnomaly:
    def test_creation(self):
        anomaly = Anomaly(
            entity_id=123,
            score=0.95,
            detector="test_detector"
        )
        assert anomaly.entity_id == 123
        assert anomaly.score == 0.95
        assert anomaly.detector == "test_detector"
    
    def test_as_dict(self):
        anomaly = Anomaly(
            entity_id=123,
            score=0.95,
            detector="test_detector"
        )
        result = anomaly.as_dict()
        assert result == {
            "entity_id": 123,
            "score": 0.95,
            "detector": "test_detector"
        }


class TestAnomalyReport:
    def test_creation(self):
        now = datetime.utcnow()
        anomalies = [
            Anomaly(entity_id=1, score=0.9, detector="detector1"),
            Anomaly(entity_id=2, score=0.8, detector="detector2")
        ]
        report = AnomalyReport(
            anomalies=anomalies,
            generated_at=now
        )
        assert report.anomalies == anomalies
        assert report.generated_at == now
    
    def test_as_dicts(self):
        now = datetime.utcnow()
        anomalies = [
            Anomaly(entity_id=1, score=0.9, detector="detector1"),
            Anomaly(entity_id=2, score=0.8, detector="detector2")
        ]
        report = AnomalyReport(
            anomalies=anomalies,
            generated_at=now
        )
        result = report.as_dicts()
        assert len(result) == 2
        assert result[0]["entity_id"] == 1
        assert result[0]["score"] == 0.9
        assert result[0]["detector"] == "detector1"
        assert result[0]["generated_at"] == now
        assert result[1]["entity_id"] == 2
        assert result[1]["generated_at"] == now