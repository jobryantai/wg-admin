#!/bin/bash

WG_DIR="/etc/wireguard"
WG_IF="wg0"
WG_PORT=51820
WG_NET="10.8.0.0/24"

sudo mkdir -p ${WG_DIR}
cd ${WG_DIR}

# Generate keys
wg genkey | sudo tee server_private.key > /dev/null
sudo cat server_private.key | wg pubkey | sudo tee server_public.key > /dev/null

SERVER_PRIV=$(sudo cat server_private.key)
SERVER_PUB=$(sudo cat server_public.key)

# Create wg0.conf
sudo tee ${WG_DIR}/${WG_IF}.conf > /dev/null <<EOF
[Interface]
Address = 10.8.0.1/24
ListenPort = ${WG_PORT}
PrivateKey = ${SERVER_PRIV}
SaveConfig = true

EOF

sudo chmod 600 ${WG_DIR}/${WG_IF}.conf

# Enable service
sudo systemctl enable wg-quick@${WG_IF}
sudo systemctl start wg-quick@${WG_IF}

