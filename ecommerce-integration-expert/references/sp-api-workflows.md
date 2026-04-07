# Amazon SP-API — Common Workflows

## Pull Unshipped Orders

```python
import requests

BASE = "https://sellingpartnerapi-na.amazon.com"

def get_orders(access_token, aws_key, aws_secret):
    url = f"{BASE}/orders/v0/orders"
    params = {
        "MarketplaceIds": "ATVPDKIKX0DER",
        "OrderStatuses": "Unshipped,PartiallyShipped",
        "CreatedAfter": "2024-01-01T00:00:00Z"
    }
    headers = signed_headers("GET", url, access_token, aws_key, aws_secret)
    return requests.get(url, params=params, headers=headers).json()
```

## Submit a Feed (Inventory Update)

```python
import json

def submit_feed(feed_type, payload, marketplace_ids, access_token, aws_key, aws_secret):
    # 1. Create feed document
    url = f"{BASE}/feeds/2021-06-30/documents"
    headers = signed_headers("POST", url, access_token, aws_key, aws_secret)
    doc = requests.post(url, headers=headers,
        json={"contentType": "application/json; charset=UTF-8"}).json()

    # 2. Upload to S3 pre-signed URL (no auth headers needed)
    requests.put(doc["url"],
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=UTF-8"})

    # 3. Submit feed
    url2 = f"{BASE}/feeds/2021-06-30/feeds"
    headers2 = signed_headers("POST", url2, access_token, aws_key, aws_secret)
    feed = requests.post(url2, headers=headers2, json={
        "feedType": feed_type,
        "marketplaceIds": marketplace_ids,
        "inputFeedDocumentId": doc["feedDocumentId"]
    }).json()
    return feed["feedId"]

def poll_feed(feed_id, access_token, aws_key, aws_secret, max_polls=20):
    import time
    for _ in range(max_polls):
        url = f"{BASE}/feeds/2021-06-30/feeds/{feed_id}"
        headers = signed_headers("GET", url, access_token, aws_key, aws_secret)
        resp = requests.get(url, headers=headers).json()
        if resp.get("processingStatus") in ("DONE", "FATAL", "CANCELLED"):
            return resp
        time.sleep(30)
    raise TimeoutError("Feed timed out")
```

## Subscribe to ORDER_CHANGE Notifications

```python
def create_sqs_destination(queue_arn, access_token, aws_key, aws_secret):
    url = f"{BASE}/notifications/v1/destinations"
    headers = signed_headers("POST", url, access_token, aws_key, aws_secret)
    return requests.post(url, headers=headers, json={
        "resourceSpecification": {
            "sqs": {"arn": queue_arn}
        },
        "name": "MyOrderNotifications"
    }).json()

def subscribe_to_notifications(notification_type, destination_id,
                                access_token, aws_key, aws_secret):
    url = f"{BASE}/notifications/v1/subscriptions/{notification_type}"
    headers = signed_headers("POST", url, access_token, aws_key, aws_secret)
    return requests.post(url, headers=headers, json={
        "payloadVersion": "1.0",
        "destinationId": destination_id
    }).json()

# Usage
sub = subscribe_to_notifications("ORDER_CHANGE", dest_id,
                                   access_token, aws_key, aws_secret)
```

## Rate Limit Retry

```python
import time

def with_retry(request_fn, max_retries=5):
    for attempt in range(max_retries):
        resp = request_fn()
        if resp.status_code == 429:
            wait = 2 ** attempt
            print(f"Rate limited, waiting {wait}s...")
            time.sleep(wait)
        elif resp.status_code >= 500:
            time.sleep(5)
        else:
            return resp
    raise Exception("Max retries exceeded")
```

## Sandbox Setup

Use sandbox URLs for testing:
- NA: `https://sandbox.sellingpartnerapi-na.amazon.com`

Sandbox requires specific test case parameters per endpoint. For example,
Orders in sandbox only returns results if you pass specific test `CreatedAfter`
values. See: https://developer-docs.amazon.com/sp-api/docs/the-selling-partner-api-sandbox

## Error Code Quick Reference

| Code | Meaning | Fix |
|---|---|---|
| `InvalidAccessToken` | LWA token expired | Refresh token |
| `AccessDenied` | Missing SP-API role | Request role in Developer Console |
| `QuotaExceeded` | Rate limited (429) | Exponential backoff |
| `InvalidInput` | Bad request body | Validate against schema |
| `ResourceNotFound` | Wrong ID or region | Check marketplace ID and endpoint |
| `Unauthorized` | SigV4 mismatch | Recheck AWS credentials and region |
