from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from pipeline_anomaly.domain.models.anomaly import AnomalyReport
from pipeline_anomaly.domain.services.interfaces import AlertSink


class FileAlertSink(AlertSink):
    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(file_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.touch()

    def send(self, report: AnomalyReport) -> None:
        payload = {
            "generated_at": report.generated_at.isoformat(),
            "window_start": report.window_start.isoformat(),
            "window_end": report.window_end.isoformat(),
            "anomalies": [
                {
                    "detector": a.detector,
                    "score": a.score,
                    "severity": a.severity,
                    "description": a.description,
                }
                for a in report.anomalies
            ],
            "written_at": datetime.utcnow().isoformat()
        }

        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
