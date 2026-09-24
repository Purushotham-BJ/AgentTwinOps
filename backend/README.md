# Backend

This directory hosts the Python backend service for AgentTwinOps.

## Responsibility

- Provide the API application shell for future FastAPI development.
- Hold infrastructure, configuration, and persistence scaffolding.
- Keep the implementation documentation-first until the service is ready.

## Database Migrations (Alembic)

This project uses Alembic for database migrations. The migration infrastructure is configured to use the application's asynchronous SQLAlchemy engine and loads the `DATABASE_URL` directly from the application settings.

### Migration Commands

Ensure your virtual environment is active before running migration commands.

- **Generate a new migration**:
  ```bash
  alembic revision --autogenerate -m "description_of_changes"
  ```
  *(Note: Always review generated migrations before applying them).*

- **Upgrade database to latest revision**:
  ```bash
  alembic upgrade head
  ```

- **Downgrade database by 1 revision**:
  ```bash
  alembic downgrade -1
  ```

- **Check current revision**:
  ```bash
  alembic current
  ```

- **View migration history**:
  ```bash
  alembic history
  ```

- **Generate SQL script for offline upgrade**:
  ```bash
  alembic upgrade head --sql
  ```

Migrations are stored in the `alembic/versions/` directory. The application's Declarative Base is automatically wired to Alembic's `target_metadata`.
