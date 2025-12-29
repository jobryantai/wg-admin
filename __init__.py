from flask import Flask
from .routes import bp
from .config import Config
from .db import close_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(bp)
    app.teardown_appcontext(close_db)

    return app

