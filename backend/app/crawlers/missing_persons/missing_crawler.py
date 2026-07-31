"""Missing persons database crawler."""

from datetime import UTC, datetime

import aiohttp
from bs4 import BeautifulSoup

from app.crawlers.base.crawler import BaseCrawler, CrawlItem, CrawlResult


class MissingPersonsCrawler(BaseCrawler):
    source_type = "missing_persons"

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
        api_url = self.config.get("api_url")
        list_url = self.config.get("list_url", self.config["base_url"])

        async with aiohttp.ClientSession(headers={"User-Agent": self.user_agent}) as session:
            if api_url:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    data = await resp.json()
                records = data if isinstance(data, list) else data.get("results", data.get("items", []))
                for record in records[: self.config.get("max_articles", 100)]:
                    result.items.append(
                        self._normalize_item(
                            CrawlItem(
                                url=record.get("url", f"{list_url}/{record.get('id', '')}"),
                                title=f"Missing: {record.get('name', 'Unknown')}",
                                content=self._format_record(record),
                                published_at=datetime.now(UTC),
                                external_id=str(record.get("id", record.get("case_number", ""))),
                                metadata={"record_type": "missing_person", "raw": record},
                            )
                        )
                    )
            else:
                async with session.get(list_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    html = await resp.text()
                soup = BeautifulSoup(html, "lxml")
                for row in soup.select(self.config.get("selectors", {}).get("row", "tr, .case-row"))[:50]:
                    cols = row.select("td, .field")
                    if len(cols) >= 2:
                        name = cols[0].get_text(strip=True)
                        details = " | ".join(c.get_text(strip=True) for c in cols[1:])
                        result.items.append(
                            self._normalize_item(
                                CrawlItem(
                                    url=list_url,
                                    title=f"Missing: {name}",
                                    content=details,
                                    published_at=datetime.now(UTC),
                                    metadata={"record_type": "missing_person"},
                                )
                            )
                        )

        result.pages_crawled = len(result.items)
        return result

    @staticmethod
    def _format_record(record: dict) -> str:
        parts = []
        for key in ("name", "age", "last_seen", "location", "description", "case_number", "status"):
            if record.get(key):
                parts.append(f"{key.replace('_', ' ').title()}: {record[key]}")
        return "\n".join(parts)
