"""
News scraper using public RSS feeds — no API key required.
Parses BBC, Reuters, Science Daily, Al Jazeera, and more.
"""
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional
import asyncio
import re

FEEDS = {
    "world": [
        ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
        ("The Guardian", "https://www.theguardian.com/world/rss"),
    ],
    "regional": [
        ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
        ("Times of India", "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"),
    ],
    "science": [
        ("Science Daily", "https://www.sciencedaily.com/rss/top/science.xml"),
        ("NASA News", "https://www.nasa.gov/rss/dyn/breaking_news.rss"),
    ],
    "conflict": [
        ("Al Jazeera News", "https://www.aljazeera.com/xml/rss/all.xml"),
        ("CNBC World", "https://search.cnbc.com/rs/search/view.xml?partnerId=2000&keywords=conflict"),
    ],
    "technology": [
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ("Wired", "https://www.wired.com/feed/rss"),
    ],
}

def clean_html(text: str) -> str:
    """Strip HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text or "").strip()

def parse_rss(xml_text: str, source: str, limit: int = 5) -> list[dict]:
    """Parse RSS XML into list of article dicts."""
    items = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"media": "http://search.yahoo.com/mrss/"}
        channel = root.find("channel") or root
        for item in channel.findall(".//item")[:limit]:
            title = clean_html(item.findtext("title", ""))
            desc = clean_html(item.findtext("description", ""))
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            if title:
                items.append({
                    "title": title,
                    "description": desc[:200] + "..." if len(desc) > 200 else desc,
                    "url": link,
                    "source": source,
                    "published": pub_date,
                })
    except ET.ParseError:
        pass
    return items

async def fetch_feed(client: httpx.AsyncClient, name: str, url: str) -> list[dict]:
    """Fetch a single RSS feed."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; DashboardBot/1.0)"}
        r = await client.get(url, headers=headers, timeout=8, follow_redirects=True)
        if r.status_code == 200:
            return parse_rss(r.text, name)
    except Exception as e:
        print(f"Feed error [{name}]: {e}")
    return []

async def fetch_category(category: str) -> dict:
    """Fetch all feeds for a category concurrently."""
    feeds = FEEDS.get(category, [])
    async with httpx.AsyncClient() as client:
        tasks = [fetch_feed(client, name, url) for name, url in feeds]
        results = await asyncio.gather(*tasks)
    articles = [item for feed_items in results for item in feed_items]
    return {"category": category, "articles": articles, "count": len(articles)}

async def fetch_all_news(category: str = "all") -> dict:
    """Fetch all categories or a specific one."""
    if category != "all":
        data = await fetch_category(category)
        return {category: data}

    categories = list(FEEDS.keys())
    tasks = [fetch_category(cat) for cat in categories]
    results = await asyncio.gather(*tasks)
    return {cat: result for cat, result in zip(categories, results)}