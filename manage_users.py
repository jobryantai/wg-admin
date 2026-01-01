import sys
import getpass

import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

DB_NAME = "wgadmin_dev"
DB_USER = "postgres"  # we'll run this script as the postgres OS user


def get_db():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        cursor_factory=RealDictCursor,
    )
    return conn


def create_user(username, password):
    conn = get_db()
    cur = conn.cursor()
    pw_hash = generate_password_hash(password)
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id;",
        (username, pw_hash),
    )
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return row["id"]


def reset_password(username, password):
    conn = get_db()
    cur = conn.cursor()
    pw_hash = generate_password_hash(password)
    cur.execute(
        "UPDATE users SET password_hash = %s WHERE username = %s RETURNING id;",
        (pw_hash, username),
    )
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return row["id"] if row else None


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("create", "reset"):
        print("Usage:")
        print("  manage_users.py create <username>")
        print("  manage_users.py reset  <username>")
        sys.exit(1)

    action = sys.argv[1]
    username = sys.argv[2]

    password = getpass.getpass(f"Enter password for {username}: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Error: passwords do not match.")
        sys.exit(1)

    if action == "create":
        user_id = create_user(username, password)
        print(f"Created user '{username}' with id={user_id}")
    else:
        user_id = reset_password(username, password)
        if user_id is None:
            print(f"No such user: '{username}'")
            sys.exit(1)
        print(f"Updated password for '{username}' (id={user_id})")


if __name__ == "__main__":
    main()

