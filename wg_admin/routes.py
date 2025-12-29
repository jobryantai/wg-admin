from flask import Blueprint, request, session, redirect, url_for, render_template, make_response
from .db import get_db
from .auth import verify_user, login_required
from .peers import add_peer, list_peers, delete_peer
from .wgconfig import generate_client_config
from .audit import log_action
from .qrcodegen import generate_qr_base64
from .wg import wg_add_peer, wg_remove_peer, wg_show

bp = Blueprint("main", __name__)


# -----------------------------
# Health Check
# -----------------------------
@bp.route("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# DB Test
# -----------------------------
@bp.route("/db-test")
def db_test():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM test_table LIMIT 1;")
    row = cur.fetchone()
    return row or {"error": "no data"}


# -----------------------------
# Authentication
# -----------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = verify_user(username, password)
        if user:
            session["user_id"] = user["id"]
            log_action(user["id"], "login")
            return {"status": "logged_in"}

        return {"error": "invalid credentials"}, 401

    return """
    <form method="POST">
        <input name="username" placeholder="username">
        <input name="password" type="password" placeholder="password">
        <button>Login</button>
    </form>
    """


@bp.route("/logout")
def logout():
    log_action(session.get("user_id"), "logout")
    session.clear()
    return {"status": "logged_out"}


# -----------------------------
# Admin Dashboard UI
# -----------------------------
@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", title="Dashboard")


# -----------------------------
# Peer Management UI
# -----------------------------
@bp.route("/peers-ui")
@login_required
def peers_ui():
    peers = list_peers()
    return render_template("peers.html", peers=peers, title="Peers")


# Add Peer UI (GET)
@bp.route("/peers-ui/add", methods=["GET"])
@login_required
def peers_add_ui():
    return render_template("add_peer.html", title="Add Peer")


# Add Peer UI (POST)
@bp.route("/peers-ui/add", methods=["POST"])
@login_required
def peers_add_ui_post():
    name = request.form.get("name")
    public_key = request.form.get("public_key")
    allowed_ips = request.form.get("allowed_ips")

    peer_id = add_peer(name, public_key, allowed_ips, session["user_id"])

    # Apply to WireGuard
    wg_add_peer(public_key, allowed_ips)
    log_action(session["user_id"], "wg_add_peer", f"{public_key} {allowed_ips}")

    log_action(session["user_id"], "add_peer", f"peer_id={peer_id}, name={name}")
    return redirect("/peers-ui")
@bp.route("/sync-wg")
@login_required
def sync_wg():
    db = get_db()
    cur = db.cursor()

    # Get DB peers
    cur.execute("SELECT public_key, allowed_ips FROM peers;")
    db_peers = cur.fetchall()

    # Get wg0 peers
    wg_peers = wg_dump()

    if wg_peers is None:
        return {"error": "wg0 not available"}, 500

    db_pubkeys = {p["public_key"]: p["allowed_ips"] for p in db_peers}
    wg_pubkeys = set(wg_peers)

    # Peers missing in wg0 → add them
    for pubkey, allowed_ips in db_pubkeys.items():
        if pubkey not in wg_pubkeys:
            wg_add_peer(pubkey, allowed_ips)
            log_action(session["user_id"], "sync_add_peer", pubkey)

    # Peers in wg0 but not in DB → remove them
    for pubkey in wg_pubkeys:
        if pubkey not in db_pubkeys:
            wg_remove_peer(pubkey)
            log_action(session["user_id"], "sync_remove_peer", pubkey)

    log_action(session["user_id"], "sync_complete")

    return redirect("/dashboard")

@bp.route("/peers-ui/<int:peer_id>/edit", methods=["GET"])
@login_required
def peers_edit_ui(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM peers WHERE id = %s;", (peer_id,))
    peer = cur.fetchone()

    if not peer:
        return {"error": "peer not found"}, 404

    return render_template("edit_peer.html", peer=peer, title="Edit Peer")
@bp.route("/peers-ui/<int:peer_id>/edit", methods=["POST"])
@login_required
def peers_edit_ui_post(peer_id):
    name = request.form.get("name")
    allowed_ips = request.form.get("allowed_ips")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT public_key FROM peers WHERE id = %s;", (peer_id,))
    peer = cur.fetchone()

    if not peer:
        return {"error": "peer not found"}, 404

    public_key = peer["public_key"]

    # Update DB
    update_peer(peer_id, name, allowed_ips, session["user_id"])

    # Update WireGuard live interface
    wg_add_peer(public_key, allowed_ips)

    log_action(session["user_id"], "edit_peer", f"peer_id={peer_id}, name={name}, allowed_ips={allowed_ips}")

    return redirect("/peers-ui")

# Peer Config UI
@bp.route("/peers-ui/<int:peer_id>/config")
@login_required
def peer_config_ui(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM peers WHERE id = %s;", (peer_id,))
    peer = cur.fetchone()

    if not peer:
        return {"error": "peer not found"}, 404

    server_public_key = "SERVER_PUBLIC_KEY_HERE"
    server_endpoint = "vpn.example.com:51820"
    server_allowed_ips = "0.0.0.0/0"

    config = generate_client_config(peer, server_public_key, server_endpoint, server_allowed_ips)

    log_action(session["user_id"], "view_config_ui", f"peer_id={peer_id}")
    return render_template("peer_config.html", config=config, peer_id=peer_id, title="Peer Config")


# -----------------------------
# Download Config (NEW)
# -----------------------------
@bp.route("/peers-ui/<int:peer_id>/download")
@login_required
def peer_config_download(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM peers WHERE id = %s;", (peer_id,))
    peer = cur.fetchone()

    if not peer:
        return {"error": "peer not found"}, 404

    server_public_key = "SERVER_PUBLIC_KEY_HERE"
    server_endpoint = "vpn.example.com:51820"
    server_allowed_ips = "0.0.0.0/0"

    config = generate_client_config(peer, server_public_key, server_endpoint, server_allowed_ips)

    log_action(session["user_id"], "download_config", f"peer_id={peer_id}")

    response = make_response(config)
    response.headers["Content-Type"] = "text/plain"
    response.headers["Content-Disposition"] = f"attachment; filename=peer-{peer_id}.conf"

    return response


# -----------------------------
# QR Code UI
# -----------------------------
@bp.route("/peers-ui/<int:peer_id>/qr")
@login_required
def peer_qr_ui(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM peers WHERE id = %s;", (peer_id,))
    peer = cur.fetchone()

    if not peer:
        return {"error": "peer not found"}, 404

    server_public_key = "SERVER_PUBLIC_KEY_HERE"
    server_endpoint = "vpn.example.com:51820"
    server_allowed_ips = "0.0.0.0/0"

    config = generate_client_config(peer, server_public_key, server_endpoint, server_allowed_ips)
    qr_data = generate_qr_base64(config)

    log_action(session["user_id"], "view_qr", f"peer_id={peer_id}")
    return render_template("peer_qr.html", qr_data=qr_data, config=config, title="QR Code")


# -----------------------------
# WireGuard Status UI (NEW)
# -----------------------------
@bp.route("/wg-status")
@login_required
def wg_status():
    status = wg_show()
    log_action(session["user_id"], "wg_status")
    return render_template("wg_status.html", status=status, title="WireGuard Status")


# -----------------------------
# Audit Log UI
# -----------------------------
@bp.route("/audit-ui")
@login_required
def audit_ui():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 100;")
    logs = cur.fetchall()
    return render_template("audit.html", audit=logs, title="Audit Log")


# -----------------------------
# Peer Management API
# -----------------------------
@bp.route("/peers", methods=["GET"])
@login_required
def peers_list():
    peers = list_peers()
    return {"peers": peers}


@bp.route("/peers", methods=["POST"])
@login_required
def peers_add():
    name = request.form.get("name")
    public_key = request.form.get("public_key")
    allowed_ips = request.form.get("allowed_ips")

    peer_id = add_peer(name, public_key, allowed_ips, session["user_id"])

    # Apply to WireGuard
    wg_add_peer(public_key, allowed_ips)
    log_action(session["user_id"], "wg_add_peer", f"{public_key} {allowed_ips}")

    log_action(session["user_id"], "add_peer", f"peer_id={peer_id}, name={name}")
    return {"status": "peer_added", "peer_id": peer_id}


@bp.route("/peers/<int:peer_id>", methods=["DELETE"])
@login_required
def peers_delete(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT public_key FROM peers WHERE id = %s", (peer_id,))
    peer = cur.fetchone()

    if peer:
        wg_remove_peer(peer["public_key"])
        log_action(session["user_id"], "wg_remove_peer", peer["public_key"])

    delete_peer(peer_id)
    log_action(session["user_id"], "delete_peer", f"peer_id={peer_id}")

    return {"status": "peer_deleted"}


# -----------------------------
# Peer Config Generation API
# -----------------------------
@bp.route("/peers/<int:peer_id>/config")
@login_required
def peer_config(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM peers WHERE id = %s;", (peer_id,))
    peer = cur.fetchone()

    if not peer:
        return {"error": "peer not found"}, 404

    server_public_key = "SERVER_PUBLIC_KEY_HERE"
    server_endpoint = "vpn.example.com:51820"
    server_allowed_ips = "0.0.0.0/0"

    config = generate_client_config(peer, server_public_key, server_endpoint, server_allowed_ips)

    log_action(session["user_id"], "generate_config", f"peer_id={peer_id}")
    return {"config": config}


# -----------------------------
# Audit Log API
# -----------------------------
@bp.route("/audit")
@login_required
def audit_list():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 100;")
    logs = cur.fetchall()
    return {"audit": logs}

