"""RSS/XML feed crawler."""

import asyncio
from datetime import UTC, datetime

import aiohttp
import feedparser

from app.crawlers.base.crawler import BaseCrawler, CrawlItem, CrawlResult


class RSSCrawler(BaseCrawler):
    source_type = "rss"

    async def health_check(self) -> bool:
        feed_url = self.config.get("feed_url", self.config["base_url"])
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    return resp.status < 400
        except Exception:
            return False

    async def crawl(self, incremental: bool = True) -> CrawlResult:
        result = CrawlResult()
        feed_url = self.config.get("feed_url", self.config["base_url"])
        since = self.config.get("since") if incremental else None

        async with aiohttp.ClientSession(headers={"User-Agent": self.user_agent}) as session:
            async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                content = await resp.text()

        feed = feedparser.parse(content)
        max_items = self.config.get("max_articles", 100)

        for entry in feed.entries[:max_items]:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=UTC)

            if since and published and published.isoformat() < since:
                continue

            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            result.items.append(
                self._normalize_item(
                    CrawlItem(
                        url=entry.link,
                        title=entry.title,
                        content=summary,
                        author=getattr(entry, "author", None),
                        published_at=published,
                        external_id=getattr(entry, "id", entry.link),
                    )
                )
            )
            await asyncio.sleep(1.0 / self.rate_limit)

        result.pages_crawled = len(result.items)
        return result
