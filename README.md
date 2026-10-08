# Simple Task Management API

A RESTful API for personal task management built with **FastAPI**, **PostgreSQL**, and **JWT** auth.
Dockerized, tested with pytest (>= 80% coverage), CI/CD via GitHub Actions, deployed to AWS EC2.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/users/register` | no | Create a user (`email`, `password` 8-72 chars) |
| POST | `/users/login` | no | Returns `{"access_token": "...", "token_type": "bearer"}` |
| GET | `/tasks` | yes | List the current user's tasks |
| POST | `/tasks` | yes | Create a task |
| PUT | `/tasks/{id}` | yes | Update a task |
| DELETE | `/tasks/{id}` | yes | Delete a task (204) |
| GET | `/health` | no | Liveness check |

Invalid payloads return **400**. Missing/invalid tokens return **401**. Another user's task returns **404**.
Interactive docs: `/docs` (Swagger, use *Authorize* and paste the token) and `/openapi.json`.

## Run locally with Docker

```bash
cp .env.example .env        # edit secrets
docker compose up --build
# API: http://localhost:8000/docs
```

## Run locally without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
docker compose up -d db                     # just PostgreSQL
export DATABASE_URL=postgresql+psycopg2://taskuser:change-me@localhost:5432/taskdb
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
uvicorn app.main:app --reload
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest          # uses in-memory SQLite; fails if coverage < 80%
```

## Quick demo

```bash
curl -X POST localhost:8000/users/register -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"password123"}'
TOKEN=$(curl -s -X POST localhost:8000/users/login -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"password123"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -X POST localhost:8000/tasks -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"title":"Ship it"}'
curl localhost:8000/tasks -H "Authorization: Bearer $TOKEN"
```

## Deploy to AWS EC2

1. **Launch EC2**: Amazon Linux 2023, t3.micro/t2.micro. **Security group**: inbound TCP 22 (your IP only) and TCP 80 (0.0.0.0/0). Do not open 5432.
2. **One-time setup** on the instance:
   ```bash
   scp scripts/ec2_setup.sh ec2-user@<EC2_IP>:~
   ssh ec2-user@<EC2_IP> 'bash ec2_setup.sh'
   ```
   This installs Docker + Compose and generates `~/task-api/.env` with random secrets.
3. **GitHub repo secrets** (Settings > Secrets and variables > Actions):
   - `EC2_HOST` - public IP or DNS
   - `EC2_USER` - `ec2-user`
   - `EC2_SSH_KEY` - contents of the private key (.pem) for the instance
4. Push to `main`. `.github/workflows/deploy.yml` runs tests, builds and pushes the image to GHCR, then SSHes to EC2 and runs `docker compose up -d`, followed by a `/health` smoke test.
5. Your deployed API URL: `http://<EC2_IP>/docs`

`.github/workflows/ci.yml` runs on every push/PR: pytest with the coverage gate, plus a Docker build that fails if the image exceeds 150 MB.

## Project layout

```
app/
  main.py        app, logging middleware, 400 validation handler, health
  config.py      env-based settings
  database.py    SQLAlchemy engine/session
  models.py      User, Task
  schemas.py     Pydantic models
  security.py    bcrypt hashing, JWT create/verify
  deps.py        get_current_user dependency
  routers/       users.py, tasks.py
tests/           pytest suite (service/security + API integration via httpx TestClient)
scripts/         ec2_setup.sh, deploy.sh
Dockerfile       multi-stage, alpine, non-root
docker-compose.yml / docker-compose.prod.yml
```

## Notes

- Set a strong `SECRET_KEY` in production; the default is for local dev only.
- Tables are created on startup (`create_all`). For schema changes beyond a demo, add Alembic.
