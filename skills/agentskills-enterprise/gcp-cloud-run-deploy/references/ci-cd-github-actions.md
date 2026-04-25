# CI/CD Reference: GitHub Actions + Cloud Build

## GitHub Actions Workflow Template

This template uses **direct API calls** — no `gcloud` CLI. Authentication uses Workload Identity Federation (preferred) or service account key.

### Workload Identity Federation (Recommended)

More secure than key files — no long-lived credentials to manage or rotate.

#### Prerequisites (set up once via API)
1. Create a Workload Identity Pool
2. Create a Workload Identity Provider for GitHub
3. Grant the pool's principal `roles/iam.workloadIdentityUser` on the service account

```yaml
# .github/workflows/deploy-cloud-run.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  id-token: write  # Required for Workload Identity Federation

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  REGION: ${{ secrets.GCP_REGION }}
  SERVICE_NAME: ${{ secrets.CLOUD_RUN_SERVICE }}
  REPOSITORY: ${{ secrets.ARTIFACT_REPO }}
  IMAGE_NAME: ${{ secrets.IMAGE_NAME }}

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.SA_EMAIL }}

      - name: Get access token (via OAuth2 API, not gcloud)
        id: token
        run: |
          pip install PyJWT cryptography requests -q
          TOKEN=$(python3 -c "
          import json, time, jwt, requests
          creds = json.load(open('${{ steps.auth.outputs.credentials_file_path }}'))
          now = int(time.time())
          payload = {'iss': creds['client_email'], 'scope': 'https://www.googleapis.com/auth/cloud-platform', 'aud': 'https://oauth2.googleapis.com/token', 'iat': now, 'exp': now + 3600}
          signed = jwt.encode(payload, creds['private_key'], algorithm='RS256')
          resp = requests.post('https://oauth2.googleapis.com/token', data={'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion': signed})
          print(resp.json()['access_token'])
          ")
          echo "::add-mask::$TOKEN"
          echo "token=$TOKEN" >> $GITHUB_OUTPUT

      - name: Trigger Cloud Build (via API)
        id: build
        run: |
          RESPONSE=$(curl -s -X POST \
            "https://cloudbuild.googleapis.com/v1/projects/$PROJECT_ID/builds" \
            -H "Authorization: Bearer ${{ steps.token.outputs.token }}" \
            -H "Content-Type: application/json" \
            -d '{
              "steps": [
                {
                  "name": "gcr.io/cloud-builders/docker",
                  "args": [
                    "build", "-t",
                    "'"$REGION"'-docker.pkg.dev/'"$PROJECT_ID"'/'"$REPOSITORY"'/'"$IMAGE_NAME"':'"$GITHUB_SHA"'",
                    "."
                  ]
                }
              ],
              "images": [
                "'"$REGION"'-docker.pkg.dev/'"$PROJECT_ID"'/'"$REPOSITORY"'/'"$IMAGE_NAME"':'"$GITHUB_SHA"'"
              ]
            }')
          
          BUILD_ID=$(echo $RESPONSE | jq -r '.metadata.build.id')
          echo "build_id=$BUILD_ID" >> $GITHUB_OUTPUT

      - name: Wait for Cloud Build completion
        run: |
          while true; do
            STATUS=$(curl -s \
              "https://cloudbuild.googleapis.com/v1/projects/$PROJECT_ID/builds/${{ steps.build.outputs.build_id }}" \
              -H "Authorization: Bearer ${{ steps.token.outputs.token }}" \
              | jq -r '.status')
            
            echo "Build status: $STATUS"
            
            if [ "$STATUS" = "SUCCESS" ]; then
              echo "Build completed successfully"
              break
            elif [ "$STATUS" = "FAILURE" ] || [ "$STATUS" = "CANCELLED" ] || [ "$STATUS" = "TIMEOUT" ]; then
              echo "Build failed with status: $STATUS"
              exit 1
            fi
            
            sleep 10
          done

      - name: Deploy to Cloud Run (via Admin API v2)
        run: |
          IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${GITHUB_SHA}"
          
          # Check if service exists
          HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            "https://run.googleapis.com/v2/projects/$PROJECT_ID/locations/$REGION/services/$SERVICE_NAME" \
            -H "Authorization: Bearer ${{ steps.token.outputs.token }}")
          
          if [ "$HTTP_CODE" = "404" ]; then
            # Create new service
            curl -s -X POST \
              "https://run.googleapis.com/v2/projects/$PROJECT_ID/locations/$REGION/services?serviceId=$SERVICE_NAME" \
              -H "Authorization: Bearer ${{ steps.token.outputs.token }}" \
              -H "Content-Type: application/json" \
              -d '{
                "template": {
                  "containers": [{"image": "'"$IMAGE_URI"'"}],
                  "scaling": {"minInstanceCount": 0, "maxInstanceCount": 10}
                },
                "ingress": "INGRESS_TRAFFIC_ALL"
              }'
          else
            # Update existing service
            curl -s -X PATCH \
              "https://run.googleapis.com/v2/projects/$PROJECT_ID/locations/$REGION/services/$SERVICE_NAME" \
              -H "Authorization: Bearer ${{ steps.token.outputs.token }}" \
              -H "Content-Type: application/json" \
              -d '{
                "template": {
                  "containers": [{"image": "'"$IMAGE_URI"'"}]
                }
              }'
          fi

      - name: Verify deployment
        run: |
          sleep 10
          SERVICE_URL=$(curl -s \
            "https://run.googleapis.com/v2/projects/$PROJECT_ID/locations/$REGION/services/$SERVICE_NAME" \
            -H "Authorization: Bearer ${{ steps.token.outputs.token }}" \
            | jq -r '.uri')
          
          echo "Service deployed at: $SERVICE_URL"
          
          HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL")
          if [ "$HTTP_STATUS" -ge 200 ] && [ "$HTTP_STATUS" -lt 400 ]; then
            echo "Health check passed (HTTP $HTTP_STATUS)"
          else
            echo "Warning: Health check returned HTTP $HTTP_STATUS"
          fi
```

