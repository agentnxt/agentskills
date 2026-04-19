from tools.google_trends import GoogleTrendsTool


def test_google_trends_basic():
    tool = GoogleTrendsTool(keywords=["seo", "content marketing"])
    result = tool.fetch()
    assert isinstance(result, dict)
    for k in ["seo", "content marketing"]:
        # ensure keys present (order-insensitive)
        assert k in result
        assert isinstance(result[k], int)
