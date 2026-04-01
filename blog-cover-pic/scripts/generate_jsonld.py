#!/usr/bin/env python3
"""Generate JSON-LD Article structured data for a blog post."""

import argparse
import json
import os
from datetime import date


def build_jsonld(
    title: str,
    author: str,
    publish_date: str,
    slug: str,
    description: str,
    image_base_url: str,
    publisher_name: str,
    publisher_logo_url: str,
) -> dict:
    """Build a schema.org Article JSON-LD object."""
    image_base = image_base_url.rstrip("/")

    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description or title,
        "image": [
            f"{image_base}/{slug}-feature.png",
            f"{image_base}/{slug}-og.png",
            f"{image_base}/{slug}-google.png",
        ],
        "datePublished": publish_date,
        "dateModified": publish_date,
        "author": {
            "@type": "Person",
            "name": author,
        },
    }

    if publisher_name:
        publisher = {
            "@type": "Organization",
            "name": publisher_name,
        }
        if publisher_logo_url:
            publisher["logo"] = {
                "@type": "ImageObject",
                "url": publisher_logo_url,
            }
        data["publisher"] = publisher

    # mainEntityOfPage — derive page URL from image base URL and slug
    data["mainEntityOfPage"] = {
        "@type": "WebPage",
        "@id": f"{image_base.rsplit('/', 1)[0]}/{slug}",
    }

    return data


def main():
    parser = argparse.ArgumentParser(description="Generate JSON-LD Article structured data.")
    parser.add_argument("--title", required=True, help="Blog post title")
    parser.add_argument("--author", required=True, help="Author name")
    parser.add_argument("--date", required=True, help="Publish date (YYYY-MM-DD)")
    parser.add_argument("--slug", required=True, help="URL slug")
    parser.add_argument("--description", default="", help="Post description/summary")
    parser.add_argument("--image-base-url", required=True, help="Base URL where images will be hosted")
    parser.add_argument("--publisher-name", default="", help="Publisher/organization name")
    parser.add_argument("--publisher-logo-url", default="", help="Publisher logo URL")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    jsonld = build_jsonld(
        title=args.title,
        author=args.author,
        publish_date=args.date,
        slug=args.slug,
        description=args.description,
        image_base_url=args.image_base_url,
        publisher_name=args.publisher_name,
        publisher_logo_url=args.publisher_logo_url,
    )

    output_path = os.path.join(args.output_dir, f"{args.slug}-jsonld.json")
    with open(output_path, "w") as f:
        json.dump(jsonld, f, indent=2)

    print(f"JSON-LD written to: {output_path}")

    # Also print the <script> tag version for easy embedding
    print("\nEmbed in HTML <head>:")
    print(f'<script type="application/ld+json">')
    print(json.dumps(jsonld, indent=2))
    print("</script>")


if __name__ == "__main__":
    main()
