#!/usr/bin/env python3
"""
Deploy a container image to Cloud Run via the Admin API v2.

Handles both creating new services and updating existing ones.
Builds the image via Cloud Build API if --build is specified.

Usage:
    # Deploy existing image
    python deploy.py --key-file sa-key.json --project my-project --region us-central1 \
        --service my-service --image us-central1-docker.pkg.dev/my-project/repo/app:latest

    # Build and deploy from source
    python deploy.py --key-file sa-key.json --project my-project --region us-central1 \
        --service my-service --build --repo my-repo --branch main

    # Full options
    python deploy.py --key-file sa-key.json --project my-project --region us-central1 \
        --service my-service --image IMAGE_URI --port 8080 --memory 512Mi --cpu 1 \
        --min-instances 0 --max-instances 10 --env KEY=value --env SECRET=sm:my-secret
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error

# Import auth from same directory
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_access_token


def api_call(method, url, token, body=None):
    """Make an authenticated API call. Returns (status_code, response_dict)."""
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = json.loads(e.read().decode()) if e.read else {}
        return e.code, error_body


def ensure_artifact_registry(token, project, region, repo_name):
    """Create Artifact Registry Docker repo if it doesn't exist."""
    url = f"https://artifactregistry.googleapis.com/v1/projects/{project}/locations/{region}/repositories/{repo_name}"
    status, _ = api_call("GET", url, token)

    if status == 404:
        print(f"Creating Artifact Registry repository: {repo_name}")
        create_url = f"https://artifactregistry.googleapis.com/v1/projects/{project}/locations/{region}/repositories?repositoryId={repo_name}"
        status, resp = api_call("POST", create_url, token, {
            "format": "DOCKER",
            "description": f"Docker images for {repo_name}"
        })
        if status not in (200, 201):
            print(f"Failed to create Artifact Registry: {json.dumps(resp, indent=2)}", file=sys.stderr)
            sys.exit(1)
        print(f"Artifact Registry repository created: {repo_name}")
    elif status == 200:
        print(f"Artifact Registry repository exists: {repo_name}")
    else:
        print(f"Error checking Artifact Registry: {status}", file=sys.stderr)
        sys.exit(1)


def build_image(token, project, region, repo_name, image_name, tag, github_repo, branch):
    """Build a Docker image using Cloud Build API."""
    image_uri = f"{region}-docker.pkg.dev/{project}/{repo_name}/{image_name}:{tag}"

    print(f"Triggering Cloud Build for: {image_uri}")

    build_config = {
        "source": {
            "repoSource": {
                "projectId": project,
                "repoName": github_repo,
                "branchName": branch
            }
        },
        "steps": [
            {
                "name": "gcr.io/cloud-builders/docker",
                "args": ["build", "-t", image_uri, "."]
            }
        ],
        "images": [image_uri]
    }

    url = f"https://cloudbuild.googleapis.com/v1/projects/{project}/builds"
    status, resp = api_call("POST", url, token, build_config)

    if status not in (200, 201):
        print(f"Failed to trigger build: {json.dumps(resp, indent=2)}", file=sys.stderr)
        sys.exit(1)

    build_id = resp.get("metadata", {}).get("build", {}).get("id")
    print(f"Build started: {build_id}")

    # Poll for completion
    build_url = f"https://cloudbuild.googleapis.com/v1/projects/{project}/builds/{build_id}"
    while True:
        time.sleep(10)
        status, resp = api_call("GET", build_url, token)
        build_status = resp.get("status", "UNKNOWN")
        print(f"  Build status: {build_status}")

        if build_status == "SUCCESS":
            print(f"Build completed: {image_uri}")
            return image_uri
        elif build_status in ("FAILURE", "CANCELLED", "TIMEOUT", "INTERNAL_ERROR"):
            print(f"Build failed: {build_status}", file=sys.stderr)
            if "statusDetail" in resp:
                print(f"  Detail: {resp['statusDetail']}", file=sys.stderr)
            sys.exit(1)


def parse_env_vars(env_list, project):
    """Parse environment variables. Format: KEY=value or KEY=sm:secret-name for Secret Manager."""
    env_vars = []
    for item in (env_list or []):
        key, _, value = item.partition("=")
        if value.startswith("sm:"):
            secret_name = value[3:]
            env_vars.append({
                "name": key,
                "valueSource": {
                    "secretKeyRef": {
                        "secret": f"projects/{project}/secrets/{secret_name}",
                        "version": "latest"
                    }
                }
            })
        else:
            env_vars.append({"name": key, "value": value})
    return env_vars


