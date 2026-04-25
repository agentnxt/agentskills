# Metabase Dashboard Setup Reference

## Authentication

```
POST {METABASE_URL}/api/session
Content-Type: application/json

{"username": "{EMAIL}", "password": "{PASSWORD}"}

→ Response: {"id": "session-token-here"}
```

Use `X-Metabase-Session: {SESSION_TOKEN}` header for all subsequent requests.

---

## Data Source Connection

Before creating dashboards, ensure Metabase has a database connection to query Cloud Run metrics.

### Option 1: BigQuery (Recommended for GCP)

Export Cloud Monitoring metrics to BigQuery, then connect Metabase:

```
POST {METABASE_URL}/api/database
X-Metabase-Session: {SESSION_TOKEN}
Content-Type: application/json

{
  "engine": "bigquery-cloud-sdk",
  "name": "GCP Metrics - BigQuery",
  "details": {
    "project-id": "{GCP_PROJECT_ID}",
    "dataset-filters-type": "inclusion",
    "dataset-filters-patterns": "cloud_run_metrics",
    "service-account-json": "{SA_KEY_JSON_ESCAPED}"
  }
}
```

### Option 2: PostgreSQL (Cloud SQL or external)

```
POST {METABASE_URL}/api/database
X-Metabase-Session: {SESSION_TOKEN}
Content-Type: application/json

{
  "engine": "postgres",
  "name": "Cloud Run Metrics DB",
  "details": {
    "host": "{DB_HOST}",
    "port": 5432,
    "dbname": "{DB_NAME}",
    "user": "{DB_USER}",
    "password": "{DB_PASSWORD}",
    "ssl": true
  }
}
```

---

## Creating a Collection (Folder)

Organize dashboards in a collection:

```
POST {METABASE_URL}/api/collection
X-Metabase-Session: {SESSION_TOKEN}

{
  "name": "Cloud Run - {SERVICE_NAME}",
  "description": "Monitoring dashboards for {SERVICE_NAME}",
  "color": "#509EE3"
}
```

---

## Creating a Dashboard

```
POST {METABASE_URL}/api/dashboard
X-Metabase-Session: {SESSION_TOKEN}

{
  "name": "{SERVICE_NAME} - Service Health",
  "description": "Real-time health metrics for {SERVICE_NAME}",
  "collection_id": {COLLECTION_ID},
  "parameters": [
    {
      "name": "Time Range",
      "slug": "time_range",
      "id": "time_range",
      "type": "date/range"
    }
  ]
}
```

---

## Creating Questions (Cards)

Each metric becomes a "question" (card) in Metabase.

### Request Rate Card

```
POST {METABASE_URL}/api/card
X-Metabase-Session: {SESSION_TOKEN}

{
  "name": "Request Rate (per minute)",
  "display": "line",
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT timestamp_bucket('1 minute', timestamp) AS minute, COUNT(*) AS requests FROM cloud_run_requests WHERE service_name = '{{service_name}}' AND timestamp >= NOW() - INTERVAL '1 hour' GROUP BY minute ORDER BY minute",
      "template-tags": {
        "service_name": {
          "name": "service_name",
          "display-name": "Service Name",
          "type": "text",
          "default": "{SERVICE_NAME}"
        }
      }
    },
    "database": {DATABASE_ID}
  },
  "visualization_settings": {
    "graph.x_axis.title_text": "Time",
    "graph.y_axis.title_text": "Requests/min"
  },
  "collection_id": {COLLECTION_ID}
}
```

### Error Rate Card

```
POST {METABASE_URL}/api/card
X-Metabase-Session: {SESSION_TOKEN}

{
  "name": "Error Rate (5xx %)",
  "display": "line",
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT timestamp_bucket('5 minutes', timestamp) AS period, (SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END)::FLOAT / COUNT(*)) * 100 AS error_pct FROM cloud_run_requests WHERE service_name = '{{service_name}}' AND timestamp >= NOW() - INTERVAL '6 hours' GROUP BY period ORDER BY period"
    },
    "database": {DATABASE_ID}
  },
  "visualization_settings": {
    "graph.y_axis.title_text": "Error %",
    "graph.colors": ["#EF8C8C"]
  },
  "collection_id": {COLLECTION_ID}
}
```

