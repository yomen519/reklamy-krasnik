from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Inicjalizacja rozszerzeń
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()