#!/bin/bash
# chmod +x deploy.sh

VPS_USER="YOURUSER"
VPS_IP="YOUR_VPS_IP"

ssh ${VPS_USER}@${VPS_IP} "
  cd /opt/wg-admin &&
  git pull origin main &&
  source venv/bin/activate &&
  pip install -r requirements.txt &&
  sudo systemctl restart wg-admin
"

