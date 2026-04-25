#!/usr/bin/env python3
"""
Set up Metabase dashboards for Cloud Run service monitoring.

Usage:
    # Connect to Metabase and create a monitoring dashboard
    python monitoring.py --metabase-url https://metabase.example.com \
        --email admin@example.com --password secret \
        --service my-service --database-id 1

    # List existing dashboards
    python monitoring.py --metabase-url https://metabase.example.com \
        --email admin@example.com --password secret \
        list
"""

import argparse
import json
import sys
import urllib.request
import urllib.error


def metabase_call(method, url, body=None, session_token=None):
    """Make a Metabase API call."""
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if session_token:
        req.add_header("X-Metabase-Session", session_token)

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read().decode())
        except Exception:
            error_body = {"error": str(e)}
        return e.code, error_body


def authenticate(metabase_url, email, password):
    """Get Metabase session token."""
    status, resp = metabase_call("POST", f"{metabase_url}/api/session",
                                  {"username": email, "password": password})
    if status == 200:
        return resp.get("id")
    else:
        print(f"Metabase authentication failed: {json.dumps(resp, indent=2)}", file=sys.stderr)
        sys.exit(1)


def create_collection(metabase_url, token, service_name):
    """Create a collection for the service dashboards."""
    status, resp = metabase_call("POST", f"{metabase_url}/api/collection", {
        "name": f"Cloud Run - {service_name}",
        "description": f"Monitoring dashboards for {service_name}",
        "color": "#509EE3"
    }, token)

    if status in (200, 201):
        print(f"Collection created: {resp.get('id')}")
        return resp.get("id")
    else:
        print(f"Failed to create collection: {json.dumps(resp, indent=2)}", file=sys.stderr)
        sys.exit(1)


def create_card(metabase_url, token, name, display, query, database_id, collection_id,
                viz_settings=None):
    """Create a Metabase question (card)."""
    card = {
        "name": name,
        "display": display,
        "dataset_query": {
            "type": "native",
            "native": {"query": query},
            "database": database_id
        },
        "visualization_settings": viz_settings or {},
        "collection_id": collection_id
    }

    status, resp = metabase_call("POST", f"{metabase_url}/api/card", card, token)
    if status in (200, 201):
        print(f"  Card created: {name} (ID: {resp.get('id')})")
        return resp.get("id")
    else:
        print(f"  Failed to create card '{name}': {json.dumps(resp, indent=2)}", file=sys.stderr)
        return None