### Service Account Key (Alternative)

Less secure — use only when Workload Identity Federation isn't feasible.

```yaml
      - name: Authenticate with Service Account Key
        id: auth
        run: |
          echo '${{ secrets.GCP_SA_KEY }}' > /tmp/sa-key.json
          
          # Exchange key for access token via OAuth2 API
          TOKEN=$(python3 -c "
          import json, time, jwt, requests
          
          with open('/tmp/sa-key.json') as f:
              key = json.load(f)
          
          now = int(time.time())
          payload = {
              'iss': key['client_email'],
              'scope': 'https://www.googleapis.com/auth/cloud-platform',
              'aud': 'https://oauth2.googleapis.com/token',
              'iat': now,
              'exp': now + 3600
          }
          
          signed = jwt.encode(payload, key['private_key'], algorithm='RS256')
          resp = requests.post('https://oauth2.googleapis.com/token', data={
              'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
              'assertion': signed
          })
          print(resp.json()['access_token'])
          ")
          
          echo "::add-mask::$TOKEN"
          echo "token=$TOKEN" >> $GITHUB_OUTPUT
          rm /tmp/sa-key.json
```

---

## Cloud Build Trigger (via API)

Create a trigger that auto-builds on push to main:

```
POST https://cloudbuild.googleapis.com/v1/projects/{PROJECT_ID}/triggers
Authorization: Bearer {TOKEN}

{
  "name": "{SERVICE_NAME}-deploy",
  "description": "Auto-deploy {SERVICE_NAME} on push to main",
  "github": {
    "owner": "{GITHUB_OWNER}",
    "name": "{GITHUB_REPO}",
    "push": {
      "branch": "^main$"
    }
  },
  "build": {
    "steps": [
      {
        "name": "gcr.io/cloud-builders/docker",
        "args": [
          "build", "-t",
          "{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO}/{IMAGE}:$COMMIT_SHA",
          "."
        ]
      },
      {
        "name": "gcr.io/cloud-builders/curl",
        "entrypoint": "bash",
        "args": [
          "-c",
          "curl -X PATCH 'https://run.googleapis.com/v2/projects/{PROJECT_ID}/locations/{REGION}/services/{SERVICE_NAME}' -H 'Authorization: Bearer $(gcloud auth print-access-token)' -H 'Content-Type: application/json' -d '{\"template\":{\"containers\":[{\"image\":\"{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO}/{IMAGE}:'$COMMIT_SHA'\"}]}}'"
        ]
      }
    ],
    "images": [
      "{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO}/{IMAGE}:$COMMIT_SHA"
    ]
  }
}
```

### Staging → Production Promotion

For production safety, set up a two-stage pipeline:

1. **Push to `main`** → deploys to staging Cloud Run service
2. **Manual approval** (via GitHub environment protection rules) → deploys to production

The GitHub Actions workflow handles this with two jobs:
- `deploy-staging` runs on every push to main
- `deploy-production` requires manual approval and runs after staging succeeds
