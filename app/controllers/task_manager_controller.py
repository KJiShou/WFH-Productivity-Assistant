from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

# Store due_date as "YYYY-MM-DD"
DATE_FMT = "%Y-%m-%d"


# -------------------- Domain Model --------------------
@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    project: Optional[str] = None
    due_date: Optional[str] = None  # "YYYY-MM-DD" or None
    status: str = "todo"
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        # fill defaults & normalize
        now_iso = datetime.utcnow().isoformat()
        t = cls(
            id=data.get("id") or str(uuid.uuid4()),
            title=(data.get("title") or "").strip(),
            description=(data.get("description") or "").strip(),
            project=(data.get("project") or None),
            due_date=(data.get("due_date") or None),
            status=(data.get("status") or "todo"),
            created_at=data.get("created_at") or now_iso,
            updated_at=data.get("updated_at") or data.get("created_at") or now_iso,
        )
        # crude date validation; if invalid, drop it
        if t.due_date:
            try:
                datetime.strptime(t.due_date, DATE_FMT)
            except ValueError:
                t.due_date = None
        return t


# -------------------- Controller --------------------
class TaskManagerController:
    """
    CRUD for tasks with JSON file persistence.
    - add_task(): create + save
    - view_tasks(): read fresh from file
    - get_task(): read one by id
    - update_task(): modify allowed fields + save
    - delete_task(): remove + save
    """

    def __init__(self, storage_path: str = "tasks.json"):
        self.storage_path = storage_path
        self._tasks: Dict[str, Task] = {}
        self._ensure_file()

    # ---------- file i/o ----------
    def _ensure_file(self) -> None:
        if not os.path.exists(self.storage_path):
            self._write_file([])

    def _read_file(self) -> List[Dict[str, Any]]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Corrupted/empty => reset
            self._write_file([])
            return []
        except FileNotFoundError:
            self._ensure_file()
            return []
        except Exception as e:
            raise RuntimeError(f"Failed reading {self.storage_path}: {e}") from e

    def _write_file(self, payload: List[Dict[str, Any]]) -> None:
        # Atomic write (safe for crashes)
        tmp = f"{self.storage_path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.storage_path)

    def _load_into_memory(self) -> None:
        raw = self._read_file()
        self._tasks = {item.get("id"): Task.from_dict(item) for item in raw if item}

    def _save_from_memory(self) -> None:
        self._write_file([t.to_dict() for t in self._tasks.values()])

    # ---------- public API ----------
    def add_task(
        self,
        title: str,
        description: str = "",
        project: Optional[str] = None,
        due_date: Optional[str] = None,  # "YYYY-MM-DD"
        status: str = "todo",
    ) -> Task:
        """Create a task and persist to file."""
        self._load_into_memory()
        now = datetime.utcnow().isoformat()
        t = Task(
            id=str(uuid.uuid4()),
            title=title.strip(),
            description=description.strip(),
            project=project.strip() if isinstance(project, str) else project,
            due_date=due_date,
            status=status,
            created_at=now,
            updated_at=now,
        )
        self._tasks[t.id] = t
        self._save_from_memory()
        return t

    def view_tasks(self) -> List[Task]:
        """Fresh read from file; returns tasks sorted by (due_date, created_at)."""
        self._load_into_memory()

        def key(t: Task):
            try:
                due = (
                    datetime.strptime(t.due_date, DATE_FMT)
                    if t.due_date
                    else datetime.max
                )
            except ValueError:
                due = datetime.max
            return (due, t.created_at)

        return sorted(self._tasks.values(), key=key)

    def get_task(self, task_id: str) -> Optional[Task]:
        self._load_into_memory()
        return self._tasks.get(task_id)

    def update_task(self, task_id: str, **fields) -> Task:
        """
        Update allowed fields in a task and persist.
        Allowed: title, description, project, due_date, status
        """
        self._load_into_memory()
        if task_id not in self._tasks:
            raise KeyError(f"Task '{task_id}' not found")
        t = self._tasks[task_id]
        allowed = {"title", "description", "project", "due_date", "status"}
        for k, v in fields.items():
            if k in allowed:
                setattr(t, k, v.strip() if isinstance(v, str) else v)
        t.updated_at = datetime.utcnow().isoformat()
        self._tasks[task_id] = t
        self._save_from_memory()
        return t

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by id and persist. Returns True if deleted."""
        self._load_into_memory()
        existed = task_id in self._tasks
        if existed:
            del self._tasks[task_id]
            self._save_from_memory()
        return existed

    # convenience filter/search (optional)
    def find_by_title(self, query: str) -> List[Task]:
        self._load_into_memory()
        q = query.lower()
        return [t for t in self._tasks.values() if q in t.title.lower()]
