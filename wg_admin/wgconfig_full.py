import os
from .db import get_db

WG_CONF_PATH = "/etc/wireguard/wg0.conf"
WG_TMP_PATH = "/etc/wireguard/wg0.conf.tmp"
WG_BACKUP_PATH = "/etc/wireguard/wg0.conf.bak"


def generate_full_config():
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM interfaces LIMIT 1;")
    iface = cur.fetchone()
    if not iface:
        raise Exception("No interface row found in DB")

    config = []
    config.append("[Interface]")
    config.append(f"Address = {iface['address']}")
    config.append(f"ListenPort = {iface['listen_port']}")
    config.append(f"PrivateKey = {iface['private_key']}")
    config.append("")

    cur.execute("SELECT public_key, allowed_ips FROM peers ORDER BY id;")
    peers = cur.fetchall()

    for p in peers:
        config.append("[Peer]")
        config.append(f"PublicKey = {p['public_key']}")
        config.append(f"AllowedIPs = {p['allowed_ips']}")
        config.append("")

    return "\n".join(config)


def write_config_safely(config_text):
    os.system(f"sudo cp {WG_CONF_PATH} {WG_BACKUP_PATH}")
    with open(WG_TMP_PATH, "w") as f:
        f.write(config_text)
    os.system(f"sudo mv {WG_TMP_PATH} {WG_CONF_PATH}")


def apply_config():
    os.system(f"sudo wg syncconf wg0 {WG_CONF_PATH}")
