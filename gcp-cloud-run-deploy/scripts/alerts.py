#!/usr/bin/env python3
"""
Create GCP Cloud Monitoring alert policies and notification channels for Cloud Run services.

Usage:
    # Create email notification channel
    python alerts.py --key-file sa-key.json --project my-project \
        channel --type email --email alerts@example.com --name "Team Alerts"

    # Create webhook notification channel
    python alerts.py --key-file sa-key.json --project my-project \
        channel --type webhook --url https://hooks.slack.com/xxx --name "Slack Webhook"

    # Create default alert policies for a Cloud Run service
    python alerts.py --key-file sa-key.json --project my-project \
        alerts --service my-service --channel CHANNEL_ID

    # Create a custom alert
    python alerts.py --key-file sa-key.json --project my-project \
        custom --service my-service --channel CHANNEL_ID \
        --metric "run.googleapis.com/request_latencies" --threshold 2000 --display "High Latency"
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_access_token


def api_call(method, url, token, body=None):
    """Make an authenticated API call."""
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read().decode())
        except Exception:
            error_body = {"error": str(e)}
        return e.code, error_body


def create_notification_channel(token, project, channel_type, name, **kwargs):
    """Create a notification channel (email or webhook)."""
    url = f"https://monitoring.googleapis.com/v3/projects/{project}/notificationChannels"

    if channel_type == "email":
        channel = {
            "type": "email",
            "displayName": name,
            "labels": {"email_address": kwargs["email"]}
        }
    elif channel_type == "webhook":
        channel = {
            "type": "webhook_token_auth",
            "displayName": name,
            "labels": {"url": kwargs["url"]}
        }
    else:
        print(f"Unsupported channel type: {channel_type}", file=sys.stderr)
        sys.exit(1)

    status, resp = api_call("POST", url, token, channel)
    if status in (200, 201):
        channel_id = resp.get("name", "")
        print(f"Notification channel created: {channel_id}")
        print(f"  Type: {channel_type}")
        print(f"  Name: {name}")
        return channel_id
    else:
        print(f"Failed to create channel: {json.dumps(resp, indent=2)}", file=sys.stderr)
        sys.exit(1)


def create_alert_policy(token, project, display_name, service_name, metric_type,
                        comparison, threshold, duration, channel_ids, aggregation_aligner="ALIGN_RATE"):
    """Create a Cloud Monitoring alert policy."""
    url = f"https://monitoring.googleapis.com/v3/projects/{project}/alertPolicies"

    policy = {
        "displayName": display_name,
        "conditions": [
            {
                "displayName": display_name,
                "conditionThreshold": {
                    "filter": f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}" AND metric.type="{metric_type}"',
                    "comparison": comparison,
                    "thresholdValue": threshold,
                    "duration": duration,
                    "aggregations": [
                        {
                            "alignmentPeriod": "60s",
                            "perSeriesAligner": aggregation_aligner
                        }
                    ]
                }
            }
        ],
        "notificationChannels": channel_ids if isinstance(channel_ids, list) else [channel_ids],
        "combiner": "OR",
        "enabled": True
    }

    status, resp = api_call("POST", url, token, policy)
    if status in (200, 201):
        policy_name = resp.get("name", "")
        print(f"Alert policy created: {display_name}")
        print(f"  Policy ID: {policy_name}")
        return policy_name
    else:
        print(f"Failed to create alert: {json.dumps(resp, indent=2)}", file=sys.stderr)
        return None


def create_default_alerts(token, project, service_name, channel_ids):
    """Create a standard set of alert policies for a Cloud Run service."""
    defaults = [
        {
            "display_name": f"{service_name} - High Error Rate (5xx > 5%)",
            "metric_type": "run.googleapis.com/request_count",
            "comparison": "COMPARISON_GT",
            "threshold": 5,
            "duration": "300s",
            "aggregation_aligner": "ALIGN_RATE"
        },
        {
            "display_name": f"{service_name} - High Latency (p99 > 2s)",
            "metric_type": "run.googleapis.com/request_latencies",
            "comparison": "COMPARISON_GT",
            "threshold": 2000,
            "duration": "300s",
            "aggregation_aligner": "ALIGN_PERCENTILE_99"
        },
        {
            "display_name": f"{service_name} - Max Instances Sustained (>10min)",
            "metric_type": "run.googleapis.com/container/instance_count",
            "comparison": "COMPARISON_GT",
            "threshold": 9,  # Alert when at or near max
            "duration": "600s",
            "aggregation_aligner": "ALIGN_MAX"
        },
        {
            "display_name": f"{service_name} - High Cold Start Rate (>20%)",
            "metric_type": "run.googleapis.com/container/startup_latencies",
            "comparison": "COMPARISON_GT",
            "threshold": 20,
            "duration": "300s",
            "aggregation_aligner": "ALIGN_PERCENTILE_99"
        }
    ]

    print(f"\nCreating default alert policies for: {service_name}")
    print(f"Notification channel(s): {channel_ids}\n")

    created = []
    for alert_def in defaults:
        result = create_alert_policy(
            token, project,
            alert_def["display_name"],
            service_name,
            alert_def["metric_type"],
            alert_def["comparison"],
            alert_def["threshold"],
            alert_def["duration"],
            channel_ids,
            alert_def["aggregation_aligner"]
        )
        if result:
            created.append(result)

    print(f"\n{len(created)}/{len(defaults)} alert policies created successfully")
    return created


def main():
    parser = argparse.ArgumentParser(description="Cloud Monitoring alerts for Cloud Run")
    parser.add_argument("--key-file", required=True, help="Service account JSON key file")
    parser.add_argument("--project", required=True, help="GCP project ID")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Channel subcommand
    ch_parser = subparsers.add_parser("channel", help="Create notification channel")
    ch_parser.add_argument("--type", required=True, choices=["email", "webhook"])
    ch_parser.add_argument("--name", required=True, help="Channel display name")
    ch_parser.add_argument("--email", help="Email address (for email type)")
    ch_parser.add_argument("--url", help="Webhook URL (for webhook type)")

    # Default alerts subcommand
    al_parser = subparsers.add_parser("alerts", help="Create default alert policies")
    al_parser.add_argument("--service", required=True, help="Cloud Run service name")
    al_parser.add_argument("--channel", required=True, action="append", help="Notification channel ID")

    # Custom alert subcommand
    cu_parser = subparsers.add_parser("custom", help="Create custom alert policy")
    cu_parser.add_argument("--service", required=True, help="Cloud Run service name")
    cu_parser.add_argument("--channel", required=True, action="append", help="Notification channel ID")
    cu_parser.add_argument("--metric", required=True, help="Metric type")
    cu_parser.add_argument("--threshold", type=float, required=True, help="Threshold value")
    cu_parser.add_argument("--display", required=True, help="Alert display name")
    cu_parser.add_argument("--duration", default="300s", help="Duration (default: 300s)")
    cu_parser.add_argument("--comparison", default="COMPARISON_GT", help="Comparison type")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    token = get_access_token(args.key_file)["access_token"]

    if args.command == "channel":
        if args.type == "email" and not args.email:
            print("Error: --email required for email channel", file=sys.stderr)
            sys.exit(1)
        if args.type == "webhook" and not args.url:
            print("Error: --url required for webhook channel", file=sys.stderr)
            sys.exit(1)
        create_notification_channel(token, args.project, args.type, args.name,
                                     email=args.email, url=args.url)

    elif args.command == "alerts":
        create_default_alerts(token, args.project, args.service, args.channel)

    elif args.command == "custom":
        create_alert_policy(token, args.project, args.display, args.service,
                           args.metric, args.comparison, args.threshold,
                           args.duration, args.channel)


if __name__ == "__main__":
    main()
