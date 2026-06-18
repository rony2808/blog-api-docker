# Blog API — Docker Stack

A REST API for a blog built with Docker Compose.

## Stack
- **nginx** — reverse proxy
- **Flask** — Python REST API
- **MySQL** — database
- **Redis** — cache

## Architecture
nginx (:80) → Flask (:5000) → MySQL (:3306)
                            → Redis (:6379)

## Features
- Multi-stage build (Flask image ~46MB)
- Redis cache with 60s expiration
- Cache invalidation on write
- Persistent MySQL volume
- Healthchecks on all services
- Environment variables via .env

## Usage
1. Clone the repo
2. cp .env.example .env and fill in the values
3. docker compose up -d

## API Routes
- GET  /              → API status
- GET  /articles      → list all articles (cached)
- GET  /articles/<id> → get one article (cached)
- POST /articles      → create an article

## Example
curl http://localhost/articles
curl -X POST http://localhost/articles \
  -H "Content-Type: application/json" \
  -d '{"title": "My article", "content": "Hello World"}'
