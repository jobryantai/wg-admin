def generate_client_config(peer, server_public_key, server_endpoint, server_allowed_ips):
    return f"""
[Interface]
PrivateKey = {peer['client_private_key']}
Address = {peer['allowed_ips']}
DNS = 1.1.1.1

[Peer]
PublicKey = {server_public_key}
Endpoint = {server_endpoint}
AllowedIPs = {server_allowed_ips}
PersistentKeepalive = 25
"""
