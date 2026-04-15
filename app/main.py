from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import get_router
from app.core.config import get_settings
from app.services.blob_storage import BlobStorage
from app.services.event_bus import EventBus
from app.services.metadata_service import MetadataService

settings = get_settings()
storage = BlobStorage(settings.blob_root_path)
event_bus = EventBus(settings.kafka_bootstrap_servers, settings.kafka_topic)
metadata_service = MetadataService(storage=storage, event_bus=event_bus)


async def handle_event(event):
    # In production this would trigger cache invalidation / config propagation.
    return None


@asynccontextmanager
async def lifespan(_: FastAPI):
    await event_bus.start()
    await event_bus.subscribe(handle_event)
    yield
    await event_bus.stop()


app = FastAPI(title="ContentIQ", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


def _get_metadata_service() -> MetadataService:
    return metadata_service


app.include_router(get_router(_get_metadata_service))
