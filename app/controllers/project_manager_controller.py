# project_manager_controller.py
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import re

_HEX6 = re.compile(r"^#[0-9a-fA-F]{6}$")


def _valid_hex6(color: str | None) -> str | None:
    if isinstance(color, str) and _HEX6.match(color.strip()):
        return color.strip()
    return None


@dataclass
class Project:
    id: str
    name: str
    color: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        now = datetime.utcnow().isoformat()
        return cls(
            id=data.get("id") or str(uuid.uuid4()),
            name=(data.get("name") or "").strip(),
            color=(data.get("color") or None),
            created_at=data.get("created_at") or now,
            updated_at=data.get("updated_at") or data.get("created_at") or now,
        )


class ProjectManagerController:
    """CRUD for projects with JSON persistence."""

    def __init__(self, storage_path: str = "projects.json"):
        self.storage_path = storage_path
        self._projects: Dict[str, Project] = {}
        self._ensure_file()

    # ------------- file I/O -------------
    def _ensure_file(self) -> None:
        if not os.path.exists(self.storage_path):
            self._write_file([])

    def _read_file(self) -> List[Dict[str, Any]]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            self._write_file([])
            return []
        except FileNotFoundError:
            self._ensure_file()
            return []
        except Exception as e:
            raise RuntimeError(f"Failed reading {self.storage_path}: {e}") from e

    def _write_file(self, payload: List[Dict[str, Any]]) -> None:
        tmp = f"{self.storage_path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.storage_path)

    def _load(self) -> None:
        self._projects = {p["id"]: Project.from_dict(p) for p in self._read_file()}

    def _save(self) -> None:
        self._write_file([p.to_dict() for p in self._projects.values()])

    # ------------- public API -------------
    def add_project(self, name: str, color: Optional[str] = None) -> Project:
        self._load()
        name = (name or "").strip()
        if not name:
            raise ValueError("Project name is required")

        # dedupe by name (case-insensitive)
        for p in self._projects.values():
            if p.name.lower() == name.lower():
                # signal to caller that we returned existing
                return p

        now = datetime.utcnow().isoformat()
        safe_color = _valid_hex6(color)  # <- sanitize
        p = Project(
            id=str(uuid.uuid4()),
            name=name,
            color=safe_color,
            created_at=now,
            updated_at=now,
        )
        self._projects[p.id] = p
        self._save()
        return p

    def list_projects(self) -> List[Project]:
        self._load()
        # sort by name
        return sorted(self._projects.values(), key=lambda x: x.name.lower())

    def get_by_id(self, pid: str) -> Optional[Project]:
        self._load()
        return self._projects.get(pid)

    def get_by_name(self, name: str) -> Optional[Project]:
        self._load()
        lname = name.lower()
        for p in self._projects.values():
            if p.name.lower() == lname:
                return p
        return None

    def update_project(self, pid: str, **fields) -> Project:
        self._load()
        if pid not in self._projects:
            raise KeyError("Project not found")
        p = self._projects[pid]
        if "name" in fields and fields["name"]:
            p.name = fields["name"].strip()
        if "color" in fields:
            p.color = fields["color"]
        p.updated_at = datetime.utcnow().isoformat()
        self._projects[pid] = p
        self._save()
        return p

    def delete_project(self, pid: str) -> bool:
        self._load()
        ok = pid in self._projects
        if ok:
            del self._projects[pid]
            self._save()
        return ok
