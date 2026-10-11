# Docker and AWS EC2 Deployment Guide

This document explains how to reproduce the container build and EC2 deployment. It is not a claim that a live AWS deployment has already succeeded. Keep real evidence from your own environment in the submission.

## 1. Validate the repository locally

Run these commands from the repository root:

```bash
python -m pip install -r requirements-dev.txt
pytest
docker build -t task-api:local .
docker compose config
docker compose up --build -d
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/openapi.json
docker compose ps
docker compose logs --tail=100 api
docker compose down
```

Do not proceed to deployment until tests, image build, compose validation, and health checks pass. On Windows PowerShell, use the same commands where available; install Docker Desktop and ensure Docker Engine is running first.

## 2. Prepare an EC2 host

1. Create an Amazon Linux 2023 EC2 instance.
2. Configure the security group to allow SSH (TCP 22) only from your own IP. Allow HTTP (TCP 80) for a public demo. Do not expose PostgreSQL port 5432.
3. Connect with SSH and run `scripts/ec2_setup.sh`.
4. Log out and back in so the Docker group membership takes effect.
5. Confirm Docker and Compose work: `docker --version` and `docker compose version`.
6. Ensure the instance has sufficient disk space and outbound access to pull container images.

The setup script creates `~/task-api/.env` with random database and JWT secrets. Keep that file private and never commit it.

## 3. Configure GitHub Actions secrets

Under **Repository Settings → Secrets and variables → Actions**, add:

- `EC2_HOST`: public IPv4 address or DNS name.
- `EC2_USER`: usually `ec2-user`.
- `EC2_SSH_KEY`: complete private key for the EC2 host.

The deployment workflow uses the GitHub Actions token to publish the image to GHCR. The EC2 host must be able to authenticate and pull that package. If the GHCR package is private, configure a read-only package token on the instance or make the package public intentionally. Never paste tokens into logs or commit them.

## 4. Trigger and verify deployment

After the workflow files are on the default branch and the required secrets are configured, push a commit to `main`. In **Actions**, inspect both test and deploy jobs.

On the EC2 host, verify:

```bash
cd ~/task-api
docker compose -f docker-compose.prod.yml --env-file .env ps
docker compose -f docker-compose.prod.yml --env-file .env logs --tail=100 api
curl --fail http://127.0.0.1/health
```

From your own computer, verify the public endpoint:

```bash
curl --fail http://<EC2_PUBLIC_IP>/health
curl --fail http://<EC2_PUBLIC_IP>/openapi.json
```

Expected health response:

```json
{"status":"ok"}
```

Do not describe deployment as successful unless the Actions deployment job, EC2 container status, and public health request have all succeeded.

## 5. Capture genuine submission evidence

Capture your own screenshots after the commands above pass. Recommended files:

- `docs/evidence/01-github-actions-green.png`: successful CI and deployment jobs.
- `docs/evidence/02-docker-image.png`: local image build and `docker images task-api`.
- `docs/evidence/03-ec2-containers.png`: `docker compose ps` showing healthy/running services.
- `docs/evidence/04-public-health.png`: browser or terminal showing the public `/health` response.
- `docs/evidence/05-openapi-docs.png`: live `/docs` page.
- `docs/evidence/06-protected-endpoint.png`: Swagger authorization and a successful authenticated task request, with tokens and personal data hidden.

Only include screenshots from a real run. Never create mock screenshots or claim that an untested host is deployed. If a public EC2 IP is not available, say that deployment is configured but not yet verified.

## 6. Production caveats

This is a learning/demo deployment. Before handling real users or sensitive data, configure HTTPS, a domain and reverse proxy or load balancer, restrictive security-group rules, secret rotation, database backups, monitoring, dependency updates, and database migrations (for example Alembic). Keep PostgreSQL private. Do not use the development fallback JWT key in production.
