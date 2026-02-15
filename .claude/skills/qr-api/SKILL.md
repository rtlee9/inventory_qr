---
name: qr-api
description: Manage shortened URLs via the Dynamic QR API. Use when the user wants to create, update, delete, list, or track shortened URLs, or get QR codes.
argument-hint: [action] [args...]
allowed-tools: Bash
---

# Dynamic QR API Skill

Manage shortened URLs on the Dynamic QR app via its HTTP API.

## Connection

- **Base URL**: `https://qr.ryanlee.site/api`
- **Auth**: `X-API-Key` header, value from `API_KEY` env var
- Use `curl` for all requests

## Endpoints

### List recent URL actions
```bash
curl -s -H "X-API-Key: $API_KEY" https://qr.ryanlee.site/api/urls/ | python3 -m json.tool
```

### Create a shortened URL
```bash
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com", "key": "my-slug"}' \
  https://qr.ryanlee.site/api/urls/ | python3 -m json.tool
```

### Get detail/history for a key
```bash
curl -s -H "X-API-Key: $API_KEY" https://qr.ryanlee.site/api/urls/<key>/ | python3 -m json.tool
```

### Update a URL's target
```bash
curl -s -X PUT -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"long_url": "https://new-target.com"}' \
  https://qr.ryanlee.site/api/urls/<key>/ | python3 -m json.tool
```

### Delete a shortened URL
```bash
curl -s -X DELETE -H "X-API-Key: $API_KEY" \
  https://qr.ryanlee.site/api/urls/<key>/ | python3 -m json.tool
```

### Get tracking/hit data
```bash
curl -s -H "X-API-Key: $API_KEY" https://qr.ryanlee.site/api/urls/<key>/track/ | python3 -m json.tool
```

### Get QR code URL
```bash
curl -s -H "X-API-Key: $API_KEY" https://qr.ryanlee.site/api/urls/<key>/qr/ | python3 -m json.tool
```

## Interpreting arguments

Map the user's request to the right endpoint:

- "create <url> as <key>" → POST create
- "update <key> to <url>" → PUT update
- "delete <key>" → DELETE
- "list" / "show recent" → GET list
- "track <key>" / "hits for <key>" → GET track
- "qr <key>" / "qr code for <key>" → GET qr
- "info <key>" / "history <key>" → GET detail

## Key format

Keys must match `^[a-zA-Z0-9-]+$` (letters, numbers, hyphens only).

## Notes

- The `API_KEY` env var must be set before calling. If it's not set, ask the user to provide it.
- All responses are JSON. Show the user the relevant fields concisely.
- Short URLs resolve at `https://aws3.link/<key>`.
