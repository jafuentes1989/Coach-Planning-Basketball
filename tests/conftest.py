import os
import sys

import pytest

# Asegurar que la raíz del proyecto está en sys.path para poder importar "app"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app, db


TEST_DB_PATH = os.path.join(BASE_DIR, "test_cpb.db")


@pytest.fixture(scope="session")
def app():
    """Crea una instancia de la app para tests con una BBDD SQLite aislada."""
    # Configuración específica para testing
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test_cpb.db",
        # Carpeta de uploads aislada para no tocar /app/static/uploads
        "UPLOAD_FOLDER": os.path.join(BASE_DIR, "test_uploads"),
    }

    application = create_app(test_config=test_config)

    # Crear tablas para toda la sesión de tests
    with application.app_context():
        db.create_all()

    yield application

    # Teardown al final de todos los tests
    with application.app_context():
        db.drop_all()

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    upload_folder = os.path.join(BASE_DIR, "test_uploads")
    if os.path.isdir(upload_folder):
        # borrar ficheros creados de forma sencilla
        for nombre in os.listdir(upload_folder):
            try:
                os.remove(os.path.join(upload_folder, nombre))
            except OSError:
                pass
        try:
            os.rmdir(upload_folder)
        except OSError:
            pass


@pytest.fixture()
def client(app):
    """Cliente de pruebas de Flask."""
    return app.test_client()


@pytest.fixture()
def app_context(app):
    """Proporciona un contexto de aplicación para operaciones con la BBDD."""
    with app.app_context():
        yield
