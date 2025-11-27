from __future__ import annotations

from datetime import datetime

import pandas as pd

from pipeline_anomaly.domain.models.aggregate import AggregateCollection
from pipeline_anomaly.domain.models.anomaly import AnomalyReport
from pipeline_anomaly.domain.models.batch import RecordBatch
from pipeline_anomaly.infrastructure.clients.clickhouse import ClickHouseFactory


class ClickHouseRepository:
    def __init__(self, factory: ClickHouseFactory) -> None:
        self._factory = factory

    def ensure_schema(self) -> None:
        ddl_statements = [
            """
            CREATE TABLE IF NOT EXISTS events (
                event_time DateTime,
                entity_id UInt64,
                value Float64,
                attribute Float64
            ) 
            ENGINE = MergeTree
            PARTITION BY toYYYYMM(event_time)
            ORDER BY (event_time, entity_id)
            """,
            """
            CREATE TABLE IF NOT EXISTS aggregates (
                metric String,
                value Float64,
                window_start DateTime,
                window_end DateTime,
                extra Map(String, Float64) CODEC(ZSTD(3))
            ) 
            ENGINE = MergeTree(version)
            ORDER BY (metric, window_start)
            """,
            """
            CREATE TABLE IF NOT EXISTS anomaly_reports (
                generated_at DateTime,
                window_start DateTime,
                window_end DateTime,
                detector String,
                score Float64,
                severity Float64,
                description String
            ) ENGINE = MergeTree ORDER BY (generated_at, detector)
            """,
        ]
        with self._factory.connect() as client:
            for ddl in ddl_statements:
                client.command(ddl)

    def ingest_batch(self, batch: RecordBatch) -> None:
        with self._factory.connect() as client:
            client.insert_df("events", batch.dataframe)
            
    def insert_dicts(self, table: str, rows: list[dict]) -> None:
        if not rows:
            return
        
        first_keys = set(rows[0].keys())
        for r in rows:
            if set(r.keys()) != first_keys:
                raise ValueError("All dicts must have the same keys")

        column_names = list(first_keys)
        data = [[row[col] for col in column_names] for row in rows]

        with self._factory.connect() as client:
            client.insert(table, data, column_names=column_names)

    def persist_aggregates(self, aggregates: AggregateCollection) -> None:
        payload = aggregates.as_dict()
        self.insert_dicts("aggregates", payload)

    def persist_report(self, report: AnomalyReport) -> None:
        rows = [
            {
                "generated_at": report.generated_at,
                "window_start": report.window_start,
                "window_end": report.window_end,
                "detector": anomaly.detector,
                "score": anomaly.score,
                "severity": anomaly.severity,
                "description": anomaly.description,
            }
            for anomaly in report.anomalies
        ]
        self.insert_dicts("anomaly_reports", rows)

    def read_latest_window(self) -> pd.DataFrame:
        with self._factory.connect() as client:
            query = """
            SELECT * FROM events
            WHERE event_time >= now() - INTERVAL 2 DAY
            ORDER BY event_time
            """
            result = client.query_df(query)
        if result.empty:
            raise RuntimeError("events table is empty")
        return result
