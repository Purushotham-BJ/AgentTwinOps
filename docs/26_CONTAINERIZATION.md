# Containerization Guide

This project is fully containerized using Docker Compose.

## Prerequisites
- Docker Engine
- Docker Compose

## Architecture
- **Development profile**: PostgreSQL `5432`, backend `8000`, frontend Vite `5173`,
  and AI service `8001` are mapped for local verification.
- **AWS production profile**: only the Nginx frontend is published on port `80`;
  PostgreSQL, backend, and AI service remain private on the Compose network.

The Compose configuration is the development/runtime verification profile. For production-like Kubernetes
deployment, use the manifests in `../k8s/`, build `frontend/Dockerfile.prod`, replace the example Secret,
and publish the backend, AI-service, and frontend images to a registry accessible by the cluster.

For AWS EC2 deployment with Docker Compose, use `docker-compose.prod.yml` and a protected
`.env.aws` file copied from `../.env.aws.example`. The production profile keeps PostgreSQL,
the backend, and the AI service on the private Compose network. The Nginx frontend is the
only published application port and proxies `/api/` to the backend and `/ai/` to the AI service.

## Usage

### Start
To build and start the entire stack in the background:
```bash
docker compose up -d --build
```

### AWS EC2 production profile

On an Ubuntu EC2 host, install Docker Engine and the Compose plugin, clone the repository,
copy `.env.aws.example` to `.env.aws`, replace every placeholder, and restrict the file:

```bash
cp .env.aws.example .env.aws
chmod 600 .env.aws
docker compose --env-file .env.aws -f docker-compose.prod.yml config --quiet
docker compose --env-file .env.aws -f docker-compose.prod.yml up -d --build
```

The initial HTTP entry point is `http://<EC2_PUBLIC_IP>/`. `VITE_API_BASE_URL=/` and
`VITE_AI_API_BASE_URL=/ai` are build-time values; do not set them to localhost in AWS.
For a domain and HTTPS, update the public frontend URL, CORS origins, OAuth callback URLs,
and add TLS termination in front of the frontend before calling the deployment production-ready.

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
- Optional OAuth variables (`FRONTEND_URL`, provider client IDs/secrets, and
  redirect URIs) must be supplied through deployment secrets; do not commit
  provider credentials. See `docs/27_OAUTH_AUTHENTICATION.md`.
- The AI service reads `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` from deployment
  secrets and uses `AI_MODEL`, `AI_TEMPERATURE`, and `AI_MAX_TOKENS` from
  non-secret configuration.
- Gemini is the primary provider when `AI_PROVIDER=gemini`; its
  `GEMINI_API_KEY` is supplied through the local `.env` or Kubernetes Secret,
  and `GEMINI_MODEL` selects the model. If the selected provider is unavailable
  or unconfigured, deterministic agents continue to operate without claiming
  an LLM-backed result.
- AI-to-backend authentication uses `BACKEND_API_TOKEN` when configured,
  otherwise it logs in with `BACKEND_SERVICE_EMAIL` and
  `BACKEND_SERVICE_PASSWORD`. If a configured API token is rejected with
  `401 Unauthorized`, the client clears that stale token, performs one
  service-account login, and retries the protected request. Requests
  originating from an authenticated user always forward that user's bearer
  token and do not fall back to service credentials.
- The service account only needs a valid local user role for the currently
  protected read APIs (`infrastructure`, `incidents`, `metrics`, and `twins`);
  credentials must be supplied through local `.env`, Docker environment
  substitution, or Kubernetes Secret references. They are never committed.

### AWS security and operations

Use an EC2 Security Group with TCP 22 restricted to administrator IPs and TCP 80
temporarily open for HTTP testing. Open TCP 443 only after a domain and HTTPS
termination path are configured. Do not open TCP 5432, 8000, or 8001 publicly.
The PostgreSQL data remains in the named `postgres_data` Docker volume. Use
`docker compose --env-file .env.aws -f docker-compose.prod.yml down` for a safe stop;
never use `down -v` for routine operations.

To verify or inspect the deployment:

```bash
docker compose --env-file .env.aws -f docker-compose.prod.yml ps
curl http://localhost/api/v1/health
curl http://localhost/ai/api/v1/health
docker compose --env-file .env.aws -f docker-compose.prod.yml logs --tail=100 backend ai-service
```

To update, pull the reviewed commit and rebuild:

```bash
git pull --ff-only origin feature/containerization-database
docker compose --env-file .env.aws -f docker-compose.prod.yml up -d --build
```

Before production use, configure HTTPS with a real domain and certificate, take
database backups, and validate the EC2 host's disk, memory, patching, and monitoring.

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

### Local production-profile validation

The EC2-style Compose profile was validated locally with a protected `.env.aws` file:

- Nginx served the frontend on port `80`; backend, AI service, and PostgreSQL remained
  private to the Compose network.
- `/api/v1/health`, `/ai/status`, and `/ai/api/v1/health` returned HTTP 200.
- Authenticated infrastructure, metrics, Digital Twin, recommendations, simulation,
  orchestration, and CPU prediction requests completed successfully through the Nginx
  `/api/` and `/ai/` proxies.
- Unauthenticated and invalid-token protected API requests returned HTTP 401.
- The registration form displayed live password requirements, confirm-password validation,
  and retained Google/GitHub sign-in buttons.
- The stack was stopped and restarted with `docker compose ... down` followed by
  `docker compose ... up -d`; users, infrastructure, incidents, metrics, and twin rows
  remained available afterward. PostgreSQL data was preserved in the named
  `agenttwinops-main_postgres_data` volume.
- AWS deployment was not performed. HTTPS and a production domain remain deployment
  prerequisites.

Report exports use authenticated CSV downloads through
`/api/v1/reports/infrastructure` and `/api/v1/reports/incidents`. The files are
generated from persisted PostgreSQL infrastructure, latest metrics, Digital
Twin, and incident data. Prediction and simulation exports remain unavailable
because their current API results are transient and are not stored as report
history.

### Troubleshooting
- **AI Service `401 Unauthorized`**: If the AI service cannot reach the backend with authorization, ensure `BACKEND_SERVICE_EMAIL` and `BACKEND_SERVICE_PASSWORD` in `docker-compose.yml` match a registered backend user.
- **Backend Test Imports**: If running pytest natively, ensure `PYTHONPATH` does not conflict with the project root.
