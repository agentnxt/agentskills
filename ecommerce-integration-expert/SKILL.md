---
did: skill:015
version: "1.0.0"
created: "2026-04-29"
name: ecommerce-integration-expert
description: >
  Expert on e-commerce integrations, APIs, and agentic commerce. Covers:
  Amazon SP-API (LWA/SigV4, orders, FBA, feeds, catalog, fulfillment),
  Google Merchant API v1 + UCP (Universal Commerce Protocol), OpenAI
  Agentic Commerce Protocol (ACP), Spree Commerce (Rails), Mercur
  (TypeScript marketplace), Shopify, WooCommerce, eBay, Walmart,
  BigCommerce. Trigger on: SP-API, FBA, LWA credentials, selling partner,
  sync inventory, pull orders, marketplace integration, list products,
  Google Merchant API, UCP, ChatGPT checkout, agentic commerce, ACP,
  Spree API, Mercur, multi-vendor marketplace, headless commerce, product
  feed, checkout API, delegated payments, or any e-commerce platform
  developer question. Always trigger for marketplace API integration
  tasks even if not explicitly requested.
---

# E-Commerce Integration Expert

Senior e-commerce integration engineer with expertise spanning traditional
marketplace APIs, modern headless/composable platforms, and the emerging
agentic commerce layer (ACP, UCP). Your job: guide developers from auth
through production, with working code and real-world guidance.

---

## 1. Platform Landscape (2025–2026)

### Traditional Marketplace APIs
| Platform | Auth | Docs |
|---|---|---|
| **Amazon SP-API** | LWA + AWS SigV4 | https://developer-docs.amazon.com/sp-api/ |
| **Google Merchant API v1** | OAuth 2.0 | https://developers.google.com/merchant/api |
| **Shopify Admin API** | OAuth 2.0 / API Key | https://shopify.dev/docs/api |
| **WooCommerce REST API** | OAuth 1.0a / API Keys | https://woocommerce.github.io/woocommerce-rest-api-docs/ |
| **eBay Developer APIs** | OAuth 2.0 | https://developer.ebay.com/develop/apis |
| **Walmart Marketplace** | Client Credentials | https://developer.walmart.com |
| **BigCommerce** | API Key / OAuth | https://developer.bigcommerce.com |

### Headless / OSS / Enterprise Platforms
| Platform | Stack | Best For |
|---|---|---|
| **Spree Commerce** | Ruby on Rails, API-first | Multi-store, B2B, headless |
| **Mercur** | TypeScript, event-driven | Multi-vendor marketplaces |
| **Liferay Commerce** | Java/OSGi, DXP-integrated | Enterprise B2B buying portals |
| **Medusa** | Node.js, modular | Composable commerce |

### Agentic Commerce Protocols (2025/2026)
| Protocol | Owner | Status |
|---|---|---|
| **ACP** (Agentic Commerce Protocol) | OpenAI + Stripe | Live Sep 2025; pivoted to app-based Mar 2026 |
| **UCP** (Universal Commerce Protocol) | Google + 20+ partners | Announced Jan 2026; waitlist open |

---

## 2. Amazon SP-API

### Authentication: LWA + SigV4

```python
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

def get_lwa_token(client_id, client_secret, refresh_token):
    resp = requests.post(
        "https://api.amazon.com/auth/o2/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return resp.json()["access_token"]

def signed_headers(method, url, access_token, aws_key, aws_secret, region="us-east-1"):
    creds = Credentials(aws_key, aws_secret)
    req = AWSRequest(method=method, url=url)
    SigV4Auth(creds, "execute-api", region).add_auth(req)
    req.headers["x-amz-access-token"] = access_token
    return dict(req.headers)
```

### SP-API Groups

| Group | Use Case | Version |
|---|---|---|
| Orders | Retrieve/manage buyer orders | v0 |
| Catalog Items | Search/get product data | v2022-04-01 |
| Listings Items | Create/update listings | v2021-08-01 |
| Feeds | Bulk inventory, pricing, listings | v2021-06-30 |
| Reports | Sales, inventory, settlement | v2021-06-30 |
| FBA Inventory | Real-time FBA stock | v1 |
| Fulfillment Outbound | MFN/MCF shipments | v2020-07-01 |
| Notifications | Real-time event subscriptions | v1 |
| Pricing | Competitive pricing | v0 |
| A+ Content | Enhanced brand content | v2020-11-01 |
| Data Kiosk | GraphQL analytics | v2023-11-15 |
| AWD | Amazon Warehousing & Distribution | v2024-05-09 |
| Shipping | Buy/track labels | v2 |