def deploy_service(token, project, region, service_name, image_uri, port, memory, cpu,
                   min_instances, max_instances, env_vars):
    """Create or update a Cloud Run service."""
    base_url = f"https://run.googleapis.com/v2/projects/{project}/locations/{region}/services"

    container = {
        "image": image_uri,
        "ports": [{"containerPort": port}],
        "resources": {
            "limits": {"cpu": str(cpu), "memory": memory}
        }
    }
    if env_vars:
        container["env"] = env_vars

    service_config = {
        "template": {
            "containers": [container],
            "scaling": {
                "minInstanceCount": min_instances,
                "maxInstanceCount": max_instances
            }
        },
        "ingress": "INGRESS_TRAFFIC_ALL"
    }

    # Check if service exists
    check_url = f"{base_url}/{service_name}"
    status, _ = api_call("GET", check_url, token)

    if status == 404:
        print(f"Creating new Cloud Run service: {service_name}")
        url = f"{base_url}?serviceId={service_name}"
        status, resp = api_call("POST", url, token, service_config)
    else:
        print(f"Updating existing Cloud Run service: {service_name}")
        status, resp = api_call("PATCH", check_url, token, service_config)

    if status not in (200, 201):
        print(f"Deployment failed: {json.dumps(resp, indent=2)}", file=sys.stderr)
        sys.exit(1)

    # Wait for service to become ready
    print("Waiting for service to become ready...")
    for _ in range(30):
        time.sleep(5)
        status, resp = api_call("GET", check_url, token)
        conditions = resp.get("conditions", [])
        ready = any(c.get("type") == "Ready" and c.get("state") == "CONDITION_SUCCEEDED"
                     for c in conditions)
        if ready:
            service_url = resp.get("uri", "unknown")
            print(f"\nService deployed successfully!")
            print(f"  URL: {service_url}")
            print(f"  Image: {image_uri}")
            print(f"  Region: {region}")
            return resp

    print("Warning: Service did not become ready within timeout", file=sys.stderr)
    return resp


def main():
    parser = argparse.ArgumentParser(description="Deploy to Cloud Run via Admin API v2")
    parser.add_argument("--key-file", required=True, help="Service account JSON key file")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--region", required=True, help="Cloud Run region")
    parser.add_argument("--service", required=True, help="Cloud Run service name")

    # Image source
    parser.add_argument("--image", help="Container image URI (if pre-built)")
    parser.add_argument("--build", action="store_true", help="Build image via Cloud Build first")
    parser.add_argument("--repo", help="GitHub repo name (for --build)")
    parser.add_argument("--branch", default="main", help="Branch to build from (default: main)")
    parser.add_argument("--tag", default=None, help="Image tag (default: timestamp)")
    parser.add_argument("--image-name", default=None, help="Image name in Artifact Registry")
    parser.add_argument("--ar-repo", default=None, help="Artifact Registry repo name")

    # Service config
    parser.add_argument("--port", type=int, default=8080, help="Container port (default: 8080)")
    parser.add_argument("--memory", default="512Mi", help="Memory limit (default: 512Mi)")
    parser.add_argument("--cpu", default="1", help="CPU limit (default: 1)")
    parser.add_argument("--min-instances", type=int, default=0, help="Min instances (default: 0)")
    parser.add_argument("--max-instances", type=int, default=10, help="Max instances (default: 10)")
    parser.add_argument("--env", action="append", help="Env var: KEY=value or KEY=sm:secret-name")

    args = parser.parse_args()

    if not args.image and not args.build:
        print("Error: provide either --image or --build", file=sys.stderr)
        sys.exit(1)

    # Authenticate
    token_data = get_access_token(args.key_file)
    token = token_data["access_token"]
    print(f"Authenticated as: {token_data['service_account']}")

    # Build if needed
    image_uri = args.image
    if args.build:
        if not args.repo:
            print("Error: --repo required when using --build", file=sys.stderr)
            sys.exit(1)
        ar_repo = args.ar_repo or args.service
        image_name = args.image_name or args.service
        tag = args.tag or str(int(time.time()))

        ensure_artifact_registry(token, args.project, args.region, ar_repo)
        image_uri = build_image(token, args.project, args.region, ar_repo, image_name, tag,
                                args.repo, args.branch)

    # Parse env vars
    env_vars = parse_env_vars(args.env, args.project)

    # Deploy
    deploy_service(token, args.project, args.region, args.service, image_uri,
                   args.port, args.memory, args.cpu, args.min_instances, args.max_instances, env_vars)


if __name__ == "__main__":
    main()
