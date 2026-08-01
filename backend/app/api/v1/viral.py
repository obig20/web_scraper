"""API endpoints for viral content fetching."""

from fastapi import APIRouter, HTTPException

from app.crawlers.viral_content import ViralContentFetcher

router = APIRouter()


@router.get("/viral-content")
async def fetch_viral_content():
    """Fetch viral crime and horror content for YouTube content creation."""
    try:
        config = {
            "rate_limit": 2.0,
            "user_agent": "CHRE-ResearchBot/1.0",
            "max_articles": 10,
        }
        
        fetcher = ViralContentFetcher(config)
        result = await fetcher.crawl()
        
        # Sort by viral score
        sorted_items = sorted(
            result.items, 
            key=lambda x: x.metadata.get("viral_score", 0), 
            reverse=True
        )
        
        return {
            "success": True,
            "items_found": len(sorted_items),
            "pages_crawled": result.pages_crawled,
            "errors": result.errors,
            "content": [
                {
                    "title": item.title,
                    "url": item.url,
                    "content": item.content[:500] + "..." if len(item.content) > 500 else item.content,
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                    "viral_score": item.metadata.get("viral_score", 0),
                    "youtube_potential": item.metadata.get("youtube_potential", {}),
                    "source": item.metadata.get("source", "unknown"),
                }
                for item in sorted_items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/viral-content/high-potential")
async def fetch_high_potential_content():
    """Fetch only high viral potential content (score > 70)."""
    try:
        config = {
            "rate_limit": 2.0,
            "user_agent": "CHRE-ResearchBot/1.0",
            "max_articles": 15,
        }
        
        fetcher = ViralContentFetcher(config)
        result = await fetcher.crawl()
        
        # Filter high potential items
        high_potential = [
            item for item in result.items 
            if item.metadata.get("viral_score", 0) > 70
        ]
        
        # Sort by viral score
        sorted_items = sorted(
            high_potential,
            key=lambda x: x.metadata.get("viral_score", 0),
            reverse=True
        )
        
        return {
            "success": True,
            "high_potential_items": len(sorted_items),
            "total_items_found": len(result.items),
            "content": [
                {
                    "title": item.title,
                    "url": item.url,
                    "content": item.content[:500] + "..." if len(item.content) > 500 else item.content,
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                    "viral_score": item.metadata.get("viral_score", 0),
                    "youtube_potential": item.metadata.get("youtube_potential", {}),
                    "source": item.metadata.get("source", "unknown"),
                }
                for item in sorted_items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/viral-content/topics")
async def get_trending_topics():
    """Get trending crime and horror topics."""
    # This would normally analyze fetched content to find trending topics
    trending_topics = [
        {
            "topic": "True Crime - Unsolved Mysteries",
            "viral_score": 85,
            "youtube_potential": "high",
            "competition": "medium",
            "estimated_views": "100K-500K"
        },
        {
            "topic": "Paranormal - Ghost Investigations",
            "viral_score": 78,
            "youtube_potential": "high", 
            "competition": "high",
            "estimated_views": "50K-300K"
        },
        {
            "topic": "Horror - Disturbing Discoveries",
            "viral_score": 72,
            "youtube_potential": "medium",
            "competition": "low",
            "estimated_views": "25K-150K"
        },
        {
            "topic": "Cold Cases - New Evidence",
            "viral_score": 68,
            "youtube_potential": "medium",
            "competition": "medium",
            "estimated_views": "30K-200K"
        }
    ]
    
    return {
        "success": True,
        "trending_topics": trending_topics
    }
