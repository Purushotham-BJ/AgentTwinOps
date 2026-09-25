# Containerization Guide

This project is fully containerized using Docker Compose.

## Prerequisites
- Docker Engine
- Docker Compose

## Architecture
- **PostgreSQL**: `postgres:14-alpine` exposed on port `5432`
- **Backend**: FastAPI backend serving on port `8000`
- **Frontend**: Vite dev server mapped to port `5173`
- **AI Service**: FastAPI ML server mapped to port `8001`

The Compose configuration is the development/runtime verification profile. For production-like Kubernetes
deployment, use the manifests in `../k8s/`, build `frontend/Dockerfile.prod`, replace the example Secret,
and publish the backend, AI-service, and frontend images to a registry accessible by the cluster.

## Usage

### Start
To build and start the entire stack in the background:
```bash
docker compose up -d --build
```

### Stop
To stop the stack without losing database data:
```bash
docker compose down
```

### Database Data Reset (Wipe)
To completely reset the stack and wipe the persistent database volume:
```bash
docker compose down -v
```

### Logs
View logs for all services:
```bash
docker compose logs -f
```
Or for a specific service:
```bash
docker compose logs -f backend
docker compose logs -f ai-service
```

### Database Configuration
- The backend connects to the database via the internal compose DNS: `postgres:5432`
- Credentials are provided via environment variables in `docker-compose.yml`.

### Migrations
To run database migrations after starting the stack:
```bash
docker compose exec backend alembic upgrade head
```

The Kubernetes backend deployment runs `alembic upgrade head` in an init container before starting application
replicas. PostgreSQL data is stored in the `postgres-data` PVC.

### Kubernetes validation

Render the deployment without applying it:

```bash
kubectl kustomize k8s
```

Applying the manifests requires a configured cluster, registry image names, ingress controller, domain, and
values copied from `k8s/secret.example.yaml` into a real Secret. No production credentials belong in Git.

### Testing
To run backend tests inside the container (against the docker database):
```bash
docker compose exec backend pytest
```

### Troubleshooting
- **AI Service `401 Unauthorized`**: If the AI service cannot reach the backend with authorization, ensure `BACKEND_SERVICE_EMAIL` and `BACKEND_SERVICE_PASSWORD` in `docker-compose.yml` match a registered backend user.
- **Backend Test Imports**: If running pytest natively, ensure `PYTHONPATH` does not conflict with the project root.
