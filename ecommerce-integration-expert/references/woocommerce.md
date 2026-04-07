# WooCommerce — Integration Reference

## API Landscape (2025–2026)

WooCommerce now has **two distinct APIs** — know which to use:

| API | Endpoint Base | Auth | Use For |
|---|---|---|---|
| **WC REST API v3** | `/wp-json/wc/v3/` | Consumer Key/Secret (OAuth 1.0a or HTTPS Basic) | Admin integrations: ERP, order management, catalog sync |
| **Store API** (Blocks API) | `/wp-json/wc/store/v1/` | Nonce (frontend) | Headless storefronts, Cart+Checkout Blocks, mobile apps |

### ⚠️ Deprecation Alert
The **Legacy REST API** (pre-v3) has been removed from core since WooCommerce 9.0. If you need it, install the `woocommerce-legacy-rest-api` plugin. Legacy webhooks configured to use it also stop working without the plugin. Strongly recommend migrating to v3.

---

## WC REST API v3 — Auth & Setup

**Prerequisites:**
- WooCommerce 3.5+, WordPress 4.4+
- Pretty permalinks enabled (not "Plain") in Settings → Permalinks

```python
# Python — using requests
import requests
from requests_oauthlib import OAuth1

consumer_key = "ck_xxxx"
consumer_secret = "cs_xxxx"
base_url = "https://yourstore.com/wp-json/wc/v3"

auth = OAuth1(consumer_key, consumer_secret)

# List orders
orders = requests.get(f"{base_url}/orders", auth=auth).json()

# Create a product
product = requests.post(f"{base_url}/products", auth=auth, json={
    "name": "My Product",
    "type": "simple",
    "regular_price": "29.99",
    "stock_quantity": 100,
    "manage_stock": True
}).json()
```

```javascript
// Node.js — official client
const WooCommerceRestApi = require("@woocommerce/woocommerce-rest-api").default;

const api = new WooCommerceRestApi({
  url: "https://yourstore.com",
  consumerKey: "ck_xxxx",
  consumerSecret: "cs_xxxx",
  version: "wc/v3"
});

// Get orders
const { data } = await api.get("orders", { status: "processing", per_page: 20 });

// Update order status
await api.put(`orders/${orderId}`, { status: "completed" });
```

---

## WC REST API v3 — Key Endpoints

| Resource | Endpoint | Common Operations |
|---|---|---|
| Orders | `/orders` | GET list, GET by ID, PUT status, POST refund |
| Products | `/products` | CRUD, variations, attributes |
| Customers | `/customers` | GET, CREATE, UPDATE |
| Coupons | `/coupons` | CRUD |
| Shipping | `/shipping/zones` | Zones, methods, locations |
| Reports | `/reports/sales` | Sales, top sellers, totals |
| Webhooks | `/webhooks` | CREATE, LIST, DELETE |

---

## Store API — Headless / Blocks

The Store API powers WooCommerce Blocks (Cart Block, Checkout Block) and is
designed for **unauthenticated frontend consumers**. Lives at `/wp-json/wc/store/v1/`.

```javascript
// Add to cart (no auth needed, uses nonce)
const nonce = await fetch("/wp-json/wc/store/v1/cart/nonce")
  .then(r => r.json()).then(d => d.nonce);

await fetch("/wp-json/wc/store/v1/cart/add-item", {
  method: "POST",
  headers: { "Nonce": nonce, "Content-Type": "application/json" },
  body: JSON.stringify({ id: 123, quantity: 1 })
});

// Checkout
await fetch("/wp-json/wc/store/v1/checkout", {
  method: "POST",
  headers: { "Nonce": nonce, "Content-Type": "application/json" },
  body: JSON.stringify({
    payment_method: "stripe",
    billing_address: { first_name: "John", email: "john@example.com", ... },
    shipping_address: { ... }
  })
});
```

**Key benefit**: After Store API checkout, WooCommerce fires the same hooks as
classic checkout (`woocommerce_checkout_order_created`, etc.) — existing webhook
integrations work without modification.

---

## Webhooks

WooCommerce supports webhooks for: orders, products, customers, coupons.

**Built-in Topics:**
- `order.created`, `order.updated`, `order.deleted`
- `product.created`, `product.updated`, `product.deleted`
- `customer.created`, `customer.updated`, `customer.deleted`
- `coupon.created`, `coupon.updated`, `coupon.deleted`
- Custom: `action.woocommerce_add_to_cart`

**WooCommerce 10.4 (Dec 2025)**: Added webhook support for the **Agentic Commerce protocol** — WooCommerce stores can now participate in ACP/UCP flows automatically.

```javascript
// Create webhook via API
await api.post("webhooks", {
  name: "New Order",
  topic: "order.created",
  delivery_url: "https://your-app.com/hooks/wc-order"
});

// Verify incoming webhook (Node.js)
const crypto = require("crypto");
function verifyWebhook(rawBody, signature, secret) {
  const hash = crypto.createHmac("sha256", secret)
    .update(rawBody).digest("base64");
  return hash === signature;
}

app.post("/hooks/wc-order", express.raw({ type: "application/json" }), (req, res) => {
  const sig = req.headers["x-wc-webhook-signature"];
  if (!verifyWebhook(req.body, sig, process.env.WC_WEBHOOK_SECRET)) {
    return res.sendStatus(401);
  }
  const order = JSON.parse(req.body);
  // process order...
  res.sendStatus(200);
});
```

Webhook delivery via `wp-cron`. Headers sent: `X-WC-Webhook-Topic`,
`X-WC-Webhook-Resource`, `X-WC-Webhook-Event`, `X-WC-Webhook-Signature`.
Webhooks auto-disable after 5 consecutive failures.

---

## WooCommerce Performance Notes (2025–2026)

- **HPOS** (High Performance Order Storage) is now stable — enable for stores with high order volume, dramatically reduces DB load
- **Lazy-loaded REST namespaces**: `wc-admin` / `wc-analytics` now load on-demand, cutting TTFB by 30–60ms for headless/API consumers
- **Store API rate limiting**: Only POST requests on checkout endpoint are now rate-limited (fixed in WC 10.4 — PUT requests for payment method switching no longer count)
- **Interactivity API Mini Cart**: Now default in production (WC 10.4) — smaller JS bundles

---

## Useful Links

- REST API docs: https://woocommerce.github.io/woocommerce-rest-api-docs/
- Store API docs: https://github.com/woocommerce/woocommerce/tree/trunk/plugins/woocommerce/src/StoreApi
- Developer blog: https://developer.woocommerce.com/
- Legacy API migration guide: https://developer.woocommerce.com/2024/05/14/goodbye-legacy-rest-api/
