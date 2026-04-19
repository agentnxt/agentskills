import json
import requests
from typing import List, Optional, Dict


class GoogleSearchConsoleTool:
    def __init__(
        self,
        site_url: str,
        credentials_path: Optional[str] = None,
        scopes: Optional[List[str]] = None,
    ):
        self.site_url = site_url
        self.credentials_path = credentials_path
        self.scopes = scopes or ["https://www.googleapis.com/auth/webmasters.readonly"]
        self.access_token = self._load_token()

    def _load_token(self) -> Optional[str]:
        if self.credentials_path:
            try:
                with open(self.credentials_path, "r") as f:
                    data = json.load(f)
                return data.get("access_token") or data.get("token")
            except Exception:
                return None
        return None

    def _auth_header(self) -> Dict[str, str]:
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    def list_sites(self) -> List[str]:
        url = "https://www.googleapis.com/webmasters/v3/sites/"
        resp = requests.get(url, headers=self._auth_header(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        sites = [s.get("siteUrl") for s in data.get("sites", [])]
        return sites

    def query(
        self,
        start_date: str,
        end_date: str,
        dimensions: List[str],
        row_limit: int = 1000,
        filters: Optional[Dict] = None,
    ) -> Dict:
        endpoint = f"https://www.googleapis.com/webmasters/v3/sites/{self.site_url}/searchAnalytics/query"
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": row_limit,
        }
        if filters:
            body["filters"] = filters
        resp = requests.post(
            endpoint, headers=self._auth_header(), json=body, timeout=15
        )
        resp.raise_for_status()
        return resp.json()
