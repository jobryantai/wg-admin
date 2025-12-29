import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql://wguser:devpassword@localhost/wgadmin_dev"
    )

