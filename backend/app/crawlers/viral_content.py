"""Viral content fetcher for crime and horror stories."""

import asyncio
import feedparser
from datetime import UTC, datetime
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from app.crawlers.base.crawler import BaseCrawler, CrawlItem, CrawlResult


class ViralContentFetcher(BaseCrawler):
    """Fetches viral crime and horror content from various sources."""

    source_type = "viral_content"

    # RSS feeds for crime and horror news
    RSS_SOURCES = [
        "https://www.crimemuseum.org/feed/",  # Crime Museum
        "https://www.truecrimedaily.com/feed/",  # True Crime Daily
        "https://www.bleedingcool.com/feed/",  # Horror/Entertainment
        "https://bloody-disgusting.com/feed/",  # Horror news
        "https://www.dreadcentral.com/feed/",  # Horror Central
    ]

    # Direct news sources for crawling
    NEWS_SOURCES = [
        {
            "name": "True Crime Daily",
            "base_url": "https://www.truecrimedaily.com",
            "list_url": "https://www.truecrimedaily.com",
            "selectors": {
                "links": "h2.entry-title a",
                "title": "h1.entry-title",
                "content": ".entry-content p",
                "date": ".entry-date time",
            },
        },
        {
            "name": "Bloody Disgusting",
            "base_url": "https://bloody-disgusting.com",
            "list_url": "https://bloody-disgusting.com",
            "selectors": {
                "links": "h2.post-title a",
                "title": "h1.post-title",
                "content": ".post-content p",
                "date": ".post-date time",
            },
        },
    ]

    async def health_check(self) -> bool:
        """Check if at least one source is reachable."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://www.truecrimedaily.com",
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    return resp.status < 400
        except Exception:
            return False

    async def crawl(self, incremental: bool = True) -> CrawlResult:
        """Fetch content from RSS feeds and news sources."""
        result = CrawlResult()

        # Fetch from RSS feeds
        rss_items = await self._fetch_rss_feeds()
        result.items.extend(rss_items)

        # Fetch from news websites
        for source_config in self.NEWS_SOURCES:
            try:
                news_items = await self._fetch_news_source(source_config)
                result.items.extend(news_items)
                result.pages_crawled += 1
                await asyncio.sleep(1.0 / self.rate_limit)
            except Exception as exc:
                result.errors.append(f"{source_config['name']}: {exc}")

        # Analyze viral potential
        for item in result.items:
            item.metadata["viral_score"] = self._calculate_viral_score(item)
            item.metadata["youtube_potential"] = self._assess_youtube_potential(item)

        return result

    async def _fetch_rss_feeds(self) -> list[CrawlItem]:
        """Fetch and parse RSS feeds."""
        items = []
        for feed_url in self.RSS_SOURCES:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:  # Get latest 10 from each feed
                    item = CrawlItem(
                        url=entry.get("link", ""),
                        title=entry.get("title", ""),
                        content=entry.get("description", "") or entry.get("summary", ""),
                        published_at=self._parse_date(entry.get("published")),
                        external_id=entry.get("id", entry.get("link", "")),
                        metadata={"source": feed_url, "type": "rss"},
                    )
                    items.append(self._normalize_item(item))
            except Exception as exc:
                print(f"RSS feed error {feed_url}: {exc}")
        return items

    async def _fetch_news_source(self, source_config: dict[str, Any]) -> list[CrawlItem]:
        """Fetch articles from a news website."""
        items = []
        selectors = source_config["selectors"]

        async with aiohttp.ClientSession(
            headers={"User-Agent": self.user_agent}
        ) as session:
            # Fetch article links
            links = await self._fetch_links(session, source_config["list_url"], selectors["links"])
            
            max_articles = self.config.get("max_articles", 5)
            for url in links[:max_articles]:
                try:
                    item = await self._fetch_article(session, url, selectors)
                    if item:
                        item.metadata["source"] = source_config["name"]
                        item.metadata["type"] = "news"
                        items.append(self._normalize_item(item))
                    await asyncio.sleep(1.0 / self.rate_limit)
                except Exception as exc:
                    print(f"Article fetch error {url}: {exc}")

        return items

    async def _fetch_links(self, session: aiohttp.ClientSession, url: str, selector: str) -> list[str]:
        """Fetch article links from a listing page."""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                html = await resp.text()
            soup = BeautifulSoup(html, "lxml")
            links = []
            for a in soup.select(selector):
                href = a.get("href")
                if href and href.startswith("http"):
                    if href not in links:
                        links.append(href)
            return links
        except Exception as exc:
            print(f"Links fetch error: {exc}")
            return []

    async def _fetch_article(
        self, session: aiohttp.ClientSession, url: str, selectors: dict
    ) -> CrawlItem | None:
        """Fetch a single article."""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status >= 400:
                    return None
                html = await resp.text()

            soup = BeautifulSoup(html, "lxml")
            title_el = soup.select_one(selectors["title"])
            content_els = soup.select(selectors["content"])
            date_el = soup.select_one(selectors["date"])

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
        except Exception as exc:
            print(f"Article fetch error: {exc}")
            return None

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse date string from RSS feed."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _calculate_viral_score(self, item: CrawlItem) -> float:
        """Calculate viral potential score (0-100)."""
        score = 0.0
        title = item.title.lower()
        content = item.content.lower()

        # Viral keywords
        viral_keywords = [
            "shocking", "terrifying", "mysterious", "unsolved", "chilling",
            "haunting", "disturbing", "bizarre", "incredible", "shocking",
            "must see", "you won't believe", "caught on camera", "exclusive",
        ]

        # Crime/horror specific keywords
        genre_keywords = [
            "murder", "serial killer", "crime", "true crime", "horror",
            "paranormal", "ghost", " haunting", "creepy", "scary",
            "mystery", "disappearance", "cold case", "investigation",
        ]

        # Check for viral keywords in title
        for keyword in viral_keywords:
            if keyword in title:
                score += 5

        # Check for genre keywords
        for keyword in genre_keywords:
            if keyword in title:
                score += 3
            if keyword in content:
                score += 1

        # Length factors
        if 50 <= len(title) <= 100:  # Optimal title length
            score += 5
        if len(content) > 500:  # Substantial content
            score += 3

        # Recency factor
        if item.published_at:
            days_old = (datetime.now(UTC) - item.published_at).days
            if days_old <= 1:
                score += 10
            elif days_old <= 7:
                score += 5

        return min(score, 100)

    def _assess_youtube_potential(self, item: CrawlItem) -> dict[str, Any]:
        """Assess YouTube content potential."""
        viral_score = item.metadata.get("viral_score", 0)
        
        return {
            "overall_score": viral_score,
            "potential": "high" if viral_score > 70 else "medium" if viral_score > 40 else "low",
            "recommended_format": self._suggest_format(item),
            "estimated_views": self._estimate_views(viral_score),
            "competition_level": self._assess_competition(item),
        }

    def _suggest_format(self, item: CrawlItem) -> str:
        """Suggest YouTube content format."""
        title = item.title.lower()
        
        if "murder" in title or "serial killer" in title:
            return "True Crime Documentary"
        elif "ghost" in title or "haunting" in title or "paranormal" in title:
            return "Paranormal Investigation"
        elif "mystery" in title or "unsolved" in title:
            return "Mystery Analysis"
        elif "shocking" in title or "disturbing" in title:
            return "Reaction/Commentary"
        else:
            return "Storytelling/Narrative"

    def _estimate_views(self, viral_score: float) -> str:
        """Estimate potential YouTube views."""
        if viral_score > 80:
            return "100K-1M+"
        elif viral_score > 60:
            return "50K-500K"
        elif viral_score > 40:
            return "10K-100K"
        else:
            return "1K-50K"

    def _assess_competition(self, item: CrawlItem) -> str:
        """Assess competition level for the topic."""
        title = item.title.lower()
        
        high_competition_keywords = ["murder", "serial killer", "ghost", "haunting"]
        medium_competition_keywords = ["mystery", "crime", "paranormal", "creepy"]
        
        for keyword in high_competition_keywords:
            if keyword in title:
                return "high"
        
        for keyword in medium_competition_keywords:
            if keyword in title:
                return "medium"
        
        return "low"
