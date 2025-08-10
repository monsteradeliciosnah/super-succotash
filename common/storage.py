from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, os, time
from typing import Iterable, List, Dict, Optional

@dataclass
class FileInfo:
    path: str
    size: int
    modified_ts: float
    sha1: Optional[str] = None
    meta: Optional[dict] = None

class LocalStorage:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def list_files(self, pattern: str = "**/*") -> Iterable[FileInfo]:
        for p in self.root.glob(pattern):
            if p.is_file():
                yield FileInfo(path=str(p), size=p.stat().st_size, modified_ts=p.stat().st_mtime)

    def write_json(self, rel: str, data: dict):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2))

    def read_json(self, rel: str) -> dict:
        return json.loads((self.root / rel).read_text())

    def touch(self, rel: str, content: str = ""):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

def now_ts() -> float:
    return time.time()
