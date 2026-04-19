import requests


class BingSearchApiTool:
    """Minimal Bing Search API wrapper.

    - api_key: Bing Search API key (Azure Cognitive Services)
    - endpoint: Bing Search API endpoint (default v7.0/search)
    """

    def __init__(
        self, api_key: str, endpoint: str = "https://api.bing.microsoft.com/v7.0/search"
    ):
        self.api_key = api_key
        self.endpoint = endpoint

    def search(self, query: str, count: int = 10, language: str = "en-US"):
        params = {
            "q": query,
            "count": str(count),
            "mkt": language,
        }
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        resp = requests.get(self.endpoint, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
