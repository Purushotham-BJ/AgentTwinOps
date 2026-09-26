# Metrics collector module.
"""
This module defines an async background task that periodically gathers system
metrics (CPU, memory, disk, network) and stores them via the MetricService.
It also triggers digital‑twin synchronization.
The collector is started from the FastAPI lifespan (backend/app/core/lifespan.py).
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime

import psutil
from sqlalchemy import select

from app.config.settings import get_settings
from app.models.infrastructure import Infrastructure
from app.services.metric_service import MetricService
from app.dependencies.db import get_db
from app.schemas.metric import MetricCreate

logger = logging.getLogger(__name__)


async def _gather_host_metrics() -> dict:
    """Collect basic host metrics using psutil.
    Returns a dictionary compatible with the ``MetricCreate`` schema.
    """
    cpu_percent = psutil.cpu_percent(interval=None)
    virtual_mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    return {
        "cpu_usage": cpu_percent,
        "memory_usage": virtual_mem.percent,
        "disk_usage": disk.percent,
        "network_usage": net_io.bytes_sent + net_io.bytes_recv,
        "latency": 0.0,  # placeholder, actual measurement could be added later
        "timestamp": datetime.utcnow(),
    }


async def collect_metrics(app) -> None:
    """Background task that runs until the application shuts down.
    The task respects the ``METRIC_COLLECTION_INTERVAL`` setting and uses a
    fresh ``AsyncSession`` per iteration obtained from the ``get_db`` dependency.
    """
    settings = get_settings()
    interval = getattr(settings, "METRIC_COLLECTION_INTERVAL", 5)
    logger.info("[METRIC COLLECTOR] Starting with interval %s seconds", interval)

    while True:
        try:
            payload_dict = await _gather_host_metrics()
            env_id = os.getenv("HOST_SERVICE_ID")

            # Obtain a DB session for this iteration.
            async for db in get_db():
                if env_id:
                    try:
                        service_uuid = uuid.UUID(env_id)
                    except ValueError:
                        logger.error(
                            "[METRIC COLLECTOR] HOST_SERVICE_ID is not a valid UUID; "
                            "skipping metric collection"
                        )
                        break
                    service_exists = await db.scalar(
                        select(Infrastructure.id).where(Infrastructure.id == service_uuid)
                    )
                else:
                    service_uuid = await db.scalar(
                        select(Infrastructure.id).order_by(Infrastructure.created_at).limit(1)
                    )
                    service_exists = service_uuid

                if service_exists is None:
                    logger.warning(
                        "[METRIC COLLECTOR] No registered infrastructure service found; "
                        "skipping metric collection"
                    )
                    break

                payload_dict["service_id"] = service_uuid
                metric_in = MetricCreate(**payload_dict)
                metric_service = MetricService(db)
                await metric_service.ingest_metric(metric_in)
                break

            logger.debug("[METRIC COLLECTOR] Metric ingested: %s", payload_dict)
        except asyncio.CancelledError:
            logger.info("[METRIC COLLECTOR] Cancellation requested – exiting loop")
            break
        except Exception as exc:
            logger.exception("[METRIC COLLECTOR] Unexpected error during collection: %s", exc)

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("[METRIC COLLECTOR] Cancellation during sleep – exiting")
            break

    logger.info("[METRIC COLLECTOR] Stopped")
