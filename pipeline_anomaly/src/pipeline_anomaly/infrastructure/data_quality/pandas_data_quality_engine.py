import pandas as pd
from typing import Tuple

from pipeline_anomaly.domain.models.rule import Expectation
from pipeline_anomaly.domain.services.interfaces import DataQualityEngine


class PandasDataQualityEngine(DataQualityEngine):
    def validate_rule(self, df: pd.DataFrame, rule: Expectation) -> Tuple[bool, str]:
        t = rule.type
        p = rule.params or {}

        if t == "not_null":
            col = p["column"]
            if df[col].isnull().any():
                return False, f"Column '{col}' contains NULL values"
            return True, ""
        
        elif t == "between":
            col = p["column"]
            min_v, max_v = p["min"], p["max"]
            bad_rows = df[(df[col] < min_v) | (df[col] > max_v)]

            if not bad_rows.empty:
                return (
                    False,
                    f"Column '{col}' values out of bounds [{min_v}, {max_v}] ({len(bad_rows)} rows)"
                )
            return True, ""

        elif t == "unique":
            cols = p["columns"]
            dups = df.duplicated(cols)

            if dups.any():
                return (
                    False,
                    f"Duplicate rows detected based on columns {cols}: {dups.sum()} duplicates"
                )
            return True, ""

        return False, f"Unknown expectation type '{t}'"
