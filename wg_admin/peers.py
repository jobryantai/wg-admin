from .db import get_db

def list_peers():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM peers ORDER BY id;")
    return cur.fetchall()


def get_peer_by_id(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM peers WHERE id = %s;", (peer_id,))
    return cur.fetchone()


def add_peer(name, public_key, allowed_ips, user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO peers (name, public_key, allowed_ips, created_by)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (name, public_key, allowed_ips, user_id))
    peer_id = cur.fetchone()["id"]
    db.commit()
    return peer_id


def update_peer(peer_id, name, allowed_ips, user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        UPDATE peers
        SET name = %s, allowed_ips = %s
        WHERE id = %s;
    """, (name, allowed_ips, peer_id))
    db.commit()


def delete_peer(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM peers WHERE id = %s;", (peer_id,))
    db.commit()
