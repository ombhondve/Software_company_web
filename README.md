# Simple Task Management API

A REST API built with FastAPI, PostgreSQL, SQLAlchemy, and JWT authentication. It includes CRUD endpoints, OpenAPI documentation, Docker configuration, automated tests, and an AWS EC2 deployment workflow.

## Features

- User registration and login with bcrypt password hashing.
- JWT bearer authentication for protected routes.
- Per-user task CRUD with ownership checks.
- PostgreSQL persistence through SQLAlchemy.
- Interactive OpenAPI docs at `/docs` and schema at `/openapi.json`.
- Health endpoints at `/health` and `/health/db`.
- Docker Compose for local development and production.
- GitHub Actions test, image-build, and deployment workflows.

## API endpoints

| Method | Path | Authentication | Description |
|---|---|---|---|
| POST | `/users/register` | No | Register a user |
| POST | `/users/login` | No | Obtain a JWT access token |
| GET | `/tasks` | Bearer token | List your tasks |
| POST | `/tasks` | Bearer token | Create a task |
| PUT | `/tasks/{task_id}` | Bearer token | Update one of your tasks |
| DELETE | `/tasks/{task_id}` | Bearer token | Delete one of your tasks |
| GET | `/health` | No | Liveness check |
| GET | `/health/db` | No | Database connectivity check |

Invalid request payloads return HTTP 400. Invalid or missing credentials return HTTP 401. A task not owned by the authenticated user returns HTTP 404.

## Run locally with Docker

1. Copy `.env.example` to `.env` and change the secrets.
2. Start the application and PostgreSQL:

   ```bash
   docker compose up --build
   ```

3. Open [http://localhost:8000/docs](http://localhost:8000/docs).

## Run locally without Docker

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
docker compose up -d db
```

Set `DATABASE_URL` to a PostgreSQL connection string and set a strong random `SECRET_KEY`. Start the API:

```bash
uvicorn app.main:app --reload
```

## Run tests

```bash
pip install -r requirements-dev.txt
pytest
```

The configured pytest coverage gate requires at least 80% coverage.

## Quick API example

Register and log in using `/docs`, then click **Authorize** and paste the returned access token. You can then create and list tasks using the protected endpoints.

## Docker and AWS EC2 deployment

The deployment workflow is stored at `.github/workflows/deploy.yml`. It runs tests, builds and pushes a container image to GitHub Container Registry, deploys over SSH, and checks the `/health` endpoint.

Follow [the deployment and evidence guide](docs/DEPLOYMENT.md) for exact validation commands, EC2 setup, GitHub Actions secrets, health checks, and the screenshots needed to demonstrate a real deployment. **The existence of deployment configuration alone is not proof that a live EC2 deployment succeeded.** Capture genuine evidence only after your own deployment passes.

Required GitHub repository Actions secrets:

- `EC2_HOST`: EC2 public IP address or DNS name.
- `EC2_USER`: SSH user, typically `ec2-user`.
- `EC2_SSH_KEY`: private SSH key contents for the instance.

On a fresh Amazon Linux 2023 instance, run `scripts/ec2_setup.sh` as `ec2-user`. The script installs Docker and Compose and creates `~/task-api/.env` with generated secrets. The deployment workflow copies `docker-compose.prod.yml` to `~/task-api`. Do not expose PostgreSQL port 5432 publicly; allow SSH only from trusted IPs and HTTP/HTTPS as needed.

Before handling real users or sensitive data, configure HTTPS, a domain and reverse proxy or load balancer, restrictive security-group rules, secret rotation, database backups, monitoring, dependency updates, and database migrations (for example Alembic). Keep PostgreSQL private.

## Project layout

```text
app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  security.py
  deps.py
  routers/
    __init__.py
    users.py
    tasks.py
tests/
  conftest.py
  test_auth.py
  test_tasks.py
  test_security.py
scripts/
  ec2_setup.sh
  deploy.sh
docs/
  DEPLOYMENT.md
.github/
  workflows/
    ci.yml
    deploy.yml
Dockerfile
docker-compose.yml
docker-compose.prod.yml
requirements.txt
requirements-dev.txt
.env.example
```

## Security notes

Use a strong, unique `SECRET_KEY` in production and never commit real credentials. The fallback key in `config.py` is for local development only. Database tables are currently initialized with SQLAlchemy `create_all`; use a migration tool such as Alembic when evolving a production schema.
