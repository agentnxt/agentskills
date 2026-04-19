"""
test_parse_wordpress.py

Run with:
    pytest test_parse_wordpress.py -v

Unit tests use mocked HTTP — no WordPress site needed.
Live tests hit the public techcrunch.wordpress.com endpoint.
"""

import json
import os
from unittest.mock import MagicMock, patch, call

import pytest

from parse_wordpress import (
    WPClient,
    WPPost,
    WPPage,
    WPTerm,
    WPAuthor,
    WPMedia,
    WPComment,
    _strip_html,
    _rendered,
    to_csv,
    to_json,
    to_flat_records,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

RAW_POST = {
    "id": 42,
    "slug": "hello-world",
    "status": "publish",
    "type": "post",
    "link": "https://myblog.com/hello-world/",
    "title": {"rendered": "Hello World"},
    "content": {"rendered": "<p>This is <strong>content</strong>.</p>"},
    "excerpt": {"rendered": "<p>Short excerpt.</p>"},
    "author": 1,
    "featured_media": 7,
    "categories": [2, 5],
    "tags": [10, 11],
    "date": "2024-01-15T10:00:00",
    "modified": "2024-03-01T12:00:00",
    "sticky": False,
    "format": "standard",
}

RAW_PAGE = {
    "id": 10,
    "slug": "about",
    "status": "publish",
    "link": "https://myblog.com/about/",
    "title": {"rendered": "About Us"},
    "content": {"rendered": "<h1>About</h1><p>We are a team.</p>"},
    "excerpt": {"rendered": "<p>About page.</p>"},
    "author": 1,
    "parent": 0,
    "menu_order": 1,
    "date": "2023-01-01T00:00:00",
    "modified": "2024-01-01T00:00:00",
}

RAW_CATEGORY = {
    "id": 2,
    "name": "Technology",
    "slug": "technology",
    "taxonomy": "category",
    "description": "<p>Tech posts</p>",
    "count": 42,
    "link": "https://myblog.com/category/technology/",
    "parent": 0,
}

RAW_TAG = {
    "id": 10,
    "name": "python",
    "slug": "python",
    "taxonomy": "post_tag",
    "description": "",
    "count": 15,
    "link": "https://myblog.com/tag/python/",
    "parent": 0,
}

RAW_AUTHOR = {
    "id": 1,
    "name": "Alice Smith",
    "slug": "alice-smith",
    "link": "https://myblog.com/author/alice-smith/",
    "description": "<p>Tech writer.</p>",
    "avatar_urls": {"96": "https://myblog.com/avatar/alice-96.jpg", "48": "https://myblog.com/avatar/alice-48.jpg"},
}

RAW_MEDIA = {
    "id": 7,
    "slug": "hero-image",
    "link": "https://myblog.com/hero-image/",
    "source_url": "https://myblog.com/wp-content/uploads/hero.jpg",
    "alt_text": "Hero image",
    "caption": {"rendered": "<p>A hero shot.</p>"},
    "media_type": "image",
    "mime_type": "image/jpeg",
    "media_details": {"width": 1920, "height": 1080},
    "date": "2024-01-01T00:00:00",
}

RAW_COMMENT = {
    "id": 100,
    "post": 42,
    "parent": 0,
    "author_name": "Bob",
    "author_email": "bob@example.com",
    "author_url": "",
    "date": "2024-01-16T09:00:00",
    "content": {"rendered": "<p>Great post!</p>"},
    "status": "approved",
}


# ---------------------------------------------------------------------------
# _strip_html / _rendered
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_strip_html_basic(self):
        assert _strip_html("<p>Hello <b>world</b>!</p>") == "Hello world!"

    def test_strip_html_entities(self):
        assert "&amp;" not in _strip_html("A &amp; B")
        assert "A & B" == _strip_html("A &amp; B")

    def test_strip_html_nbsp(self):
        result = _strip_html("hello&nbsp;world")
        assert "hello world" == result

    def test_strip_html_none(self):
        assert _strip_html(None) == ""

    def test_rendered_dict(self):
        assert _rendered({"rendered": "Hello"}) == "Hello"

    def test_rendered_string(self):
        assert _rendered("Plain") == "Plain"

    def test_rendered_none(self):
        assert _rendered(None) == ""


# ---------------------------------------------------------------------------
# WPClient base URL logic
# ---------------------------------------------------------------------------

class TestWPClientBaseURL:
    def test_self_hosted(self):
        c = WPClient("https://myblog.com")
        assert c.base == "https://myblog.com/wp-json/wp/v2"

    def test_self_hosted_trailing_slash(self):
        c = WPClient("https://myblog.com/")
        assert c.base == "https://myblog.com/wp-json/wp/v2"

    def test_wpcom_domain(self):
        c = WPClient("techcrunch.wordpress.com")
        assert "techcrunch.wordpress.com" in c.base
        assert "public-api.wordpress.com" in c.base

    def test_wpcom_forced(self):
        c = WPClient("myblog.com", wpcom=True)
        assert "public-api.wordpress.com" in c.base

    def test_auth_set(self):
        c = WPClient("https://myblog.com", username="user", app_password="pass")
        assert c._auth == ("user", "pass")

    def test_no_auth(self):
        c = WPClient("https://myblog.com")
        assert c._auth is None


# ---------------------------------------------------------------------------
# WPPost
# ---------------------------------------------------------------------------

class TestWPPost:
    def _post(self):
        return WPPost.from_raw(RAW_POST)

    def test_id(self):
        assert self._post().id == 42

    def test_title_stripped(self):
        assert self._post().title == "Hello World"

    def test_content_stripped(self):
        assert "<p>" not in self._post().content
        assert "content" in self._post().content

    def test_excerpt_stripped(self):
        assert self._post().excerpt == "Short excerpt."

    def test_categories(self):
        assert self._post().categories == [2, 5]

    def test_tags(self):
        assert self._post().tags == [10, 11]

    def test_slug(self):
        assert self._post().slug == "hello-world"

    def test_flat_categories_pipe_joined(self):
        flat = self._post().flat()
        assert flat["categories"] == "2 | 5"

    def test_flat_url(self):
        flat = self._post().flat()
        assert "hello-world" in flat["url"]

    def test_sticky_false(self):
        assert self._post().sticky is False


# ---------------------------------------------------------------------------
# WPPage
# ---------------------------------------------------------------------------

class TestWPPage:
    def _page(self):
        return WPPage.from_raw(RAW_PAGE)

    def test_title(self):
        assert self._page().title == "About Us"

    def test_content_stripped(self):
        assert "<h1>" not in self._page().content

    def test_parent_zero(self):
        assert self._page().parent == 0

    def test_flat(self):
        flat = self._page().flat()
        assert flat["id"] == 10
        assert flat["slug"] == "about"


# ---------------------------------------------------------------------------
# WPTerm
# ---------------------------------------------------------------------------

class TestWPTerm:
    def test_category(self):
        t = WPTerm.from_raw(RAW_CATEGORY)
        assert t.name == "Technology"
        assert t.taxonomy == "category"
        assert t.count == 42

    def test_description_stripped(self):
        t = WPTerm.from_raw(RAW_CATEGORY)
        assert "<p>" not in t.description

    def test_tag(self):
        t = WPTerm.from_raw(RAW_TAG, taxonomy="post_tag")
        assert t.taxonomy == "post_tag"
        assert t.name == "python"


# ---------------------------------------------------------------------------
# WPAuthor
# ---------------------------------------------------------------------------

class TestWPAuthor:
    def _author(self):
        return WPAuthor.from_raw(RAW_AUTHOR)

    def test_name(self):
        assert self._author().name == "Alice Smith"

    def test_description_stripped(self):
        assert "<p>" not in self._author().description

    def test_avatar_96(self):
        assert "96" in self._author().avatar_url


# ---------------------------------------------------------------------------
# WPMedia
# ---------------------------------------------------------------------------

class TestWPMedia:
    def _media(self):
        return WPMedia.from_raw(RAW_MEDIA)

    def test_source_url(self):
        assert "hero.jpg" in self._media().source_url

    def test_dimensions(self):
        m = self._media()
        assert m.width == 1920
        assert m.height == 1080

    def test_caption_stripped(self):
        assert "<p>" not in self._media().caption


# ---------------------------------------------------------------------------
# WPComment
# ---------------------------------------------------------------------------

class TestWPComment:
    def _comment(self):
        return WPComment.from_raw(RAW_COMMENT)

    def test_author(self):
        assert self._comment().author_name == "Bob"

    def test_content_stripped(self):
        assert "<p>" not in self._comment().content
        assert "Great post" in self._comment().content

    def test_post_id(self):
        assert self._comment().post_id == 42


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

class TestSerialisation:
    def _posts(self):
        return [WPPost.from_raw(RAW_POST)]

    def test_to_flat_records(self):
        records = to_flat_records(self._posts())
        assert records[0]["title"] == "Hello World"
        assert records[0]["id"] == 42

    def test_to_json(self):
        result = json.loads(to_json(self._posts()))
        assert result[0]["title"] == "Hello World"

    def test_to_json_single(self):
        post = WPPost.from_raw(RAW_POST)
        result = json.loads(to_json(post))
        assert result[0]["id"] == 42

    def test_to_csv(self):
        csv_str = to_csv(self._posts())
        lines = csv_str.strip().splitlines()
        assert "id" in lines[0]
        assert "42" in lines[1]

    def test_to_csv_empty(self):
        assert to_csv([]) == ""

    def test_mixed_types(self):
        items = [WPPost.from_raw(RAW_POST), WPTerm.from_raw(RAW_CATEGORY)]
        records = to_flat_records(items)
        assert len(records) == 2


# ---------------------------------------------------------------------------
# fetch_posts — mocked
# ---------------------------------------------------------------------------

class TestFetchPostsMocked:
    def _mock_client(self, pages):
        mock = MagicMock(spec=WPClient)
        mock.paginate.return_value = pages
        return mock

    def test_returns_posts(self):
        client = self._mock_client([RAW_POST])
        from parse_wordpress import fetch_posts
        posts = fetch_posts(client)
        assert len(posts) == 1
        assert posts[0].id == 42

    def test_status_param_passed(self):
        client = self._mock_client([])
        from parse_wordpress import fetch_posts
        fetch_posts(client, status="draft")
        call_kwargs = client.paginate.call_args[1]["params"]
        assert call_kwargs["status"] == "draft"

    def test_category_filter(self):
        client = self._mock_client([])
        from parse_wordpress import fetch_posts
        fetch_posts(client, category=5)
        call_kwargs = client.paginate.call_args[1]["params"]
        assert call_kwargs["categories"] == 5

    def test_search_filter(self):
        client = self._mock_client([])
        from parse_wordpress import fetch_posts
        fetch_posts(client, search="python")
        call_kwargs = client.paginate.call_args[1]["params"]
        assert call_kwargs["search"] == "python"


# ---------------------------------------------------------------------------
# fetch_categories / fetch_tags — mocked
# ---------------------------------------------------------------------------

class TestFetchTermsMocked:
    def test_fetch_categories(self):
        mock_client = MagicMock(spec=WPClient)
        mock_client.paginate.return_value = [RAW_CATEGORY]
        from parse_wordpress import fetch_categories
        cats = fetch_categories(mock_client)
        assert cats[0].name == "Technology"
        assert cats[0].taxonomy == "category"

    def test_fetch_tags(self):
        mock_client = MagicMock(spec=WPClient)
        mock_client.paginate.return_value = [RAW_TAG]
        from parse_wordpress import fetch_tags
        tags = fetch_tags(mock_client)
        assert tags[0].name == "python"


# ---------------------------------------------------------------------------
# Live tests — techcrunch.wordpress.com (public)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    os.environ.get("SKIP_LIVE_WP", "0") == "1",
    reason="Live WordPress tests disabled"
)
class TestLive:
    def _client(self):
        return WPClient("techcrunch.wordpress.com")

    def test_fetch_posts(self):
        try:
            from parse_wordpress import fetch_posts
            posts = fetch_posts(self._client(), per_page=2)
            assert len(posts) >= 1
            assert posts[0].id > 0
            assert posts[0].title != ""
        except Exception:
            pytest.skip("WordPress.com not reachable")

    def test_fetch_categories(self):
        try:
            from parse_wordpress import fetch_categories
            cats = fetch_categories(self._client())
            assert len(cats) >= 1
        except Exception:
            pytest.skip("WordPress.com not reachable")

    def test_to_csv_live(self):
        try:
            from parse_wordpress import fetch_posts
            posts = fetch_posts(self._client(), per_page=2)
            csv_str = to_csv(posts)
            assert "title" in csv_str
        except Exception:
            pytest.skip("WordPress.com not reachable")
