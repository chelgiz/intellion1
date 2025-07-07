import os

import requests
from bs4 import BeautifulSoup
from typing import List
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NewsFetcher")

# ✅ RapidAPI Bing News
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
HEADERS_BING = {
    "X-BingApis-SDK": "true",
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "bing-news-search1.p.rapidapi.com"
}
BING_URL = "https://bing-news-search1.p.rapidapi.com/news/search"

# ✅ Google fallback (HTML)
HEADERS_GOOGLE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
GOOGLE_URL = "https://www.google.com/search?q={query}&tbm=nws&hl=en"


def fetch_news_bing(query: str, max_articles: int = 5) -> List[str]:
    try:
        params = {
            "q": query,
            "freshness": "Month",
            "textFormat": "Raw",
            "safeSearch": "Off",
            "count": max_articles,
            "mkt": "en-US"
        }
        response = requests.get(BING_URL, headers=HEADERS_BING, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        articles = data.get("value", [])
        results = [article["name"] for article in articles if "name" in article]
        logger.info(f"📰 Bing: найдено {len(results)} новостей для '{query}'")
        return results
    except Exception as e:
        logger.warning(f"⚠️ Bing API не сработал для '{query}': {e}")
        return []


def fallback_google_news(query: str, max_articles: int = 5) -> List[str]:
    try:
        url = GOOGLE_URL.format(query=query.replace(" ", "+"))
        response = requests.get(url, headers=HEADERS_GOOGLE, timeout=5)

        # Проверка на редирект к consent.google.com
        if "consent.google.com" in response.url:
            logger.warning(f"⚠️ Google требует согласие на cookies — парсинг невозможен для '{query}'")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for g in soup.find_all("div", class_="BVG0Nb"):
            text = g.get_text()
            if text:
                results.append(text.strip())
            if len(results) >= max_articles:
                break

        logger.info(f"📰 Google fallback: найдено {len(results)} новостей для '{query}'")
        time.sleep(1.0)
        return results

    except Exception as e:
        logger.warning(f"⚠️ Ошибка парсинга Google для '{query}': {e}")
        return []


def get_news(player_name: str) -> List[str]:
    query = player_name.strip()
    news = fetch_news_bing(query)
    if not news:
        logger.info(f"🔁 Пробуем Google-поиск для '{query}'")
        news = fallback_google_news(query)
    return news
