"""Celery application and beat schedule."""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "chre",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.crawl_tasks",
        "app.tasks.ai_tasks",
        "app.tasks.index_tasks",
        "app.tasks.backup_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=60,
    task_max_retries=5,
    beat_schedule={
        "daily-full-crawl": {
            "task": "app.tasks.crawl_tasks.run_scheduled_crawls",
            "schedule": crontab(hour=2, minute=0),
        },
        "incremental-crawl": {
            "task": "app.tasks.crawl_tasks.run_incremental_crawls",
            "schedule": crontab(minute="*/30"),
        },
        "process-ai-queue": {
            "task": "app.tasks.ai_tasks.process_pending_articles",
            "schedule": crontab(minute="*/15"),
        },
        "incremental-index": {
            "task": "app.tasks.index_tasks.incremental_reindex",
            "schedule": crontab(minute="*/10"),
        },
        "daily-backup": {
            "task": "app.tasks.backup_tasks.run_database_backup",
            "schedule": crontab(hour=3, minute=0),
        },
        "duplicate-detection": {
            "task": "app.tasks.ai_tasks.detect_duplicates_batch",
            "schedule": crontab(hour=4, minute=0),
        },
    },
)
