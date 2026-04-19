# Agentic Commerce Deep-Dive (ACP + UCP)

## ACP vs UCP At A Glance

| | ACP (OpenAI + Stripe) | UCP (Google) |
|---|---|---|
| **Launch** | Sep 2025 | Jan 2026 (waitlist) |
| **Where** | ChatGPT (app-based, Mar 2026 pivot) | Google AI Mode + Gemini |
| **Auth model** | OpenAI approval + Stripe delegated payments | Google OAuth + Google Pay |
| **Merchant of Record** | Merchant | Merchant |
| **Fee** | ~4% transaction fee to OpenAI | TBD |
| **Open source** | Yes (Apache 2.0) | Yes |
| **Transport** | REST | REST or MCP binding |
| **PSP required** | Stripe (primary), PayPal, Adyen | Google Pay + existing PSP |
| **Onboarding** | Platform-specific (Shopify auto, Etsy auto, others apply) | Waitlist approval required |

---

## ACP — Product Feed Spec

Merchants provide a daily snapshot feed (CSV or JSON). Required fields:

```json
{
  "id": "SKU-12345",
  "title": "Wireless Headphones XZ-200",
  "description": "Premium noise-cancelling wireless headphones...",
  "link": "https://yourstore.com/products/xz-200",
  "image_link": "https://cdn.yourstore.com/xz200.jpg",
  "price": "99.99 USD",
  "availability": "in stock",
  "condition": "new",
  "brand": "YourBrand",
  "gtin": "012345678901",
  "shipping": [
    {
      "country": "US",
      "service": "Standard",
      "price": "0.00 USD"
    }
  ]
}
```

Send initial sample → OpenAI validates → daily snapshot thereafter.

---

## ACP — Checkout Session States

```
CREATED → SHIPPING_SELECTED → PAYMENT_PENDING → CONFIRMED
                                              → DECLINED
                             → CANCELLED
```

Your `/checkout` endpoint must handle these state transitions and
return the current state on every response.

---

## ACP — Delegated Payment Flow

```
1. OpenAI generates a one-time delegated payment request
   with max_chargeable_amount and expiry
2. OpenAI sends to merchant's PSP (Stripe/PayPal)
3. PSP returns a payment_token
4. OpenAI passes payment_token to merchant's /confirm endpoint
5. Merchant charges via PSP using token
6. Merchant returns CONFIRMED or DECLINED
```

**Key rule**: OpenAI is NOT the merchant of record. You charge and fulfill.

---

## UCP — Capability Model

Merchants choose which capabilities to expose:

| Capability | Description |
|---|---|
| `product_discovery` | Product search and catalog browsing |
| `checkout` | Direct purchase flow |
| `checkout.discounts` | Extension: apply member/promo discounts |
| `checkout.account_linking` | Extension: link buyer accounts for loyalty |

### UCP Checkout Capability (REST binding)

```json
{
  "capabilities": ["checkout"],
  "checkout": {
    "endpoint": "https://yourstore.com/ucp/checkout",
    "supported_payment_handlers": ["google_pay"],
    "merchant_id": "YOUR_GOOGLE_PAY_MERCHANT_ID"
  }
}
```

### UCP MCP Binding

For teams building on MCP, UCP can be exposed as an MCP server:

```json
{
  "mcp_server": {
    "url": "https://yourstore.com/mcp",
    "capabilities": ["checkout", "product_discovery"]
  }
}
```

---

## Platform Decision Matrix

| Scenario | Recommended |
|---|---|
| On Shopify, want AI discovery | Let Shopify handle both ACP + UCP |
| Large retailer, want ChatGPT app | Build ChatGPT App with ACP |
| Want Google AI Mode visibility | Join UCP waitlist, clean up Merchant API feeds |
| Building custom marketplace | Build your own ACP + UCP integrations |
| On Etsy US | Already live on ACP, no action needed |

---

## Useful Links

- ACP spec: https://developers.openai.com/commerce/guides/key-concepts
- ACP GitHub: https://github.com/openai/agentic-commerce-protocol
- UCP overview: https://developers.google.com/merchant/ucp
- UCP integration guide: https://developers.google.com/merchant/ucp/guides
- Google Merchant API updates: https://developers.google.com/merchant/api/latest-updates
