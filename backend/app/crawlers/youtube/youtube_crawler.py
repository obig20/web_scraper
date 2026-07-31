"""YouTube metadata crawler (public API / oEmbed)."""

from datetime import UTC, datetime

import aiohttp

from app.crawlers.base.crawler import BaseCrawler, CrawlItem, CrawlResult


class YouTubeCrawler(BaseCrawler):
    source_type = "youtube"

    async def health_check(self) -> bool:
        return bool(self.config.get("channel_id") or self.config.get("playlist_id"))

    async def crawl(self, incremental: bool = True) -> CrawlResult:
        result = CrawlResult()
        video_ids = self.config.get("video_ids", [])
        api_key = self.config.get("api_key", "")

        if api_key and self.config.get("channel_id"):
            video_ids.extend(await self._fetch_channel_videos(api_key))

        for vid in video_ids[: self.config.get("max_articles", 50)]:
            metadata = await self._fetch_metadata(vid)
            if metadata:
                result.items.append(self._normalize_item(metadata))
        result.pages_crawled = len(result.items)
        return result

    async def _fetch_channel_videos(self, api_key: str) -> list[str]:
        channel_id = self.config["channel_id"]
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?key={api_key}&channelId={channel_id}&part=id&order=date&maxResults=50&type=video"
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    data = await resp.json()
            return [item["id"]["videoId"] for item in data.get("items", []) if item.get("id", {}).get("videoId")]
        except Exception:
            return []

    async def _fetch_metadata(self, video_id: str) -> CrawlItem | None:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(oembed_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status >= 400:
                        return None
                    data = await resp.json()
            return CrawlItem(
                url=f"https://www.youtube.com/watch?v={video_id}",
                title=data.get("title", video_id),
                content=data.get("title", ""),
                author=data.get("author_name"),
                published_at=datetime.now(UTC),
                external_id=video_id,
                metadata={"platform": "youtube", "thumbnail": data.get("thumbnail_url")},
            )
        except Exception:
            return None
