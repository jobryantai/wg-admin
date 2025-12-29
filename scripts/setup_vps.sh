#!/bin/bash

# --- System Update ---
sudo apt update && sudo apt upgrade -y

# --- Install Postgres ---
sudo apt install -y postgresql postgresql-contrib

# --- Create Database + User ---
sudo -u postgres psql <<EOF
CREATE DATABASE wgadmin;
CREATE USER wguser WITH PASSWORD 'CHANGE_ME';
GRANT ALL PRIVILEGES ON DATABASE wgadmin TO wguser;
EOF

# --- Install Python Environment ---
sudo apt install -y python3 python3-venv python3-pip
sudo mkdir -p /opt/wg-admin
sudo chown $USER:$USER /opt/wg-admin
cd /opt/wg-admin
python3 -m venv venv

# --- Install WireGuard ---
sudo apt install -y wireguard

# --- Enable WireGuard Interface (wg0 must exist) ---
sudo systemctl enable wg-quick@wg0

# --- Create systemd Service ---
sudo tee /etc/systemd/system/wg-admin.service > /dev/null <<EOF
[Unit]
Description=WireGuard Admin Panel
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/wg-admin
ExecStart=/opt/wg-admin/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable wg-admin

