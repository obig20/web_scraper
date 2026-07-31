"""Generic news website crawler using aiohttp + BeautifulSoup."""

import asyncio
from datetime import UTC, datetime
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from app.crawlers.base.crawler import BaseCrawler, CrawlItem, CrawlResult


class NewsCrawler(BaseCrawler):
    source_type = "news"

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
        selectors = self.config.get("selectors", {})
        article_links = self.config.get("article_urls", [])
        list_url = self.config.get("list_url", self.config["base_url"])
        link_selector = selectors.get("links", "article a")

        async with aiohttp.ClientSession(
            headers={"User-Agent": self.user_agent}
        ) as session:
            if not article_links:
                article_links = await self._fetch_links(session, list_url, link_selector)

            max_articles = self.config.get("max_articles", 50)
            for url in article_links[:max_articles]:
                try:
                    item = await self._fetch_article(session, url, selectors)
                    if item:
                        result.items.append(self._normalize_item(item))
                    result.pages_crawled += 1
                    await asyncio.sleep(1.0 / self.rate_limit)
                except Exception as exc:
                    result.errors.append(f"{url}: {exc}")

        return result

    async def _fetch_links(self, session: aiohttp.ClientSession, url: str, selector: str) -> list[str]:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            html = await resp.text()
        soup = BeautifulSoup(html, "lxml")
        base = self.config["base_url"]
        links = []
        for a in soup.select(selector):
            href = a.get("href")
            if href:
                full = urljoin(base, href)
                if full not in links:
                    links.append(full)
        return links

    async def _fetch_article(
        self, session: aiohttp.ClientSession, url: str, selectors: dict
    ) -> CrawlItem | None:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status >= 400:
                return None
            html = await resp.text()

        soup = BeautifulSoup(html, "lxml")
        title_sel = selectors.get("title", "h1")
        content_sel = selectors.get("content", "article p, .article-body p")
        date_sel = selectors.get("date", "time")

        title_el = soup.select_one(title_sel)
        content_els = soup.select(content_sel)
        date_el = soup.select_one(date_sel)

        if not title_el or not content_els:
            return None

        published = None
        if date_el and date_el.get("datetime"):
            try:
                published = datetime.fromisoformat(date_el["datetime"].replace("Z", "+00:00"))
            except ValueError:
                pass

        return CrawlItem(
            url=url,
            title=title_el.get_text(strip=True),
            content="\n\n".join(p.get_text(strip=True) for p in content_els),
            published_at=published or datetime.now(UTC),
            external_id=url.rstrip("/").split("/")[-1],
        )
