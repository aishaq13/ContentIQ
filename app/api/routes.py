from fastapi import APIRouter, Depends, HTTPException, status

from app.models.metadata import MetadataRecord, MetadataRecordIn
from app.services.metadata_service import MetadataService


def get_router(get_service):
    router = APIRouter(prefix="/api/v1/metadata", tags=["metadata"])

    @router.post("", response_model=MetadataRecord, status_code=status.HTTP_201_CREATED)
    async def upsert_metadata(
        payload: MetadataRecordIn, service: MetadataService = Depends(get_service)
    ) -> MetadataRecord:
        return await service.upsert(payload)

    @router.get("/{key}", response_model=MetadataRecord)
    async def get_metadata(key: str, service: MetadataService = Depends(get_service)) -> MetadataRecord:
        record = service.get(key)
        if record is None:
            raise HTTPException(status_code=404, detail="Metadata key not found")
        return record

    @router.get("", response_model=list[MetadataRecord])
    async def list_metadata(service: MetadataService = Depends(get_service)) -> list[MetadataRecord]:
        return service.list_records()

    return router