def create_dashboard_with_cards(metabase_url, token, service_name, database_id, collection_id):
    """Create a complete monitoring dashboard with cards."""

    # Create dashboard
    status, resp = metabase_call("POST", f"{metabase_url}/api/dashboard", {
        "name": f"{service_name} - Service Health",
        "description": f"Real-time health metrics for {service_name} on Cloud Run",
        "collection_id": collection_id
    }, token)

    if status not in (200, 201):
        print(f"Failed to create dashboard: {json.dumps(resp, indent=2)}", file=sys.stderr)
        sys.exit(1)

    dashboard_id = resp.get("id")
    print(f"Dashboard created: {dashboard_id}")

    # Define cards (adapt SQL to your actual schema)
    cards = [
        {
            "name": "Request Rate (per minute)",
            "display": "line",
            "query": f"""
                SELECT
                    date_trunc('minute', timestamp) AS minute,
                    COUNT(*) AS requests
                FROM cloud_run_requests
                WHERE service_name = '{service_name}'
                    AND timestamp >= NOW() - INTERVAL '1 hour'
                GROUP BY minute
                ORDER BY minute
            """,
            "viz": {"graph.x_axis.title_text": "Time", "graph.y_axis.title_text": "Requests/min"},
            "row": 0, "col": 0, "size_x": 9, "size_y": 6
        },
        {
            "name": "Error Rate (5xx %)",
            "display": "line",
            "query": f"""
                SELECT
                    date_trunc('5 minutes', timestamp) AS period,
                    (SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0)) * 100 AS error_pct
                FROM cloud_run_requests
                WHERE service_name = '{service_name}'
                    AND timestamp >= NOW() - INTERVAL '6 hours'
                GROUP BY period
                ORDER BY period
            """,
            "viz": {"graph.y_axis.title_text": "Error %", "graph.colors": ["#EF8C8C"]},
            "row": 0, "col": 9, "size_x": 9, "size_y": 6
        },
        {
            "name": "Latency Percentiles (ms)",
            "display": "line",
            "query": f"""
                SELECT
                    date_trunc('5 minutes', timestamp) AS period,
                    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY latency_ms) AS p50,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) AS p99
                FROM cloud_run_requests
                WHERE service_name = '{service_name}'
                    AND timestamp >= NOW() - INTERVAL '6 hours'
                GROUP BY period
                ORDER BY period
            """,
            "viz": {"graph.y_axis.title_text": "Latency (ms)"},
            "row": 6, "col": 0, "size_x": 9, "size_y": 6
        },
        {
            "name": "Active Instances",
            "display": "area",
            "query": f"""
                SELECT
                    date_trunc('minute', timestamp) AS minute,
                    MAX(instance_count) AS instances
                FROM cloud_run_scaling
                WHERE service_name = '{service_name}'
                    AND timestamp >= NOW() - INTERVAL '1 hour'
                GROUP BY minute
                ORDER BY minute
            """,
            "viz": {"graph.y_axis.title_text": "Instances", "graph.colors": ["#88BF4D"]},
            "row": 6, "col": 9, "size_x": 9, "size_y": 6
        }
    ]

    # Create cards and collect for dashboard
    dashcards = []
    for i, card_def in enumerate(cards):
        card_id = create_card(
            metabase_url, token,
            card_def["name"], card_def["display"],
            card_def["query"], database_id, collection_id,
            card_def.get("viz")
        )
        if card_id:
            dashcards.append({
                "id": -(i + 1),
                "card_id": card_id,
                "row": card_def["row"],
                "col": card_def["col"],
                "size_x": card_def["size_x"],
                "size_y": card_def["size_y"]
            })

    # Add cards to dashboard
    if dashcards:
        status, resp = metabase_call("PUT", f"{metabase_url}/api/dashboard/{dashboard_id}",
                                      {"dashcards": dashcards}, token)
        if status == 200:
            print(f"\nDashboard ready: {metabase_url}/dashboard/{dashboard_id}")
        else:
            print(f"Failed to add cards to dashboard: {json.dumps(resp, indent=2)}", file=sys.stderr)

    return dashboard_id


def list_dashboards(metabase_url, token):
    """List existing dashboards."""
    status, resp = metabase_call("GET", f"{metabase_url}/api/dashboard", session_token=token)
    if status == 200:
        for d in resp:
            print(f"  [{d.get('id')}] {d.get('name')} - {d.get('description', 'No description')}")
    else:
        print(f"Failed to list dashboards: {json.dumps(resp, indent=2)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Metabase monitoring for Cloud Run")
    parser.add_argument("--metabase-url", required=True, help="Metabase instance URL")
    parser.add_argument("--email", required=True, help="Metabase admin email")
    parser.add_argument("--password", required=True, help="Metabase admin password")

    subparsers = parser.add_subparsers(dest="command")

    # Setup subcommand
    setup_parser = subparsers.add_parser("setup", help="Create monitoring dashboard")
    setup_parser.add_argument("--service", required=True, help="Cloud Run service name")
    setup_parser.add_argument("--database-id", type=int, required=True, help="Metabase database ID")

    # List subcommand
    subparsers.add_parser("list", help="List existing dashboards")

    args = parser.parse_args()

    # Authenticate
    token = authenticate(args.metabase_url, args.email, args.password)
    print(f"Authenticated to Metabase")

    if args.command == "list":
        list_dashboards(args.metabase_url, token)
    elif args.command == "setup":
        collection_id = create_collection(args.metabase_url, token, args.service)
        create_dashboard_with_cards(args.metabase_url, token, args.service,
                                     args.database_id, collection_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