### Latency Percentiles Card

```
POST {METABASE_URL}/api/card
X-Metabase-Session: {SESSION_TOKEN}

{
  "name": "Latency Percentiles (p50/p95/p99)",
  "display": "line",
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT timestamp_bucket('5 minutes', timestamp) AS period, PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY latency_ms) AS p50, PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95, PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) AS p99 FROM cloud_run_requests WHERE service_name = '{{service_name}}' AND timestamp >= NOW() - INTERVAL '6 hours' GROUP BY period ORDER BY period"
    },
    "database": {DATABASE_ID}
  },
  "collection_id": {COLLECTION_ID}
}
```

### Instance Count Card

```
POST {METABASE_URL}/api/card
X-Metabase-Session: {SESSION_TOKEN}

{
  "name": "Active Instances",
  "display": "area",
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT timestamp_bucket('1 minute', timestamp) AS minute, MAX(instance_count) AS instances FROM cloud_run_scaling WHERE service_name = '{{service_name}}' AND timestamp >= NOW() - INTERVAL '1 hour' GROUP BY minute ORDER BY minute"
    },
    "database": {DATABASE_ID}
  },
  "collection_id": {COLLECTION_ID}
}
```

---

## Adding Cards to Dashboard

After creating cards, add them to the dashboard with layout positions:

```
PUT {METABASE_URL}/api/dashboard/{DASHBOARD_ID}
X-Metabase-Session: {SESSION_TOKEN}

{
  "dashcards": [
    {
      "id": -1,
      "card_id": {REQUEST_RATE_CARD_ID},
      "row": 0,
      "col": 0,
      "size_x": 9,
      "size_y": 6
    },
    {
      "id": -2,
      "card_id": {ERROR_RATE_CARD_ID},
      "row": 0,
      "col": 9,
      "size_x": 9,
      "size_y": 6
    },
    {
      "id": -3,
      "card_id": {LATENCY_CARD_ID},
      "row": 6,
      "col": 0,
      "size_x": 9,
      "size_y": 6
    },
    {
      "id": -4,
      "card_id": {INSTANCE_COUNT_CARD_ID},
      "row": 6,
      "col": 9,
      "size_x": 9,
      "size_y": 6
    }
  ]
}
```

---

## Dashboard Subscriptions (Email Alerts)

Set up periodic email reports from Metabase:

```
POST {METABASE_URL}/api/pulse
X-Metabase-Session: {SESSION_TOKEN}

{
  "name": "{SERVICE_NAME} Daily Health Report",
  "cards": [
    {"id": {REQUEST_RATE_CARD_ID}, "include_csv": false},
    {"id": {ERROR_RATE_CARD_ID}, "include_csv": false}
  ],
  "channels": [
    {
      "channel_type": "email",
      "schedule_type": "daily",
      "schedule_hour": 9,
      "recipients": [{"email": "{RECIPIENT_EMAIL}"}]
    }
  ],
  "dashboard_id": {DASHBOARD_ID}
}
```

---

## Adapting Queries to Your Data Source

The SQL examples above assume a specific schema. When setting up, analyze the actual data source schema and adapt:

- **BigQuery**: Use `TIMESTAMP_TRUNC()` instead of `timestamp_bucket()`, backtick table names
- **PostgreSQL**: Use `date_trunc()` function
- **If using Cloud Monitoring export**: Tables will be `cloud_run_revision` metrics with specific column names from the export configuration

Always verify the schema first:
```
GET {METABASE_URL}/api/database/{DATABASE_ID}/metadata
X-Metabase-Session: {SESSION_TOKEN}
```
