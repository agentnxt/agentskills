# eBay Developer APIs — Integration Reference

## API Architecture

eBay has two API generations — always use RESTful APIs for new work:

| Type | Status | Use |
|---|---|---|
| **RESTful APIs** | Current (recommended) | All new integrations |
| **Trading API** | Legacy (SOAP/XML) | Legacy support only |
| **Finding API** | Legacy | Product search (migrate to Browse API) |

Docs: https://developer.ebay.com/develop/apis

---

## Auth: OAuth 2.0

eBay uses OAuth 2.0 with two flows:

**Application token** (Client Credentials) — for public data (no user context):
```bash
curl -X POST https://api.ebay.com/identity/v1/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Basic <base64(appId:certId)>" \
  -d "grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope"
```

**User token** (Authorization Code) — for seller operations:
```python
import requests
from base64 import b64encode

def get_user_token(code, app_id, cert_id, redirect_uri):
    credentials = b64encode(f"{app_id}:{cert_id}".encode()).decode()
    resp = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {credentials}"
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
    )
    return resp.json()  # access_token + refresh_token
```

---

## RESTful Sell APIs

| API | Base URL | Use Case |
|---|---|---|
| **Fulfillment API** | `/sell/fulfillment/v1` | Orders, shipments, refunds, disputes |
| **Inventory API** | `/sell/inventory/v1` | Listings, offers, inventory items |
| **Finances API** | `/sell/finances/v1` | Payouts, transactions, fees |
| **Marketing API** | `/sell/marketing/v1` | Promoted listings, campaigns |
| **Analytics API** | `/sell/analytics/v1` | Traffic, seller performance |
| **Account API** | `/sell/account/v1` | Policies, programs, subscriptions |
| **Feed API** | `/sell/feed/v1` | Bulk catalog data |
| **Logistics API** | `/sell/logistics/v1` | Shipping label purchase |

## RESTful Buy APIs (Buyer-facing)

| API | Use Case |
|---|---|
| Browse API | Search products, get item details |
| Order API | Buyer checkout and orders |
| Marketing API | Promotions discovery |

---

## Common Workflow: Order Fulfillment

```python
import requests

BASE = "https://api.ebay.com/sell/fulfillment/v1"
HEADERS = {"Authorization": f"Bearer {access_token}"}

# 1. Get open orders
orders = requests.get(f"{BASE}/order",
    params={"filter": "orderfulfillmentstatus:{NOT_STARTED|IN_PROGRESS}"},
    headers=HEADERS).json()

# 2. Create shipping fulfillment (after packing)
order_id = orders["orders"][0]["orderId"]
fulfillment = requests.post(
    f"{BASE}/order/{order_id}/shipping_fulfillment",
    headers=HEADERS,
    json={
        "lineItems": [{"lineItemId": "xxx", "quantity": 1}],
        "shippedDate": "2026-03-22T10:00:00.000Z",
        "shippingCarrierCode": "USPS",
        "trackingNumber": "9400111899223397648506"
    })

# 3. Issue refund if needed
refund = requests.post(f"{BASE}/order/{order_id}/issue_refund",
    headers=HEADERS,
    json={
        "reasonForRefund": "BUYER_RETURN",
        "comment": "Item returned as requested",
        "refundItems": [{"lineItemId": "xxx", "refundAmount": {"value": "29.99", "currency": "USD"}}]
    })
```

---

## ⚠️ Important: Digital Signatures (EU/UK)

Since 2023, eBay requires **digital signatures** (Ed25519 or RSA) on certain
API calls for EU/UK sellers. Affected endpoints: `issueRefund`, finances, and
others processing financial data. Required headers:
`x-ebay-signature-key`, `x-signature`, `content-digest`.

```python
# Signing is required for EU/UK financial endpoints
# Use eBay's official SDK or the hendt/ebay-api Node.js library for easy signing
```

---

## Data Handling Note (Sep 2025)

Effective September 26, 2025: eBay no longer returns **username** data for
US users in order responses. An **immutable user ID** is returned instead.
Update any integrations that parse/store eBay usernames.

---

## Sandbox

Replace `api.ebay.com` with `api.sandbox.ebay.com`. Sandbox keys are separate
from production keys — generate them at https://developer.ebay.com

---

## Rate Limits

Rate limits vary by API and compatibility level. Check your app's level at
https://developer.ebay.com/my/products. Generally:
- Fulfillment API: 5,000 calls/day (standard)
- Inventory API: 500,000 calls/day (standard)
- Always check `X-RateLimit-Limit` and `X-RateLimit-Remaining` response headers

---

## Useful Links

- Developer portal: https://developer.ebay.com
- RESTful API guide: https://developer.ebay.com/api-docs/static/ebay-rest-landing.html
- Fulfillment API: https://developer.ebay.com/api-docs/sell/fulfillment/overview.html
- Node SDK: https://github.com/hendt/ebay-api
