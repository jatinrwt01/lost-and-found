import os
from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    # Register teardown handler if database package is initialized by Dev 1
    try:
        from database.db import close_db
        app.teardown_appcontext(close_db)
    except (ImportError, AttributeError):
        pass

    # Register Developer 2 Blueprints
    from routes.auth_bp import auth_bp
    from routes.items_bp import items_bp
    from routes.admin_bp import admin_bp
    from routes.campus_bp import campus_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(campus_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", True))
