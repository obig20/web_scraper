"""Folklore and urban legend archive crawler."""

from datetime import UTC, datetime

import aiohttp
from bs4 import BeautifulSoup

from app.crawlers.base.crawler import BaseCrawler, CrawlItem, CrawlResult


class FolkloreCrawler(BaseCrawler):
    source_type = "folklore"

    async def health_check(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.config["base_url"],
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    return resp.status < 400
        except Exception:
            return False

    async def crawl(self, incremental: bool = True) -> CrawlResult:
        result = CrawlResult()
        archive_url = self.config.get("archive_url", self.config["base_url"])
        selectors = self.config.get("selectors", {
            "entry": "article, .legend, .story, .folktale",
            "title": "h1, h2, .title",
            "content": "p, .narrative",
        })

        async with aiohttp.ClientSession(headers={"User-Agent": self.user_agent}) as session:
            async with session.get(archive_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                html = await resp.text()

        soup = BeautifulSoup(html, "lxml")
        for entry in soup.select(selectors["entry"])[: self.config.get("max_articles", 40)]:
            title_el = entry.select_one(selectors["title"])
            content_els = entry.select(selectors["content"])
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            slug = title.lower().replace(" ", "-")[:80]
            result.items.append(
                self._normalize_item(
                    CrawlItem(
                        url=f"{archive_url}#{slug}",
                        title=title,
                        content="\n\n".join(p.get_text(strip=True) for p in content_els),
                        published_at=datetime.now(UTC),
                        external_id=slug,
                        metadata={"category": "folklore"},
                    )
                )
            )

        result.pages_crawled = len(result.items)
        return result
