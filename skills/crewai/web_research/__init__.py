"""Web Research skill for CrewAI agents."""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, description="Max results to return")


class WebResearchTool(BaseTool):
    name: str = "web_research"
    description: str = "Search the web and return summarized results for a given query."
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str, max_results: int = 5) -> str:
        import requests

        # Uses SearXNG if available, falls back to DuckDuckGo
        searxng_url = self._get_searxng_url()
        if searxng_url:
            return self._search_searxng(searxng_url, query, max_results)
        return self._search_duckduckgo(query, max_results)

    def _get_searxng_url(self) -> str | None:
        import os
        return os.environ.get("SEARXNG_URL")

    def _search_searxng(self, base_url: str, query: str, max_results: int) -> str:
        import requests
        resp = requests.get(
            f"{base_url}/search",
            params={"q": query, "format": "json", "categories": "general"},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])[:max_results]
        return "\n\n".join(
            f"**{r['title']}**\n{r.get('content', 'No snippet')}\nURL: {r['url']}"
            for r in results
        )

    def _search_duckduckgo(self, query: str, max_results: int) -> str:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return "\n\n".join(
            f"**{r['title']}**\n{r['body']}\nURL: {r['href']}"
            for r in results
        )
