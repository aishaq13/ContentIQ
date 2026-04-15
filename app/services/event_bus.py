import contextlib
import asyncio
import json
import logging
from collections.abc import Callable
from typing import Awaitable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.models.metadata import MetadataEvent

logger = logging.getLogger(__name__)


class EventBus:
    """Kafka-first event bus with graceful fallback when Kafka is unavailable."""

    def __init__(self, bootstrap_servers: str, topic: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self._producer: AIOKafkaProducer | None = None
        self._consumer_task: asyncio.Task | None = None
        self._fallback_queue: asyncio.Queue[MetadataEvent] = asyncio.Queue()
        self._fallback_mode = False

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        try:
            await self._producer.start()
            logger.info("Kafka producer connected")
        except Exception as exc:  # pragma: no cover - depends on external broker
            logger.warning("Kafka unavailable, switching to local fallback queue: %s", exc)
            self._fallback_mode = True

    async def stop(self) -> None:
        if self._consumer_task:
            self._consumer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._consumer_task
        if self._producer and not self._fallback_mode:
            await self._producer.stop()

    async def emit(self, event: MetadataEvent) -> None:
        if self._fallback_mode:
            await self._fallback_queue.put(event)
            return

        assert self._producer is not None
        await self._producer.send_and_wait(self.topic, event.model_dump_json().encode("utf-8"))

    async def subscribe(self, handler: Callable[[MetadataEvent], Awaitable[None]]) -> None:
        if self._fallback_mode:
            self._consumer_task = asyncio.create_task(self._consume_fallback(handler))
            return

        consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            enable_auto_commit=True,
            group_id="contentiq-propagator",
        )
        await consumer.start()

        async def _run() -> None:
            try:
                async for msg in consumer:
                    payload = json.loads(msg.value.decode("utf-8"))
                    await handler(MetadataEvent.model_validate(payload))
            finally:
                await consumer.stop()

        self._consumer_task = asyncio.create_task(_run())

    async def _consume_fallback(self, handler: Callable[[MetadataEvent], Awaitable[None]]) -> None:
        while True:
            event = await self._fallback_queue.get()
            await handler(event)
