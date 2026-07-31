"""Crawler registry and factory."""

from app.crawlers.base.crawler import BaseCrawler
from app.crawlers.folklore.folklore_crawler import FolkloreCrawler
from app.crawlers.government.gov_crawler import GovernmentCrawler
from app.crawlers.missing_persons.missing_crawler import MissingPersonsCrawler
from app.crawlers.news.news_crawler import NewsCrawler
from app.crawlers.podcast.podcast_crawler import PodcastCrawler
from app.crawlers.rss.rss_crawler import RSSCrawler
from app.crawlers.youtube.youtube_crawler import YouTubeCrawler
from app.models.source import SourceType

CRAWLER_REGISTRY: dict[SourceType, type[BaseCrawler]] = {
    SourceType.NEWS: NewsCrawler,
    SourceType.RSS: RSSCrawler,
    SourceType.XML: RSSCrawler,
    SourceType.GOVERNMENT: GovernmentCrawler,
    SourceType.POLICE: GovernmentCrawler,
    SourceType.COURT: GovernmentCrawler,
    SourceType.MISSING_PERSONS: MissingPersonsCrawler,
    SourceType.FOLKLORE: FolkloreCrawler,
    SourceType.URBAN_LEGEND: FolkloreCrawler,
    SourceType.PODCAST: PodcastCrawler,
    SourceType.YOUTUBE: YouTubeCrawler,
    SourceType.API: RSSCrawler,
    SourceType.ACADEMIC: RSSCrawler,
    SourceType.NEWSPAPER_ARCHIVE: NewsCrawler,
    SourceType.PUBLIC_DOMAIN_BOOK: FolkloreCrawler,
}


def get_crawler(source_type: SourceType, config: dict) -> BaseCrawler:
    crawler_cls = CRAWLER_REGISTRY.get(source_type, RSSCrawler)
    return crawler_cls(config)
