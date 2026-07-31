"""Base crawler interface for all source connectors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class CrawlItem:
    url: str
    title: str
    content: str
    author: str | None = None
    published_at: datetime | None = None
    external_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    media_urls: list[str] = field(default_factory=list)


@dataclass
class CrawlResult:
    items: list[CrawlItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    pages_crawled: int = 0


class BaseCrawler(ABC):
    """Abstract base for configurable source scrapers."""

    source_type: str = "generic"

    def __init__(self, source_config: dict[str, Any]) -> None:
        self.config = source_config
        self.rate_limit = source_config.get("rate_limit", 2.0)
        self.user_agent = source_config.get("user_agent", "CHRE-ResearchBot/1.0")
        self.proxy_url = source_config.get("proxy_url", "")
        self.respect_robots = source_config.get("respect_robots", True)

    @abstractmethod
    async def crawl(self, incremental: bool = True) -> CrawlResult:
        """Fetch and parse items from the configured source."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify source is reachable."""

    def _normalize_item(self, item: CrawlItem) -> CrawlItem:
        item.content = " ".join(item.content.split())
        if not item.published_at:
            item.published_at = datetime.now(UTC)
        return item
