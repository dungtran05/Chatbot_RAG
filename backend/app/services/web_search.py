from tavily import TavilyClient

from app.core.config import settings


def tavily_search(query: str) -> list[dict]:
    if not settings.tavily_api_key:
        return []
    client = TavilyClient(api_key=settings.tavily_api_key)
    response = client.search(query=query, max_results=settings.tavily_max_results)
    results = response.get("results", [])
    return [
        {
            "source": item.get("url"),
            "title": item.get("title"),
            "text": item.get("content", ""),
            "source_type": "web",
        }
        for item in results
    ]

