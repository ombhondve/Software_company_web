#!/usr/bin/env bash
# One-time setup on a fresh Amazon Linux 2023 EC2 instance.
# Run as ec2-user:  bash ec2_setup.sh
set -euo pipefail

sudo dnf update -y
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"

# Docker Compose v2 plugin
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

mkdir -p ~/task-api
if [ ! -f ~/task-api/.env ]; then
  cat > ~/task-api/.env <<ENV
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
POSTGRES_DB=taskdb
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENV
  chmod 600 ~/task-api/.env
fi

echo "Done. Log out and back in so the docker group applies."
