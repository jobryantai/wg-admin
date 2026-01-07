from flask import Blueprint, request, session, redirect, render_template, make_response, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from .qrcodegen import generate_qr_base64


from .db import get_db
from .auth import verify_user, login_required
from .peers import add_peer, list_peers, delete_peer, update_peer, get_peer_by_id
from .wgconfig_full import generate_full_config, write_config_safely, apply_config
from .wg import wg_show
from .audit import log_action

from time import time

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 5
attempts = {}

def too_many_attempts(ip):
    now = time()
    window_start = now - RATE_LIMIT_WINDOW
    attempts.setdefault(ip, [])
    attempts[ip] = [t for t in attempts[ip] if t > window_start]
    return len(attempts[ip]) >= RATE_LIMIT_MAX

def record_attempt(ip):
    attempts.setdefault(ip, []).append(time())

def retry_after_seconds(ip):
    if ip not in attempts or not attempts[ip]:
        return 0
    now = time()
    window_start = now - RATE_LIMIT_WINDOW
    recent = [t for t in attempts[ip] if t > window_start]
    if not recent:
        return 0
    oldest = min(recent)
    return int(RATE_LIMIT_WINDOW - (now - oldest))

bp = Blueprint("main", __name__)

# -----------------------------
# NEW: Full sync helper
# -----------------------------
def sync_full_config():
    config_text = generate_full_config()
    write_config_safely(config_text)
    apply_config()

# -----------------------------
# Health Check
# -----------------------------
@bp.route("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# Import Config
# -----------------------------
@bp.route("/import-config", methods=["GET", "POST"])
@login_required
def import_config():
    if request.method == "POST":
        file = request.files.get("config_file")
        if not file:
            flash("No file uploaded.")
            return render_template("import_config.html")
        flash("Config imported successfully.")
        return redirect("/dashboard")
    return render_template("import_config.html")

# -----------------------------
# Unified Entry Point
# -----------------------------
@bp.route("/")
@bp.route("/index.html")
def index():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    return render_template("dashboard.html")

# -----------------------------
# Login
# -----------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    ip = request.remote_addr
    if request.method == "POST":
        if too_many_attempts(ip):
            retry = retry_after_seconds(ip)
            return {
                "error": "too many attempts",
                "retry_after_seconds": retry,
                "message": f"Try again in {retry} seconds."
            }, 429
        record_attempt(ip)
        username = request.form.get("username")
        password = request.form.get("password")
        user = verify_user(username, password)
        if user:
            session["user_id"] = user["id"]
            log_action(user["id"], "login")
            return redirect("/")
        return {"error": "invalid credentials"}, 401
    return render_template("login.html")

# -----------------------------
# Logout
# -----------------------------
@bp.route("/logout")
def logout():
    log_action(session.get("user_id"), "logout")
    session.clear()
    return redirect("/login")

# -----------------------------
# Dashboard
# -----------------------------
@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# -----------------------------
# Peer List UI
# -----------------------------
@bp.route("/peers-ui")
@login_required
def peers_ui():
    peers = list_peers()
    return render_template("peers.html", peers=peers)

# -----------------------------
# Add Peer UI
# -----------------------------
@bp.route("/peers-ui/add", methods=["GET"])
@login_required
def peers_add_ui():
    return render_template("add_peer.html")

@bp.route("/peers-ui/add", methods=["POST"])
@login_required
def peers_add_ui_post():
    name = request.form.get("name")
    public_key = request.form.get("public_key")
    allowed_ips = request.form.get("allowed_ips")

    peer_id = add_peer(name, public_key, allowed_ips, session["user_id"])
    sync_full_config()

    log_action(session["user_id"], "add_peer", f"peer_id={peer_id}")
    return redirect("/peers-ui")

# -----------------------------
# Edit Peer UI
# -----------------------------
@bp.route("/peers-ui/<int:peer_id>/edit", methods=["GET"])
@login_required
def peers_edit_ui(peer_id):
    peer = get_peer_by_id(peer_id)
    if not peer:
        return {"error": "peer not found"}, 404
    return render_template("edit_peer.html", peer=peer)

@bp.route("/peers-ui/<int:peer_id>/edit", methods=["POST"])
@login_required
def peers_edit_ui_post(peer_id):
    name = request.form.get("name")
    allowed_ips = request.form.get("allowed_ips")

    peer = get_peer_by_id(peer_id)
    if not peer:
        return {"error": "peer not found"}, 404

    update_peer(peer_id, name, allowed_ips, session["user_id"])
    sync_full_config()

    log_action(session["user_id"], "edit_peer", f"peer_id={peer_id}")
    return redirect("/peers-ui")

# -----------------------------
# Delete Peer UI
# -----------------------------
@bp.route("/peers-ui/<int:peer_id>/delete", methods=["POST"])
@login_required
def peers_delete_ui(peer_id):
    peer = get_peer_by_id(peer_id)
    if peer:
        delete_peer(peer_id)
        sync_full_config()
        log_action(session["user_id"], "delete_peer", f"peer_id={peer_id}")
    return redirect("/peers-ui")

# -----------------------------
# Peer QR Code Generation
# -----------------------------
@bp.route("/peers-ui/<int:peer_id>/qr")
@login_required
def peer_qr(peer_id):
    peer = get_peer_by_id(peer_id)
    if not peer:
        return {"error": "peer not found"}, 404

    # Build the WireGuard config text for this peer
    config_text = f"""
[Interface]
PrivateKey = <client_private_key_here>
Address = {peer['allowed_ips']}

[Peer]
PublicKey = <server_public_key_here>
Endpoint = <server_endpoint_here>
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""

    # Generate QR code
    qr_b64 = generate_qr_base64(config_text)

    return render_template("peer_qr.html", peer=peer, qr_code=qr_b64, config_text=config_text)

# -----------------------------
# Sync WireGuard
# -----------------------------
@bp.route("/sync-wg")
@login_required
def sync_wg():
    sync_full_config()
    log_action(session["user_id"], "sync_full_config")
    return redirect("/dashboard")

# -----------------------------
# WireGuard Status
# -----------------------------
@bp.route("/wg-status")
@login_required
def wg_status():
    status = wg_show()
    return render_template("wg_status.html", status=status)

# -----------------------------
# Audit Log
# -----------------------------
@bp.route("/audit")
@login_required
def audit():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM audit_log ORDER BY created_at DESC;")
    logs = cur.fetchall()
    return render_template("audit.html", audit=logs)

# -----------------------------
# Change Password
# -----------------------------
@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        current_pw = request.form.get("current_password")
        new_pw = request.form.get("new_password")
        confirm_pw = request.form.get("confirm_password")

        cur.execute("SELECT * FROM users WHERE id = %s;", (session["user_id"],))
        user = cur.fetchone()

        if not check_password_hash(user["password_hash"], current_pw):
            flash("Current password is incorrect.")
            return render_template("change_password.html")

        if new_pw != confirm_pw:
            flash("New passwords do not match.")
            return render_template("change_password.html")

        new_hash = generate_password_hash(new_pw)
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s;",
            (new_hash, user["id"])
        )
        db.commit()

        flash("Password updated successfully.")
        return redirect("/dashboard")

    return render_template("change_password.html")
