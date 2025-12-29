#!/bin/bash

# --- System Update ---
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# --- Install Docker ---
#sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# --- Create Gitea Directories ---
sudo mkdir -p /srv/gitea/{data,config}
sudo chown -R 1000:1000 /srv/gitea

# --- Create Docker Compose File ---
cat <<EOF | sudo tee /srv/gitea/docker-compose.yml
version: "3"

services:
  gitea:
    image: gitea/gitea:latest
    container_name: gitea
    environment:
      - USER_UID=1000
      - USER_GID=1000
    volumes:
      - /srv/gitea/data:/data
    ports:
      - "3000:3000"
      - "2222:22"
    restart: always
EOF

# --- Start Gitea ---
cd /srv/gitea
sudo docker compose up -d
