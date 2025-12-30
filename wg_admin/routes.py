from flask import Blueprint, request, session, redirect, url_for, render_template, make_response
from .db import get_db
from .qrcodegen import generate_qr_base64
from .wg import sync_wg_interface, get_wg_status
from .audit import log_action

bp = Blueprint("main", __name__)

# Root redirect (new)
@bp.route("/")
def root_redirect():
    return redirect(url_for("main.login"))

@bp.route("/health")
def health():
    return {"status": "ok"}

@bp.route("/db-test")
def db_test():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT 1")
    return {"db": "ok"}

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin":
            session["user"] = username
            log_action("login", f"User {username} logged in")
            return redirect(url_for("main.dashboard"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@bp.route("/logout")
def logout():
    user = session.get("user")
    session.clear()
    log_action("logout", f"User {user} logged out")
    return redirect(url_for("main.login"))

@bp.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("main.login"))
    return render_template("dashboard.html")

@bp.route("/peers-ui")
def peers_ui():
    if "user" not in session:
        return redirect(url_for("main.login"))
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name, public_key FROM peers")
    peers = cur.fetchall()
    return render_template("peers.html", peers=peers)

@bp.route("/peers-ui/add", methods=["GET"])
def peers_add_get():
    if "user" not in session:
        return redirect(url_for("main.login"))
    return render_template("peers_add.html")

@bp.route("/peers-ui/add", methods=["POST"])
def peers_add_post():
    if "user" not in session:
        return redirect(url_for("main.login"))

    name = request.form.get("name")
    public_key = request.form.get("public_key")

    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO peers (name, public_key) VALUES (%s, %s) RETURNING id", (name, public_key))
    db.commit()

    log_action("peer_add", f"Added peer {name}")
    return redirect(url_for("main.peers_ui"))

@bp.route("/sync-wg")
def sync_wg():
    if "user" not in session:
        return redirect(url_for("main.login"))
    sync_wg_interface()
    log_action("sync", "WireGuard interface synced")
    return {"status": "ok"}

@bp.route("/peers-ui/<int:peer_id>/edit", methods=["GET"])
def peers_edit_get(peer_id):
    if "user" not in session:
        return redirect(url_for("main.login"))
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name, public_key FROM peers WHERE id=%s", (peer_id,))
    peer = cur.fetchone()
    return render_template("peers_edit.html", peer=peer)

@bp.route("/peers-ui/<int:peer_id>/edit", methods=["POST"])
def peers_edit_post(peer_id):
    if "user" not in session:
        return redirect(url_for("main.login"))
    name = request.form.get("name")
    public_key = request.form.get("public_key")

    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE peers SET name=%s, public_key=%s WHERE id=%s", (name, public_key, peer_id))
    db.commit()

    log_action("peer_edit", f"Edited peer {peer_id}")
    return redirect(url_for("main.peers_ui"))

@bp.route("/peers-ui/<int:peer_id>/config")
def peers_config(peer_id):
    if "user" not in session:
        return redirect(url_for("main.login"))
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT name, private_key, public_key FROM peers WHERE id=%s", (peer_id,))
    peer = cur.fetchone()
    return render_template("peer_config.html", peer=peer)

@bp.route("/peers-ui/<int:peer_id>/download")
def peers_download(peer_id):
    if "user" not in session:
        return redirect(url_for("main.login"))
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT config FROM peers WHERE id=%s", (peer_id,))
    config = cur.fetchone()[0]
    response = make_response(config)
    response.headers["Content-Disposition"] = f"attachment; filename=peer-{peer_id}.conf"
    return response

@bp.route("/peers-ui/<int:peer_id>/qr")
def peers_qr(peer_id):
    if "user" not in session:
        return redirect(url_for("main.login"))
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT config FROM peers WHERE id=%s", (peer_id,))
    config = cur.fetchone()[0]
    qr = generate_qr_base64(config)
    return render_template("peer_qr.html", qr=qr)

@bp.route("/wg-status")
def wg_status():
    if "user" not in session:
        return redirect(url_for("main.login"))
    status = get_wg_status()
    return render_template("wg_status.html", status=status)

@bp.route("/audit-ui")
def audit_ui():
    if "user" not in session:
        return redirect(url_for("main.login"))
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT timestamp, action, details FROM audit ORDER BY timestamp DESC")
    logs = cur.fetchall()
    return render_template("audit.html", logs=logs)

@bp.route("/peers", methods=["GET"])
def peers_get():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name, public_key FROM peers")
    peers = cur.fetchall()
    return {"peers": peers}

@bp.route("/peers", methods=["POST"])
def peers_post():
    data = request.json
    name = data.get("name")
    public_key = data.get("public_key")

    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO peers (name, public_key) VALUES (%s, %s) RETURNING id", (name, public_key))
    db.commit()

    log_action("peer_add_api", f"Added peer {name}")
    return {"status": "ok"}

@bp.route("/peers/<int:peer_id>", methods=["DELETE"])
def peers_delete(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM peers WHERE id=%s", (peer_id,))
    db.commit()

    log_action("peer_delete", f"Deleted peer {peer_id}")
    return {"status": "ok"}

@bp.route("/peers/<int:peer_id>/config")
def peers_config_api(peer_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT config FROM peers WHERE id=%s", (peer_id,))
    config = cur.fetchone()[0]
    return {"config": config}

@bp.route("/audit")
def audit_api():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT timestamp, action, details FROM audit ORDER BY timestamp DESC")
    logs = cur.fetchall()
    return {"audit": logs}
