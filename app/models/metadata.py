from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MetadataRecordIn(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    value: dict[str, Any]
    tags: list[str] = Field(default_factory=list)


class MetadataRecord(BaseModel):
    key: str
    value: dict[str, Any]
    tags: list[str] = Field(default_factory=list)
    version: int
    updated_at: datetime


class MetadataEvent(BaseModel):
    event_type: str
    record: MetadataRecord
    emitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
