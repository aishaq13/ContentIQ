from datetime import datetime, timezone

from app.models.metadata import MetadataEvent, MetadataRecord, MetadataRecordIn
from app.services.blob_storage import BlobStorage
from app.services.event_bus import EventBus


class MetadataService:
    def __init__(self, storage: BlobStorage, event_bus: EventBus) -> None:
        self.storage = storage
        self.event_bus = event_bus

    async def upsert(self, incoming: MetadataRecordIn) -> MetadataRecord:
        existing = self.storage.get(incoming.key)
        version = 1 if existing is None else existing.version + 1
        record = MetadataRecord(
            key=incoming.key,
            value=incoming.value,
            tags=incoming.tags,
            version=version,
            updated_at=datetime.now(timezone.utc),
        )
        self.storage.save(record)
        await self.event_bus.emit(MetadataEvent(event_type="metadata.upserted", record=record))
        return record

    def get(self, key: str) -> MetadataRecord | None:
        return self.storage.get(key)

    def list_records(self) -> list[MetadataRecord]:
        return sorted(self.storage.list_all(), key=lambda item: item.updated_at, reverse=True)