Full endpoint reference: https://developer-docs.amazon.com/sp-api/reference/welcome-to-api-references

### Regional Endpoints

| Region | Endpoint | Markets |
|---|---|---|
| NA | https://sellingpartnerapi-na.amazon.com | US, CA, MX |
| EU | https://sellingpartnerapi-eu.amazon.com | UK, DE, FR, IT, ES |
| FE | https://sellingpartnerapi-fe.amazon.com | JP, AU, SG |

For full workflows (orders, feeds, notifications, retry logic, sandbox), see
`references/sp-api-workflows.md`.

---

## 3. Google Merchant API v1 + UCP

### ⚠️ Deprecation Alert
The old **Content API for Shopping** shuts down **August 18, 2026**. All new
integrations must use **Merchant API v1** (GA since August 2025). The v1beta
was shut down February 28, 2026.

### Merchant API v1 — Sub-APIs

| Sub-API | Purpose |
|---|---|
| Products | Upload/manage product catalog |
| Inventory | Stock levels and pricing |
| Accounts | Merchant Center management |
| Reports | Click potential, performance analytics |
| Data Sources | Feed management (CSV/JSON) |
| Product Studio (alpha) | genAI product content generation |
| Checkout | Checkout settings for UCP |

### Auth (OAuth 2.0)

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file(
    "service-account.json",
    scopes=["https://www.googleapis.com/auth/content"]
)
service = build("merchantapi", "products_v1beta", credentials=credentials)
```

### Universal Commerce Protocol (UCP)

Google's open standard for agentic commerce — enables direct purchases inside
Google Search AI Mode and Gemini. Coalition includes Shopify, Walmart, Target,
Etsy, Wayfair, Adyen, Mastercard, Stripe, Visa, American Express, and 20+
global partners.

**Key UCP concepts:**
- Merchant stays Merchant of Record
- Capabilities: checkout, product discovery, discounts (pick what you support)
- Transports: REST API binding or MCP binding — choose per your stack
- Compatible with Agent Payments Protocol (AP2) for secure agentic payments

**Integration steps:**
1. Prepare Merchant Center account + configure product feed
2. Set up Google Pay (get your Merchant ID)
3. Implement UCP Checkout Capability (REST or MCP binding)
4. Join waitlist → approval → live on AI Mode + Gemini

Docs: https://developers.google.com/merchant/ucp

---

## 4. OpenAI Agentic Commerce Protocol (ACP)

### Current Status (March 2026)

ACP launched Sep 2025. OpenAI removed native Instant Checkout from ChatGPT
product listings in March 2026, now focusing on **retailer app-based checkout**
(Instacart, Target, Expedia). The ACP spec remains open-source (Apache 2.0).

**Platform shortcuts:**
- **Shopify merchants**: Shopify manages ACP — just apply at chatgpt.com/merchants
- **Etsy US sellers**: automatically live, no action needed
- **Large retailers**: build a ChatGPT App using ACP endpoints
- **Others**: wait for broader rollout or focus on UCP

### ACP Architecture

| Component | Purpose |
|---|---|
| Product Feeds | Daily CSV/JSON catalog sent to OpenAI |
| Agentic Checkout API | REST endpoints on your server |
| Delegated Payment Spec | Secure token flow via Stripe/PayPal/Adyen |

### ACP Checkout Flow

```
User asks ChatGPT → feed lookup → POST /checkout on your server →
return session state → ChatGPT renders UI → user confirms →
delegated payment token sent → you charge via PSP → return order
confirmation → ChatGPT shows to user
```

```python
# Minimal ACP Checkout endpoint (Flask)
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/checkout", methods=["POST"])
def create_checkout():
    body = request.json
    order = create_order_in_your_system(body)
    return jsonify({
        "checkoutSessionId": order["id"],
        "status": "PENDING_PAYMENT",
        "lineItems": order["items"],
        "shippingOptions": order["shipping"],
        "total": order["total"],
        "currency": "USD"
    })

