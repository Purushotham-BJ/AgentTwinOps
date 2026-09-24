from pathlib import Path

base = Path(__file__).resolve().parents[1]

# Create top-level directories
for folder in [
    base / "backend",
    base / "backend" / "app",
    base / "backend" / "app" / "api",
    base / "backend" / "app" / "core",
    base / "backend" / "app" / "config",
    base / "backend" / "app" / "database",
    base / "backend" / "app" / "models",
    base / "backend" / "app" / "schemas",
    base / "backend" / "app" / "repositories",
    base / "backend" / "app" / "services",
    base / "backend" / "app" / "middleware",
    base / "backend" / "app" / "security",
    base / "backend" / "app" / "utils",
    base / "backend" / "app" / "dependencies",
    base / "backend" / "app" / "exceptions",
    base / "backend" / "app" / "tests",
    base / "backend" / "alembic",
    base / "backend" / "scripts",
    base / "backend" / "requirements",
    base / "frontend",
    base / "docs",
    base / "shared",
    base / "scripts",
]:
    folder.mkdir(parents=True, exist_ok=True)

# Root files
(base / "README.md").write_text(
    """# AgentTwinOps\n\nAgentTwinOps is a documentation-first architecture scaffold for an AI-powered Digital Twin + Multi-Agent DevOps platform.\n\n## Repository intent\n\nThis repository currently contains the complete project structure for future implementation.\nNo business logic, API handlers, authentication flows, or database models have been implemented yet.\n\n## Current structure\n\n- Backend: FastAPI + SQLAlchemy + Alembic + PostgreSQL + Redis + MongoDB\n- Frontend: React + TypeScript + Vite + TailwindCSS + React Query\n- Shared: cross-cutting contracts and utilities for later use\n- Docs: project documentation and architectural references\n""",
    encoding="utf-8",
)

if not (base / ".gitignore").exists():
    (base / ".gitignore").write_text(
        """# Local environment and generated artifacts\n__pycache__/\n*.py[cod]\n.env\n.env.*\nnode_modules/\n""",
        encoding="utf-8",
    )

# Backend files
(base / "backend" / "__init__.py").write_text('"""Backend package placeholder for AgentTwinOps."""\n', encoding="utf-8")
(base / "backend" / "README.md").write_text(
    """# Backend\n\nThis directory hosts the Python backend service for AgentTwinOps.\n\n## Responsibility\n\n- Provide the API application shell for future FastAPI development.\n- Hold infrastructure, configuration, and persistence scaffolding.\n- Keep the implementation documentation-first until the service is ready.\n""",
    encoding="utf-8",
)
(base / "backend" / ".env.example").write_text(
    """# Environment configuration placeholder for local development\n# The actual values will be provided during implementation.\n\nAPP_ENV=development\nAPP_DEBUG=true\nDATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/agenttwinops\nREDIS_URL=redis://localhost:6379/0\nMONGODB_URI=mongodb://localhost:27017/agenttwinops\nJWT_SECRET_KEY=replace-me\n""",
    encoding="utf-8",
)
(base / "backend" / "pyproject.toml").write_text(
    """[project]\nname = \"agenttwinops-backend\"\nversion = \"0.1.0\"\ndescription = \"Documentation-first scaffold for AgentTwinOps backend\"\nrequires-python = \">=3.12\"\ndependencies = [\n  \"fastapi\",\n  \"uvicorn\",\n  \"sqlalchemy>=2.0\",\n  \"alembic\",\n  \"psycopg[binary]\",\n  \"redis\",\n  \"pymongo\",\n  \"pydantic>=2.0\",\n  \"python-jose[cryptography]\",\n]\n""",
    encoding="utf-8",
)
(base / "backend" / "requirements.txt").write_text(
    """# Backend dependency placeholders\nfastapi\nuvicorn\nsqlalchemy>=2.0\nalembic\npsycopg[binary]\nredis\npymongo\npydantic>=2.0\npython-jose[cryptography]\n""",
    encoding="utf-8",
)
(base / "backend" / "requirements" / "README.md").write_text(
    """# Requirements\n\nThis directory is intended for dependency and environment-specific requirement files.\n\n## Responsibility\n\n- Hold optional requirement sets for development, testing, and production.\n- Keep installation details explicit and version-driven.\n""",
    encoding="utf-8",
)
(base / "backend" / "scripts" / "README.md").write_text(
    """# Backend Scripts\n\nThis directory is reserved for local maintenance and development utilities.\n\n## Responsibility\n\n- Hold project helper scripts for setup and future operational tasks.\n- Keep scripts isolated from application runtime code.\n""",
    encoding="utf-8",
)
(base / "backend" / "alembic" / "README.md").write_text(
    """# Alembic Migrations\n\nThis directory will contain database migration files and migration configuration.\n\n## Responsibility\n\n- Store migration scripts for SQLAlchemy models.\n- Keep schema evolution organized and versioned.\n""",
    encoding="utf-8",
)

