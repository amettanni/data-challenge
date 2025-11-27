from __future__ import annotations

from loguru import logger

from pipeline_anomaly.domain.services.interfaces import ClickHouseWriter, DatasetGenerator
from pipeline_anomaly.domain.services.data_quality import DataQualityService
from pipeline_anomaly.infrastructure.data_quality.pandas_data_quality_engine import PandasDataQualityEngine
from pipeline_anomaly.infrastructure.config import DataQualityConfig

class LoadSyntheticDataset:
    def __init__(
        self,
        generator: DatasetGenerator,
        writer: ClickHouseWriter,
        dq_config: DataQualityConfig | None = None,
    ) -> None:
        self._generator = generator
        self._writer = writer
        if dq_config and dq_config.events:
            engine = PandasDataQualityEngine()
            self._dq_service = DataQualityService(engine=engine, config=dq_config)
        else:
            self._dq_service = None

    def execute(self) -> None:
        logger.info("ensure schema")
        self._writer.ensure_schema()
        for idx, batch in enumerate(self._generator.batches(), start=1):
            logger.info("ingesting batch {}/{} rows", idx, batch.size)
            if self._dq_service:
                dq_result = self._dq_service.validate("events", batch.dataframe)

                if dq_result.has_failures:
                    logger.warning(
                        "Data quality issues detected in batch {}: {} failed rules",
                        idx,
                        len(dq_result.failed_rules),
                    )
                    for failed in dq_result.failed_rules:
                        logger.warning(
                            "  - Rule `{}` failed: {}",
                            failed.rule.type,
                            failed.message,
                        )
                else:
                    logger.info("Data quality OK for batch {}", idx)

            self._writer.ingest_batch(batch)
