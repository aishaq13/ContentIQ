# ContentIQ

ContentIQ is a functional distributed metadata management project designed to simulate Azure-style cloud metadata services.

## What is included

- **Scalable Metadata APIs** built with FastAPI.
- **Distributed messaging** with Kafka (plus local fallback queue for development).
- **Blob-style persistence** abstraction for metadata records.
- **Azure Functions worker sample** for propagation workflows.
- **Containerized runtime** with Docker and Docker Compose.
- **Kubernetes manifests** suitable as a baseline for AKS-style deployment.
- **Load test script** to validate throughput and project request/day capacity.

## Architecture

```text
Client -> FastAPI Metadata API -> Blob Storage + Kafka Topic -> Propagation Worker
```

### Services

1. **API service (`app/main.py`)**
   - Handles CRUD-like metadata operations.
   - Emits metadata update events to Kafka.
2. **Event bus (`app/services/event_bus.py`)**
   - Produces and consumes metadata events.
   - Falls back to in-process queue when Kafka is unavailable.
3. **Storage (`app/services/blob_storage.py`)**
   - Stores metadata as JSON blobs (filesystem-backed for local/dev).
4. **Azure Function sample (`azure_functions/metadata_propagator/function_app.py`)**
   - Consumes event stream and simulates low-latency propagation.

## Quickstart

### 1) Local API run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

API docs: <http://localhost:8000/docs>

### 2) Docker Compose (API + Kafka)

```bash
docker compose up --build
```

### 3) Kubernetes (AKS-ready baseline)

```bash
kubectl apply -f kubernetes/kafka.yaml
kubectl apply -f kubernetes/contentiq-deployment.yaml
```

## API examples

### Create/update metadata

```bash
curl -X POST http://localhost:8000/api/v1/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "key": "asset-1001",
    "value": {"owner": "media-team", "ttl": 3600},
    "tags": ["video", "prod"]
  }'
```

### Get metadata

```bash
curl http://localhost:8000/api/v1/metadata/asset-1001
```

## Performance workflow

Run synthetic load:

```bash
python scripts/load_test.py --base-url http://localhost:8000 --total-requests 100000 --concurrency 400
```

Use resulting **requests/sec** to project daily capacity:

```text
projected_requests_day = requests_per_second * 86,400
```

You can use this harness to validate goals such as **1M+ metadata requests/day** and compare propagation latency across deployments.

## Tech Stack

- Python
- FastAPI
- Kafka
- Azure Functions (sample worker)
- Blob storage abstraction
- Docker
- Kubernetes

## Notes

- For local development without Kafka, ContentIQ automatically falls back to an in-memory event queue.
- For production deployments, replace filesystem-backed storage with managed Blob Storage and wire Kafka to a managed event platform.