# App package
(base / "backend" / "app" / "__init__.py").write_text('"""Application package placeholder for AgentTwinOps backend."""\n', encoding="utf-8")
(base / "backend" / "app" / "README.md").write_text(
    """# App Package\n\nThis package contains the backend application modules for AgentTwinOps.\n\n## Responsibility\n\n- Organize the backend into layered, dependency-friendly modules.\n- Preserve clean architecture boundaries between transport, domain, persistence, and infrastructure concerns.\n- Remain free of business logic until the implementation phase begins.\n""",
    encoding="utf-8",
)
(base / "backend" / "app" / "main.py").write_text(
    """\"\"\"FastAPI application entry point placeholder.\"\"\"\n\n# The application factory, router registration, and service wiring will be added later.\n# This file intentionally remains a structural placeholder.\n\nfrom fastapi import FastAPI\n\napp = FastAPI(title=\"AgentTwinOps API\", version=\"0.1.0\")\n""",
    encoding="utf-8",
)

# Package placeholders
for rel in [
    "api",
    "core",
    "config",
    "database",
    "models",
    "schemas",
    "repositories",
    "services",
    "middleware",
    "security",
    "utils",
    "dependencies",
    "exceptions",
    "tests",
]:
    pkg_dir = base / "backend" / "app" / rel
    (pkg_dir / "__init__.py").write_text(f'"""{rel} package placeholder for AgentTwinOps."""\n', encoding="utf-8")
    (pkg_dir / "README.md").write_text(
        f"""# {rel.title()}\n\nThis directory is reserved for the {rel} concern in the backend application.\n\n## Responsibility\n\n- Contain the {rel} modules for the future implementation.\n- Preserve architecture boundaries and keep the package intentionally lightweight.\n- Avoid business logic until the implementation phase begins.\n""",
        encoding="utf-8",
    )

# Frontend/docs/shared/scripts
(base / "frontend" / "README.md").write_text(
    """# Frontend\n\nThis directory will host the React + TypeScript frontend application for AgentTwinOps.\n\n## Responsibility\n\n- Contain the Vite-based client shell and future UI modules.\n- Keep the presentation layer separate from the backend service.\n- Remain free of business logic until implementation begins.\n""",
    encoding="utf-8",
)
(base / "docs" / "README.md").write_text(
    """# Documentation\n\nThis directory holds the project documentation set for AgentTwinOps.\n\n## Responsibility\n\n- Preserve the architecture, requirements, roadmap, and implementation references.\n- Keep documentation aligned with the evolving system design.\n- Support the documentation-first workflow for the project.\n""",
    encoding="utf-8",
)
(base / "shared" / "README.md").write_text(
    """# Shared\n\nThis directory is reserved for cross-cutting assets shared across backend and frontend concerns.\n\n## Responsibility\n\n- Hold shared contracts, schemas, or utility modules when they are introduced.\n- Provide a neutral layer for reusable content that spans multiple parts of the system.\n""",
    encoding="utf-8",
)
(base / "scripts" / "README.md").write_text(
    """# Repository Scripts\n\nThis directory hosts repository-level helper scripts.\n\n## Responsibility\n\n- Provide workspace-level automation and maintenance helpers.\n- Keep cross-project tooling separate from service-specific code.\n""",
    encoding="utf-8",
)

print("Scaffold created successfully.")
