"""Podcast metadata and transcript crawler."""

from datetime import UTC, datetime

import aiohttp
import feedparser

from app.crawlers.base.crawler import BaseCrawler, CrawlItem, CrawlResult


class PodcastCrawler(BaseCrawler):
    source_type = "podcast"

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

        async with aiohttp.ClientSession(headers={"User-Agent": self.user_agent}) as session:
            async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                content = await resp.text()

        feed = feedparser.parse(content)
        for entry in feed.entries[: self.config.get("max_articles", 50)]:
            transcript = ""
            transcript_url = None
            for link in getattr(entry, "links", []):
                if link.get("type") == "text/plain" or "transcript" in link.get("href", "").lower():
                    transcript_url = link["href"]
                    break

            if transcript_url:
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(transcript_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                            transcript = await resp.text()
                    except Exception:
                        pass

            summary = transcript or getattr(entry, "summary", "") or getattr(entry, "description", "")
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=UTC)

            result.items.append(
                self._normalize_item(
                    CrawlItem(
                        url=entry.link,
                        title=entry.title,
                        content=summary,
                        author=getattr(entry, "author", feed.feed.get("title")),
                        published_at=published or datetime.now(UTC),
                        external_id=getattr(entry, "id", entry.link),
                        metadata={"media_type": "podcast", "has_transcript": bool(transcript)},
                    )
                )
            )

        result.pages_crawled = len(result.items)
        return result
