from flask import Flask
from wg_admin.config import Config

def create_app():
    app = Flask(__name__)

    # Load config properly
    app.config.from_object(Config)

    # Register blueprints
    from wg_admin.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

