import pytest
from datetime import datetime

from pipeline_anomaly.domain.models.aggregate import Aggregate, AggregateCollection


class TestAggregate:
    def test_creation(self):
        now = datetime.utcnow()
        agg = Aggregate(
            name="test_metric",
            value=42.0,
            window_start=now,
            window_end=now,
        )
        assert agg.name == "test_metric"
        assert agg.value == 42.0
        assert agg.window_start == now
        assert agg.window_end == now
    
    def test_as_dict(self):
        now = datetime.utcnow()
        agg = Aggregate(
            name="test_metric",
            value=42.0,
            window_start=now,
            window_end=now,
        )
        result = agg.as_dict()
        assert result == {
            "name": "test_metric",
            "value": 42.0,
            "window_start": now,
            "window_end": now,
        }


class TestAggregateCollection:
    def test_creation(self):
        now = datetime.utcnow()
        agg1 = Aggregate("metric1", 10.0, now, now)
        agg2 = Aggregate("metric2", 20.0, now, now)
        collection = AggregateCollection(aggregates=(agg1, agg2))
        assert len(collection.aggregates) == 2
        assert collection.aggregates[0].name == "metric1"
        assert collection.aggregates[1].name == "metric2"
    
    def test_as_dicts(self):
        now = datetime.utcnow()
        agg1 = Aggregate("metric1", 10.0, now, now)
        agg2 = Aggregate("metric2", 20.0, now, now)
        collection = AggregateCollection(aggregates=(agg1, agg2))
        result = collection.as_dicts()
        assert len(result) == 2
        assert result[0]["name"] == "metric1"
        assert result[0]["value"] == 10.0
        assert result[1]["name"] == "metric2"
        assert result[1]["value"] == 20.0