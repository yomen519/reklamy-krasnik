from app.routes.report_routes import report_bp
from app.routes.notification_routes import notification_bp
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

from app.config import Config
from app.extensions import db, migrate, csrf


def create_app(config_class=Config):
    """Fabryka aplikacji Flask z odpowiednią konfiguracją."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ustawienie maksymalnego rozmiaru wgrywanego pliku na 16MB
    app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30

    # Inicjalizacja rozszerzeń
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Rejestracja blueprintów
    from app.routes.main import main_bp
    from app.routes.location_routes import location_bp
    from app.routes.carrier_routes import carrier_bp
    from app.routes.ad_routes import ad_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(location_bp, url_prefix='/locations')
    app.register_blueprint(carrier_bp, url_prefix='/carriers')
    app.register_blueprint(ad_bp, url_prefix='/ads')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(report_bp, url_prefix='/reports')
    app.register_blueprint(notification_bp, url_prefix='/notifications')

    # Obsługa błędów 404 i 500
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, message="Nie znaleziono strony"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error_code=500, message="Wystąpił błąd serwera"), 500

    return app