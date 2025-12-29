from .db import get_db
from flask import request

def log_action(user_id, action, details=None):
    db = get_db()
    cur = db.cursor()
    ip = request.remote_addr

    cur.execute(
        """
        INSERT INTO audit_log (user_id, action, details, ip_address)
        VALUES (%s, %s, %s, %s);
        """,
        (user_id, action, details, ip)
    )
    db.commit()
