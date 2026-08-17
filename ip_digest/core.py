from __future__ import annotations

import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

CATEGORIES = ("网文", "短剧", "漫剧", "影游", "AIGC")

@dataclass(frozen=True)
class Item:
    title: str; link: str; published_at: datetime; source: str; category: str; region: str; summary: str; score: int

def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def load_watchlist(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items")
    if not isinstance(items, list):
        raise ValueError("社媒白名单缺少 items 列表")
    required = {"id", "platform", "name", "category", "type", "focus", "search_term", "search_url", "enabled"}
    for item in items:
        if not isinstance(item, dict) or not required <= item.keys() or not item["search_url"].startswith("https://") or not isinstance(item["enabled"], bool):
            raise ValueError("社媒白名单存在不完整条目")
    return items

def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(value or ""))).strip()

def normalized_link(link: str) -> str:
    parts = urllib.parse.urlsplit(link)
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    kept = [(k, v) for k, v in query if not k.lower().startswith("utm_")]
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), urllib.parse.urlencode(kept), ""))

def fetch_source(source: dict, now: datetime, window_hours: int, keywords: list[str]) -> tuple[list[Item], str | None]:
    try:
        request = urllib.request.Request(source["url"], headers={"User-Agent": "IPIndustryDigest/0.1"})
        with urllib.request.urlopen(request, timeout=20) as response:
            root = ET.fromstring(response.read())
    except Exception as exc:
        return [], f"{source['name']}：{exc}"
    since = now - timedelta(hours=window_hours); items: list[Item] = []
    for node in root.findall("./channel/item"):
        date = node.findtext("pubDate")
        try: published = parsedate_to_datetime(date).astimezone(timezone.utc)
        except Exception: continue
        if not since <= published <= now: continue
        title = clean_text(node.findtext("title", "")); link = normalized_link(node.findtext("link", ""))
        if not title or not link: continue
        age = now - published; event_hits = sum(k.lower() in title.lower() for k in keywords)
        score = source["weight"] + min(event_hits, 3) * 10 + (6 if age < timedelta(hours=6) else 4 if age < timedelta(hours=12) else 2)
        summary = clean_text(node.findtext("description", ""))[:220]
        feed_source = node.findtext("source") or source["name"]
        items.append(Item(title, link, published, clean_text(feed_source), source["category"], source["region"], summary, score))
    return items, None

def select(items: list[Item], config: dict) -> dict[str, list[Item]]:
    dedup: dict[tuple[str, str], Item] = {}
    for item in items:
        key = (normalized_link(item.link), item.title.casefold())
        if key not in dedup or item.score > dedup[key].score: dedup[key] = item
    result = {category: [] for category in CATEGORIES}; caps = config["regional_target"]; maximum = config["max_items_per_section"]
    for category in CATEGORIES:
        pool = sorted((x for x in dedup.values() if x.category == category), key=lambda x: (-x.score, -x.published_at.timestamp()))
        china = [x for x in pool if x.region == "china"][:caps["china"]]
        overseas = [x for x in pool if x.region == "overseas"][:caps["overseas"]]
        chosen = china + overseas; used = set(chosen)
        result[category] = (chosen + [x for x in pool if x not in used])[:maximum]
    return result
