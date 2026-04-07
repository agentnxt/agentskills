# Liferay Digital Commerce — Integration Reference

## What Is Liferay Commerce?

Liferay DXP includes a full enterprise B2B/B2C commerce module. It's a
**Java/OSGi-based** platform combining DXP (Digital Experience Platform),
CMS, and commerce into one. Used heavily in enterprises, government, finance,
and manufacturing for complex B2B buying portals.

Docs: https://learn.liferay.com/w/commerce
Docker: `docker run -it -m 8g -p 8080:8080 liferay/dxp:2025.q1.6-lts`

---

## API Types

Liferay exposes three API approaches:

| Type | Path | Format | Recommended |
|---|---|---|---|
| **Headless REST APIs** | `/o/<api-name>/<version>/` | JSON (OpenAPI) | ✅ Yes |
| **GraphQL API** | `/o/graphql` | GraphQL | ✅ Yes |
| **Web Services (Service Builder)** | `/api/axis/...` | SOAP/XML | ❌ Legacy |

Explore all APIs at: `http://localhost:8080/o/api`

---

## Commerce API Namespaces

| Namespace | Covers |
|---|---|
| `headless-commerce-admin-catalog/v1.0` | Products, catalogs, options, SKUs |
| `headless-commerce-admin-order/v1.0` | Orders (admin-side) |
| `headless-commerce-admin-inventory/v1.0` | Warehouses, stock |
| `headless-commerce-admin-pricing/v1.0` | Price lists, discounts, promotions |
| `headless-commerce-admin-account/v1.0` | B2B buyer accounts |
| `headless-commerce-delivery-catalog/v1.0` | Storefront product browsing |
| `headless-commerce-delivery-cart/v1.0` | Storefront cart + checkout |

---

## Auth

Three options — Basic Auth for dev, OAuth2 for production:

```bash
# Basic Auth (dev/testing)
curl "http://localhost:8080/o/headless-commerce-admin-catalog/v1.0/catalogs" \
  --user "test@liferay.com:password"

# OAuth2 Bearer Token (production)
curl "http://localhost:8080/o/headless-commerce-admin-catalog/v1.0/catalogs" \
  -H "Authorization: Bearer <access_token>"
```

---

## Common Operations

### Get All Products
```bash
curl "http://localhost:8080/o/headless-commerce-admin-catalog/v1.0/products" \
  --user "admin@company.com:password"
```

### Create a Catalog
```bash
curl -X POST \
  "http://localhost:8080/o/headless-commerce-admin-catalog/v1.0/catalogs" \
  --user "admin@company.com:password" \
  -H "Content-Type: application/json" \
  -d '{
    "name": { "en_US": "My Catalog" },
    "currencyCode": "USD",
    "defaultLanguageId": "en_US"
  }'
```

### Java Client (for enterprise integrations)
```java
// Client JAR available at /o/api in your Liferay instance
CatalogResource.Builder builder = CatalogResource.builder();
CatalogResource catalogResource = builder
    .authentication("admin@company.com", "password")
    .build();

Page<Catalog> catalogs = catalogResource.getCatalogsPage(null, null, null, null);
```

---

## GraphQL

```bash
# Access GraphQL playground
http://localhost:8080/o/api  # select GraphQL tab

# Example query
curl -X POST "http://localhost:8080/o/graphql" \
  --user "admin@company.com:password" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ products { items { id name } } }"}'
```

---

## B2B Features (Key Differentiator)

Liferay Commerce's B2B capabilities are industry-leading:
- **Account hierarchy**: buyer orgs, sub-accounts, account groups
- **Custom price lists**: per-account or per-account-group pricing
- **Workflow approvals**: purchase order approval workflows
- **Order types**: purchase orders, quote requests
- **Buyer portal**: self-service order history, reordering, invoice management

---

## Headless Commerce Pattern

For headless storefronts (Next.js, React, etc.):

```javascript
// Storefront: browse catalog
const products = await fetch(
  "https://yoursite.com/o/headless-commerce-delivery-catalog/v1.0/channels/12345/products",
  { headers: { "Authorization": `Bearer ${guestToken}` } }
).then(r => r.json());

// Add to cart
const cart = await fetch(
  "https://yoursite.com/o/headless-commerce-delivery-cart/v1.0/carts",
  {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${userToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ channelId: 12345, currencyCode: "USD" })
  }
).then(r => r.json());
```

---

## Useful Links

- Commerce docs: https://learn.liferay.com/w/commerce
- Headless APIs: https://learn.liferay.com/w/dxp/integration/headless-apis
- Catalog API Basics: https://learn.liferay.com/w/commerce/product-management/developer-guide/catalog-api-basics
- API Explorer: `http://your-liferay-instance/o/api`
