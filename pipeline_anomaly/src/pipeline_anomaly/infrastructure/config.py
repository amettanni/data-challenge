from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from pipeline_anomaly.infrastructure.generators.synthetic_generator import SyntheticDatasetConfig


@dataclass(slots=True)
class ClickHouseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str


@dataclass(slots=True)
class IsolationForestConfig:
    contamination: float
    random_state: int


@dataclass(slots=True)
class DBSCANConfig:
    eps: float
    min_samples: int


@dataclass(slots=True)
class IQRConfig:
    multiplier: float


@dataclass(slots=True)
class EWMAConfig:
    threshold: float
    alpha: int


@dataclass(slots=True)
class EnsembleConfig:
    min_votes: int


@dataclass(slots=True)
class AnomalyDetectionConfig:
    zscore_threshold: float
    isolation_forest: IsolationForestConfig
    dbscan: DBSCANConfig
    iqr: IQRConfig
    ewma: EWMAConfig
    ensemble: EnsembleConfig


@dataclass(slots=True)
class AlertingConfig:
    enabled: bool
    threshold_score: float
    sink: str
    file_path: str | None = None

@dataclass(slots=True)
class DataQualityRuleConfig:
    type: str
    column: str | None = None
    min: float | None = None
    max: float | None = None
    columns:list[str] | None = None


@dataclass(slots=True)
class DataQualityConfig:
    events: list[DataQualityRuleConfig]

@dataclass(slots=True)
class PipelineConfig:
    clickhouse: ClickHouseConfig
    dataset: SyntheticDatasetConfig
    anomaly_detection: AnomalyDetectionConfig
    alerting: AlertingConfig
    data_quality: DataQualityConfig

    @classmethod
    def load(cls, path: Path) -> "PipelineConfig":
        with path.open("r", encoding="utf-8") as file:
            raw = yaml.safe_load(file)
        
        dq_raw = raw.get("data_quality", {})
        dq_events_raw = dq_raw.get("events", [])
        dq_events = [
            DataQualityRuleConfig(
                type=rule["type"],
                column=rule.get("column"),
                min=rule.get("min"),
                max=rule.get("max"),
                columns=rule.get("columns"),
            )
            for rule in dq_events_raw
        ]
        dq_config = DataQualityConfig(events=dq_events)

        return cls(
            clickhouse=ClickHouseConfig(**raw["clickhouse"]),
            dataset=SyntheticDatasetConfig(**raw["dataset"]),
            anomaly_detection=AnomalyDetectionConfig(
                zscore_threshold=float(raw["anomaly_detection"]["zscore_threshold"]),
                isolation_forest=IsolationForestConfig(**raw["anomaly_detection"]["isolation_forest"]),
                dbscan=DBSCANConfig(**raw["anomaly_detection"]["dbscan"]),
                iqr=IQRConfig(**raw["anomaly_detection"]["iqr"]),
                ewma=EWMAConfig(**raw["anomaly_detection"]["ewma"]),
                ensemble=EnsembleConfig(**raw["anomaly_detection"]["ensemble"]),
            ),
            alerting=AlertingConfig(**raw["alerting"]),
            data_quality=dq_config,
        )