@app.route("/checkout/<sid>/confirm", methods=["POST"])
def confirm_checkout(sid):
    token = request.json["delegatedPaymentToken"]
    charge_via_stripe(token)
    return jsonify({"status": "CONFIRMED", "orderId": "..."})
```

Docs: https://developers.openai.com/commerce
Spec: https://developers.openai.com/commerce/guides/key-concepts

---

## 5. Spree Commerce

Mature open-source Rails e-commerce framework (15k+ GitHub stars), used by
Bonobos, Bookshop.org, GoDaddy, KFC, On Cloud, Square, and 5000+ businesses.

### Key Capabilities
- Headless: full JSON Store API
- Multi-store, multi-currency, multi-language out of the box
- B2B: buyer orgs, custom pricing, approval workflows
- Marketplace via Enterprise Edition
- Spree 5.3: Price Lists, Customer Groups, Events & Subscribers Engine

### Store API — Quick Reference

```bash
# Auth
curl -X POST https://your-store.com/api/v2/user/sessions \
  -H "Content-Type: application/json" \
  -d '{"spree_user": {"email": "user@example.com", "password": "secret"}}'
```

```python
import requests

BASE = "https://your-store.com/api/v2/storefront"
TOKEN = "Bearer <your_token>"

# Products
products = requests.get(f"{BASE}/products",
    headers={"Authorization": TOKEN}).json()

# Cart
cart = requests.post(f"{BASE}/cart",
    headers={"Authorization": TOKEN}).json()
order_token = cart["data"]["attributes"]["token"]

# Add item
requests.post(f"{BASE}/cart/add_item",
    headers={"Authorization": TOKEN,
             "X-Spree-Order-Token": order_token},
    json={"variant_id": "123", "quantity": 1})
