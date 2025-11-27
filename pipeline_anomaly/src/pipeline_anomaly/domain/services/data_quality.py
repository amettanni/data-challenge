from __future__ import annotations

from dataclasses import dataclass
from typing import List, Any

from pipeline_anomaly.domain.models.rule import TableRule, Expectation
from pipeline_anomaly.infrastructure.config import DataQualityConfig


@dataclass(slots=True)
class FailedRule:
    rule: Expectation
    message: str


@dataclass(slots=True)
class DataQualityResult:
    has_failures: bool
    failed_rules: List[FailedRule]


class DataQualityService:
    def __init__(self, engine: Any, config: DataQualityConfig) -> None:
        self._engine = engine
        self._config = config

    def validate(self, table_name: str, dataframe) -> DataQualityResult:
        rules = self._build_rules_for_table(table_name)
        failures: List[FailedRule] = []

        for rule in rules.expectations:
            ok, message = self._engine.validate_rule(dataframe, rule)
            if not ok:
                failures.append(FailedRule(rule=rule, message=message))

        return DataQualityResult(
            has_failures=len(failures) > 0,
            failed_rules=failures
        )

    def _build_rules_for_table(self, table_name: str) -> TableRule:
        expectations = []
        if table_name == "events":
            for rule_cfg in self._config.events:
                expectations.append(
                    Expectation(
                        type=rule_cfg.type,
                        params={
                            "column": rule_cfg.column,
                            "min": rule_cfg.min,
                            "max": rule_cfg.max,
                            "columns": rule_cfg.columns,
                        }
                    )
                )

        return TableRule(
            table=table_name,
            expectations=tuple(expectations)
        )