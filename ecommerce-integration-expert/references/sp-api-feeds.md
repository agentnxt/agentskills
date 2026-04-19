# SP-API Feeds Reference

## Feed Types

| Feed Type | Use |
|---|---|
| `JSON_LISTINGS_FEED` | Create/update listings (preferred) |
| `POST_INVENTORY_AVAILABILITY_DATA` | Update quantity |
| `POST_PRODUCT_PRICING_DATA` | Update prices |
| `POST_FLAT_FILE_LISTINGS_DATA` | Flat file listing creation |
| `POST_ORDER_ACKNOWLEDGEMENT_DATA` | Acknowledge orders |
| `POST_ORDER_FULFILLMENT_DATA` | Confirm shipment |

## Full Feeds Workflow (Python)

```python
import requests
import json

BASE_URL = "https://sellingpartnerapi-na.amazon.com"

def submit_feed(feed_type, feed_content, marketplace_ids, access_token, headers_fn):
    # 1. Create feed document
    doc_resp = requests.post(
        f"{BASE_URL}/feeds/2021-06-30/documents",
        headers=headers_fn("POST", f"{BASE_URL}/feeds/2021-06-30/documents"),
        json={"contentType": "application/json; charset=UTF-8"}
    ).json()
    upload_url = doc_resp["url"]
    doc_id = doc_resp["feedDocumentId"]

    # 2. Upload content
    requests.put(
        upload_url,
        data=json.dumps(feed_content).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=UTF-8"}
    )

    # 3. Submit feed
    feed_resp = requests.post(
        f"{BASE_URL}/feeds/2021-06-30/feeds",
        headers=headers_fn("POST", f"{BASE_URL}/feeds/2021-06-30/feeds"),
        json={
            "feedType": feed_type,
            "marketplaceIds": marketplace_ids,
            "inputFeedDocumentId": doc_id
        }
    ).json()
    return feed_resp["feedId"]

def poll_feed(feed_id, access_token, headers_fn, max_polls=20):
    import time
    for _ in range(max_polls):
        resp = requests.get(
            f"{BASE_URL}/feeds/2021-06-30/feeds/{feed_id}",
            headers=headers_fn("GET", f"{BASE_URL}/feeds/2021-06-30/feeds/{feed_id}")
        ).json()
        status = resp.get("processingStatus")
        if status in ("DONE", "FATAL", "CANCELLED"):
            return resp
        time.sleep(30)
    raise TimeoutError("Feed did not complete in time")
```

## JSON Listings Feed Example

```json
{
  "header": {
    "sellerId": "YOUR_SELLER_ID",
    "version": "2.0",
    "issueLocale": "en_US"
  },
  "messages": [
    {
      "messageId": 1,
      "sku": "MY-SKU-001",
      "operationType": "UPDATE",
      "productType": "PRODUCT",
      "attributes": {
        "item_quantity": [{ "value": 50, "fulfillment_channel_code": "DEFAULT" }],
        "purchasable_offer": [{ "currency": "USD", "our_price": [{ "schedule": [{ "value_with_tax": 29.99 }] }] }]
      }
    }
  ]
}
```
