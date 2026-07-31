"""Database backup tasks."""

import asyncio
import os
import subprocess
from datetime import UTC, datetime

import structlog

from app.config import get_settings
from app.core.celery_app import celery_app

logger = structlog.get_logger()
settings = get_settings()


@celery_app.task(name="app.tasks.backup_tasks.run_database_backup")
def run_database_backup():
    if not settings.backup_enabled:
        return {"status": "disabled"}

    backup_dir = "/app/backups"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"{backup_dir}/chre_backup_{timestamp}.sql"

    try:
        subprocess.run(
            ["pg_dump", settings.database_url_sync, "-f", filename],
            check=True,
            capture_output=True,
            timeout=3600,
        )
        logger.info("backup_complete", file=filename)
        return {"status": "success", "file": filename}
    except Exception as exc:
        logger.error("backup_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}