```

Docs: https://spreecommerce.org/docs/api-reference/store-api/introduction
GitHub: https://github.com/spree/spree

---

## 6. Mercur — Open Source Marketplace Platform

TypeScript-first, event-driven, API-first marketplace platform. Mercur v2.0
(2026) is AI-native. Can run standalone or connect to existing Shopify/Magento
stores via **Mercur Connect**.

### Architecture

| Component | Role |
|---|---|
| Mercur Core | Modular marketplace engine |
| Admin Panel | Operator control, vendor oversight |
| Vendor Panel | Seller catalog, orders, payouts |
| Mercur Connect | Sync from Shopify, Magento, or custom platforms |
| Storefronts | Multi-vendor cart + unified checkout |

### Deployment Models

| Mode | Best For |
|---|---|
| **Standalone** | Greenfield marketplace, full ownership |
| **Connected** | Existing store adding a marketplace layer |

### Quick Start

```bash
git clone https://github.com/mercurjs/mercur
cd mercur && cp .env.example .env
# Configure: DATABASE_URL, REDIS_URL, S3 bucket in .env
docker-compose up
```

```typescript
// Create product via Mercur Vendor API
const res = await fetch("/vendor/products", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${vendorToken}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    title: "My Product",
    variants: [{ price: 2999, inventory_quantity: 50 }]
  })
});
```

Docs: https://docs.mercurjs.com | GitHub: https://github.com/mercurjs

---

## 7. WooCommerce

WooCommerce has two APIs — use the right one:

| API | Endpoint | Auth | Use |
|---|---|---|---|
| **REST API v3** | `/wp-json/wc/v3/` | Consumer Key + Secret | Admin: orders, products, ERP sync |
| **Store API** | `/wp-json/wc/store/v1/` | Nonce (frontend) | Headless storefronts, Blocks, mobile apps |

⚠️ **Legacy REST API** removed from core since WC 9.0. Install `woocommerce-legacy-rest-api` plugin if still needed; plan migration to v3.

**WooCommerce 10.4 (Dec 2025)** adds: ACP/UCP webhook support, HPOS caching (stable), lazy-loaded wc-admin namespace (saves 30–60ms TTFB), Store API rate limiting fixed.

For full code examples (auth, orders, webhooks, webhook verification, Store API cart/checkout), see `references/woocommerce.md`.

---

## 8. eBay RESTful APIs

eBay's current API suite is REST/OAuth 2.0 based. Key sell-side APIs:

| API | Base URL | Use |
|---|---|---|
| Fulfillment | `/sell/fulfillment/v1` | Orders, shipments, refunds, disputes |
| Inventory | `/sell/inventory/v1` | Listings, offers, stock |
| Finances | `/sell/finances/v1` | Payouts, fees (requires digital sig for EU/UK) |
| Marketing | `/sell/marketing/v1` | Promoted listings |
| Feed | `/sell/feed/v1` | Bulk catalog data |

⚠️ **Digital Signatures (Ed25519/RSA)** now required for EU/UK financial endpoints (refunds, payouts). ⚠️ **Sep 2025**: username field in orders replaced with immutable user ID for US users — update any integrations storing eBay usernames.

For full code examples (OAuth, get orders, create shipping fulfillment, issue refund, signing), see `references/ebay.md`.

---

## 9. Liferay Digital Commerce

Liferay DXP is a Java-based enterprise platform combining CMS, portal, and
commerce. Favoured in enterprise B2B, government, and manufacturing.

**API types:**
- **Headless REST** () — OpenAPI-compliant, recommended
- **GraphQL** () — flexible querying
- **Service Builder Web Services** — legacy SOAP, avoid for new work

**Commerce API namespaces:**
-  — products, catalogs, SKUs
-  — order management
-  — price lists, discounts
-  — storefront cart + checkout

**B2B strengths**: account hierarchies, per-account price lists, purchase order approval workflows, buyer self-service portal.

For full code examples and Java client patterns, see `references/liferay.md`.

---

## 10. Agentic Commerce: 2026 State of Play

The space is moving fast. Here's the honest picture:

| Protocol | Status | Developer Action |
|---|---|---|
| **ACP (OpenAI+Stripe)** | Native checkout removed Mar 2026; app-based model continues | Build ChatGPT App for your brand if you're a large retailer |
| **UCP (Google)** | Waitlist open Jan 2026; coalition of 20+ retailers | Join waitlist at developers.google.com/merchant/ucp |
| **Amazon+OpenAI** | Strategic partnership Feb 2026 ($50B investment) | Watch for Amazon feed integration announcements |
| **Shopify** | Catalog syndication to ChatGPT, Google AI Mode, Copilot | If on Shopify, product feeds flow automatically |

**Practical guidance for 2026:**
- Focus on UCP for Google AI Mode discovery (high search intent)
- Use Merchant API v1 to ensure product data is clean and rich
- If you're on Shopify, you get ChatGPT and Google syndication for free
- ACP direct integration now limited to large retailers with dedicated apps
- Most brands need BOTH ACP and UCP over time

For deep-dive on feed specs, payment flows, and protocol differences, see
`references/agentic-commerce.md`.

---

## 11. How to Help the User

1. **Identify platform** — ask if unclear (Amazon, Google, Spree, Mercur, agentic?)
2. **Identify use case** — orders, inventory, listings, fulfillment, agentic checkout?
3. **Identify language** — Python, TypeScript, Ruby, PHP — tailor code samples
4. **Walk through auth first** — most integration failures are auth issues
5. **Provide runnable code** — not pseudocode
6. **Flag deprecations proactively** — Google Content API sunsets Aug 2026
7. **Set realistic agentic expectations** — ACP pivoted, UCP still in waitlist
8. **Right tool for the job** — Feeds > looped Listings for bulk SP-API updates

---

## References

| File | Contents |
|---|---|
| `references/sp-api-workflows.md` | SP-API: orders, feeds, notifications, retry, sandbox |
| `references/sp-api-feeds.md` | SP-API feed types, full polling workflow |
| `references/agentic-commerce.md` | ACP vs UCP: feed specs, checkout endpoints, protocol matrix |
| `references/woocommerce.md` | WC REST v3, Store API, webhooks, HPOS, legacy migration |
| `references/ebay.md` | eBay OAuth, Fulfillment/Inventory/Finances APIs, digital signing |
| `references/liferay.md` | Liferay Commerce headless APIs, B2B features, Java client |
| `references/spree-mercur.md` | Spree and Mercur: setup, API patterns, multi-vendor |
