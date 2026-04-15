import json
from pathlib import Path
from typing import Iterable

from app.models.metadata import MetadataRecord


class BlobStorage:
    """Simple blob-like persistence backed by local files for AKS/container dev."""

    def __init__(self, root_path: str) -> None:
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def save(self, record: MetadataRecord) -> None:
        self._path_for(record.key).write_text(record.model_dump_json(indent=2), encoding="utf-8")

    def get(self, key: str) -> MetadataRecord | None:
        path = self._path_for(key)
        if not path.exists():
            return None
        return MetadataRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def list_all(self) -> Iterable[MetadataRecord]:
        for item in self.root.glob("*.json"):
            yield MetadataRecord.model_validate_json(item.read_text(encoding="utf-8"))
