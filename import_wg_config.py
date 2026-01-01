#!/usr/bin/env python3
import psycopg2
import re

WG_CONF = "/etc/wireguard/wg0.conf"

def parse_wg_config():
    interface = {}
    peers = []

    current_peer = None

    with open(WG_CONF, "r") as f:
        for line in f:
            line = line.strip()

            if line.startswith("[Interface]"):
                current_peer = None
                continue

            if line.startswith("[Peer]"):
                if current_peer:
                    peers.append(current_peer)
                current_peer = {}
                continue

            if "=" in line:
                key, value = [x.strip() for x in line.split("=", 1)]

                # Interface fields
                if current_peer is None:
                    if key == "Address":
                        interface["address"] = value
                    elif key == "ListenPort":
                        interface["listen_port"] = int(value)
                    # PrivateKey intentionally ignored for safety

                # Peer fields
                else:
                    if key == "PublicKey":
                        current_peer["public_key"] = value
                    elif key == "AllowedIPs":
                        current_peer["allowed_ips"] = value
                    # PrivateKey ignored for safety

    if current_peer:
        peers.append(current_peer)

    return interface, peers


def insert_into_db(interface, peers):
    conn = psycopg2.connect(
        dbname="wgadmin_dev",
        user="wguser",
        password="devpassword",
        host="localhost"
    )
    cur = conn.cursor()

    # Insert interface
    cur.execute("""
        INSERT INTO interfaces (name, address, listen_port)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, ("wg0", interface["address"], interface["listen_port"]))

    # Insert peers
    for idx, peer in enumerate(peers, start=1):
        cur.execute("""
            INSERT INTO peers (name, public_key, allowed_ips)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (f"Imported Peer {idx}", peer["public_key"], peer["allowed_ips"]))

    conn.commit()
    cur.close()
    conn.close()


def main():
    interface, peers = parse_wg_config()
    insert_into_db(interface, peers)
    print("WireGuard configuration imported safely.")


if __name__ == "__main__":
    main()
