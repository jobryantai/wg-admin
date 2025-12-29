from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db

def create_user(username, password):
    db = get_db()
    cur = db.cursor()
    pw_hash = generate_password_hash(password)
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id;",
        (username, pw_hash)
    )
    db.commit()
    return cur.fetchone()["id"]

def verify_user(username, password):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
    user = cur.fetchone()
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return wrapper
