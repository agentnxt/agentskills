#!/bin/bash
# Autonomyx Web Crawler — dependency installer (Firecrawl edition)
set -e

echo "Installing Python dependencies..."
pip install requests firecrawl-py --break-system-packages

echo ""
echo "✅ Done. Usage:"
echo ""
echo "  Cloud (firecrawl.dev):"
echo "    export FIRECRAWL_API_KEY=fc-YOUR-KEY"
echo "    python scripts/crawl.py --url https://example.com --output ./output"
echo ""
echo "  Self-hosted (your Coolify VPS):"
echo "    export FIRECRAWL_URL=http://vps.agnxxt.com:3002"
echo "    export FIRECRAWL_API_KEY=dummy"
echo "    python scripts/crawl.py --url https://example.com --output ./output"
