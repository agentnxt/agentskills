# Coolify API v1 Reference

Base URL: `{COOLIFY_BASE_URL}/api/v1`

All requests require the header:
```
Authorization: Bearer {COOLIFY_API_KEY}
Content-Type: application/json
```

---

## Health Check

```
GET /healthcheck
```
Returns `{ "status": "ok" }` if Coolify is reachable and the API key is valid.
Always call this first to validate credentials.

---

## Servers

### List servers
```
GET /servers
```
Response: array of server objects
```json
[
  {
    "uuid": "abc123",
    "name": "My Server",
    "ip": "1.2.3.4",
    "status": "reachable"
  }
]
```

### Get server destinations
```
GET /servers/{server_uuid}/destinations
```
Response: array of destination objects
```json
[
  {
    "uuid": "dest456",
    "name": "default",
    "network": "coolify"
  }
]
```

---

## Projects

### List projects
```
GET /projects
```

### Create project
```
POST /projects
{
  "name": "my-project",
  "description": "optional"
}
```
Response: `{ "uuid": "proj789", ... }`

### Get project
```
GET /projects/{uuid}
```

---

## Services (Docker Compose)

### Create a Docker Compose service
```
POST /services
{
  "type": "docker-compose",
  "name": "my-service",
  "project_uuid": "proj789",
  "environment_name": "production",   // optional, default: "production"
  "server_uuid": "abc123",
  "destination_uuid": "dest456",
  "git_repository": "https://github.com/user/repo",
  "git_branch": "main",
  "git_commit_sha": "HEAD",           // optional
  "docker_compose_location": "/docker-compose.yml",
  "docker_compose_raw": null,         // alternative: pass raw compose YAML as string
  "instant_deploy": false             // set true to deploy immediately on creation
}
```
Response:
```json
{
  "uuid": "svc111",
  "url": "https://my-service.coolify.yourdomain.com",
  ...
}
```

### Get service
```
GET /services/{uuid}
```
Key fields in response:
- `status`: `running` | `stopped` | `restarting` | `exited`
- `url`: public URL
- `fqdn`: fully qualified domain name

### List services in a project
```
GET /projects/{project_uuid}/{environment_name}/services
```

### Delete service
```
DELETE /services/{uuid}
```

---

## Environment Variables

### List env vars for a service
```
GET /services/{service_uuid}/envs
```

### Create / upsert a single env var
```
POST /services/{service_uuid}/envs
{
  "key": "MY_VAR",
  "value": "my_value",
  "is_secret": false,      // true hides value in UI
  "is_required": false     // marks var as required in Coolify UI
}
```

### Bulk upsert env vars
```
POST /services/{service_uuid}/envs/bulk
{
  "data": [
    { "key": "VAR1", "value": "val1", "is_secret": false },
    { "key": "SECRET1", "value": "s3cr3t", "is_secret": true }
  ]
}
```
⚡ Prefer bulk upsert over individual calls when wiring many vars.

### Update an env var
```
PATCH /services/{service_uuid}/envs
{
  "key": "MY_VAR",
  "value": "new_value",
  "is_secret": false
}
```

### Delete an env var
```
DELETE /services/{service_uuid}/envs
{ "key": "MY_VAR" }
```

---

## Deployments

### Trigger a deployment
```
POST /deploy?uuid={service_uuid}&force=false
```
- `force=true` rebuilds from scratch (no cache)

Response:
```json
{
  "message": "Deployment queued.",
  "deployment_uuid": "dep222"
}
```

### Get deployment status
```
GET /deployments/{deployment_uuid}
```
Key fields:
- `status`: `queued` | `in_progress` | `finished` | `failed` | `cancelled`
- `logs`: array of log lines

### List deployments for a service
```
GET /services/{service_uuid}/deployments
```

---

## Applications (alternative to Services for single-container)

> Use **Services** for Docker Compose. Use **Applications** only for single
> Dockerfile or Nixpacks-based deployments.

### Create application
```
POST /applications
{
  "type": "private-github-app" | "public",
  "name": "my-app",
  "project_uuid": "proj789",
  "server_uuid": "abc123",
  "destination_uuid": "dest456",
  "git_repository": "https://github.com/user/repo",
  "git_branch": "main",
  "build_pack": "dockerfile" | "nixpacks" | "static"
}
```

---

## Common Error Codes

| Code | Meaning | Fix |
|---|---|---|
| 401 | Invalid API key | Check `COOLIFY_API_KEY` |
| 403 | Forbidden | Key lacks permission for this resource |
| 404 | Resource not found | Check UUID is correct |
| 409 | Conflict (already exists) | Use existing resource or delete first |
| 422 | Validation error | Check request body — response includes field errors |
| 500 | Coolify internal error | Check Coolify server logs |

---

## Notes

- Coolify API is versioned at `/api/v1` — always use this prefix.
- UUIDs are used throughout — never use names as identifiers in API calls.
- The `environment_name` in Coolify projects defaults to `"production"` if not specified.
- After wiring env vars, always trigger a new deployment for changes to take effect.
- Coolify auto-generates a public URL (FQDN) for services — retrieve it from the
  `GET /services/{uuid}` response after deployment.
