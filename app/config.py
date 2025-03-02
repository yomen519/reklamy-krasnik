import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Podstawowa konfiguracja aplikacji."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bardzo-tajny-klucz-zmienic-w-produkcji'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, '..', 'instance',
                                                                                            'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}

    # Konfiguracja uploadów
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    THUMBNAIL_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')
    ORIGINAL_FOLDER = os.path.join(UPLOAD_FOLDER, 'original')
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Utwórz katalogi, jeśli nie istnieją
    for folder in [UPLOAD_FOLDER, THUMBNAIL_FOLDER, ORIGINAL_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    # Konfiguracja aplikacji
    APP_NAME = "Reklamy Kraśnik"

    # Konfiguracja mapy
    DEFAULT_MAP_CENTER = [50.928, 22.227]  # Kraśnik
    DEFAULT_MAP_ZOOM = 13