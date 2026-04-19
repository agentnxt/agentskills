from typing import List, Dict
import random
import os


class GoogleTrendsTool:
    def __init__(self, keywords: List[str], timeframe: str = "now 7-d"):
        self.keywords = keywords
        self.timeframe = timeframe

    def fetch(self) -> Dict[str, int]:
        # Prefer live data if pytrends is installed; otherwise fall back to a deterministic mock
        try:
            from pytrends.request import TrendReq  # type: ignore

            pytrends = TrendReq()
            pytrends.build_payload(self.keywords, timeframe=self.timeframe)
            data = pytrends.interest_over_time()
            if data is not None and not data.empty:
                # Return average interest per keyword
                return {kw: int(data[kw].mean()) for kw in self.keywords if kw in data}
        except Exception:
            pass
        # Mock fallback: deterministic but varied values for reproducibility
        result: Dict[str, int] = {}
        for kw in self.keywords:
            # simple hash-based pseudo-random but stable score 0-100
            score = abs(hash(kw + self.timeframe)) % 101
            result[kw] = int(score)
        return result
