"""Government and police press release crawler."""

from datetime import UTC, datetime

import aiohttp
from bs4 import BeautifulSoup

from app.crawlers.base.crawler import BaseCrawler, CrawlItem, CrawlResult


class GovernmentCrawler(BaseCrawler):
    source_type = "government"

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
        releases_url = self.config.get("releases_url", self.config["base_url"])
        selectors = self.config.get("selectors", {
            "list_item": ".press-release, .news-item, article",
            "title": "h2, h3, .title",
            "content": ".body, .content, p",
            "date": ".date, time",
        })

        async with aiohttp.ClientSession(headers={"User-Agent": self.user_agent}) as session:
            async with session.get(releases_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                html = await resp.text()

        soup = BeautifulSoup(html, "lxml")
        for item_el in soup.select(selectors["list_item"])[: self.config.get("max_articles", 30)]:
            title_el = item_el.select_one(selectors["title"])
            content_els = item_el.select(selectors["content"])
            date_el = item_el.select_one(selectors["date"])
            link_el = item_el.select_one("a")

            if not title_el:
                continue

            url = link_el["href"] if link_el and link_el.get("href") else releases_url
            if not url.startswith("http"):
                from urllib.parse import urljoin
                url = urljoin(self.config["base_url"], url)

            result.items.append(
                self._normalize_item(
                    CrawlItem(
                        url=url,
                        title=title_el.get_text(strip=True),
                        content="\n".join(c.get_text(strip=True) for c in content_els) or title_el.get_text(),
                        published_at=datetime.now(UTC),
                        external_id=url.split("/")[-1],
                        metadata={"source_category": "government_press_release"},
                    )
                )
            )

        result.pages_crawled = len(result.items)
        return result
