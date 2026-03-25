---
name: agentic-search-engine
description: AI Agent Search Engine skills. Use when you need to index your own platform or find wallets and other skills for AI agents.
---

# Agentic Search Engine

Official skill file for interacting with the AI Agent Search Engine.
This service indexes AI agent platforms and supports semantic retrieval over their capabilities.

## Sync Rule

Keep this file in sync with live API contracts.
Whenever request payloads, query params, or response fields change for agent-facing routes, update this file in the same change.

## Base URL

By default, the application runs locally at `http://localhost:8000`.
All API routes are prefixed with `/api`.

## Agent Flow

1. Register a platform with metadata and optional `skills_url`.
2. Add capabilities directly via `/api/skills/` or queue ingestion via `/api/platforms/{platform_id}/ingest`.
3. Search with `/api/search/` and use returned `platform_id` and `skill_md_url`.
4. Call `/api/skills/{platform_id}` to fetch full capability text for a chosen result.

## Endpoints

### 1. Register a New Platform

Use this endpoint to register a new platform or agent application into the index.

**Endpoint**: `POST /api/platforms/`
**Payload**:

```json
{
  "name": "My Agent App",
  "url": "https://my-agent.example.com",
  "homepage_uri": "https://my-agent.example.com/home",
  "description": "Optional description of what this platform does.",
  "skills_url": "https://my-agent.example.com/.agents/skills/agentic-search-engine/SKILL.md"
}
```

`skills_url` is optional, but recommended. If provided, search results return this exact value in `skill_md_url`.

**Success Response (200)**:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "My Agent App",
  "skills_url": "https://my-agent.example.com/.agents/skills/agentic-search-engine/SKILL.md",
  "message": "Platform created successfully. Crawler dispatched to discover skills and analyze the webpage."
}
```

### 2. Queue Skill Ingestion

Use this endpoint to trigger crawling/ingestion for a registered platform.

**Endpoint**: `POST /api/platforms/{platform_id}/ingest`

**Query Params**:

- `skills_url` (optional string): Temporary override for this ingest run. If omitted, the service uses the platform's stored `skills_url`.

**Success Response (200)**:

```json
{
  "message": "Ingestion task queued.",
  "platform_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Responses**:

- `400` invalid `platform_id` format
- `404` platform not found

### 3. Register a Skill

Use this endpoint to add capability text directly to a registered platform. Embeddings are generated automatically.

**Endpoint**: `POST /api/skills/`
**Payload**:

```json
{
  "platform_id": "<UUID of the registered platform>",
  "capabilities": "Supports managing wallets for AI agents, processing transactions, and handling crypto."
}
```

**Success Response (200)**:

```json
{
  "id": "5f3cc2f2-2d2c-4f0d-a0d7-3f3f5f888111",
  "platform_id": "123e4567-e89b-12d3-a456-426614174000",
  "capabilities": "Supports managing wallets for AI agents, processing transactions, and handling crypto.",
  "message": "Skill ingested successfully"
}
```

### 4. Search for Skills

Use this endpoint to semantically search for platforms matching the capability you need.

**Endpoint**: `GET /api/search/`
**Query Parameters**:

- `query` (string): The description of the skill you are looking for.
- `top_k` (integer, optional): Number of results to return. Range `1..50`, default `5`.

**Example Request**:
`GET /api/search/?query=wallets%20for%20ai%20agents&top_k=3`

**Example Response**:

```json
[
  {
    "platform_name": "My Agent App",
    "platform_description": "Optional description of what this platform does.",
    "platform_id": "123e4567-e89b-12d3-a456-426614174000",
    "skill": "Supports managing wallets for AI agents...",
    "similarity": 0.85,
    "skill_md_url": "https://my-agent.example.com/.agents/skills/agentic-search-engine/SKILL.md"
  }
]
```

`skill_md_url` comes from the platform's registered `skills_url` and may be `null` if it was not provided.

### 5. Get Full Skill Details for a Platform

Use this endpoint after search to retrieve full capabilities text for a selected platform.

**Endpoint**: `GET /api/skills/{platform_id}`

**Success Response (200, found)**:

```json
{
  "platform_id": "123e4567-e89b-12d3-a456-426614174000",
  "capabilities": "Supports managing wallets for AI agents, processing transactions, and handling crypto.",
  "created_at": "2026-03-25T11:10:00.000000"
}
```

**Success Response (200, not found in index yet)**:

```json
{
  "status": "not_found",
  "message": "We do not have a skill file for this platform yet. You can request it to be indexed via the /platforms endpoint."
}
```
