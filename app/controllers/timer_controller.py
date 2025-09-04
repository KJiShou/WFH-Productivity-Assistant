import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any

RECORD_FILE = "timer_record.json"
TIME_FMT = "%d-%m-%Y %H:%M:%S"


@dataclass
class TimerRecord:
    task_id: str
    start_day: str
    start_date_time: str
    duration: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TimerController:
    def __init__(self, record: str = RECORD_FILE):
        self.record = record
        self._ensure_file()

    # file input and output
    def _ensure_file(self) -> None:
        if not os.path.exists(self.record):
            self._write_file([])

    # loads the JSON file into list
    def _read_file(self) -> List[Dict[str, Any]]:
        try:
            with open(self.record, "r", encoding="utf-8") as f:
                return json.load(f)

        except (json.JSONDecodeError, FileNotFoundError):
            self._write_file([])
            return []

    # save the data back to JSON file
    def _write_file(self, data: List[Dict[str, Any]]) -> None:
        tmp = f"{self.record}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.record)

    # --- public API ---
    def add_record(
        self, task_id: str, start_day: str, start_date_time: str, duration: str
    ) -> TimerRecord:
        record = TimerRecord(
            task_id=task_id,
            start_day=start_day,
            start_date_time=start_date_time,
            duration=duration,
        )
        data = self._read_file()
        data.append(record.to_dict())
        self._write_file(data)
        return record

    def view_record(self) -> List[TimerRecord]:
        raw = self._read_file()
        return [TimerRecord(**s) for s in raw]
