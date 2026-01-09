from flask import session

from app import db
from app.models import Usuario


def registrar_usuario(client, alias="coach1", password="secret"):
    datos = {
        "alias": alias,
        "nombre": "Nombre",
        "apellido": "Apellido",
        "email": f"{alias}@test.com",
        "password": password,
        "nivel": "1",
        "temporadas": 3,
        "club": "Club Test",
    }
    return client.post("/auth/registro", data=datos, follow_redirects=False)


def test_registro_crea_usuario_y_redirige(client, app_context):
    resp = registrar_usuario(client)

    # Debe redirigir al login
    assert resp.status_code == 302
    assert "/auth/acceso" in resp.headers["Location"]

    # El usuario debe existir en la BBDD
    usuario = Usuario.query.filter_by(alias="coach1").first()
    assert usuario is not None
    assert usuario.email == "coach1@test.com"


def test_registro_alias_duplicado_muestra_mensaje(client, app_context):
    # Crear usuario inicial
    registrar_usuario(client, alias="coach_dup")

    # Intentar registrar con el mismo alias
    resp = registrar_usuario(client, alias="coach_dup")

    # Se mantiene en la página de registro (200) y muestra mensaje
    assert resp.status_code == 200
    assert "El alias ya existe" in resp.get_data(as_text=True)


def test_registro_email_duplicado_muestra_mensaje(client, app_context):
    # Crear usuario inicial con un email concreto
    registrar_usuario(client, alias="coach_mail1")

    # Intentar registrar otro usuario con el mismo email
    datos = {
        "alias": "coach_mail2",
        "nombre": "Nombre",
        "apellido": "Apellido",
        "email": "coach_mail1@test.com",
        "password": "secret",
        "nivel": "1",
        "temporadas": 3,
        "club": "Club Test",
    }
    resp = client.post("/auth/registro", data=datos, follow_redirects=False)

    assert resp.status_code == 200
    # Verificamos parte del mensaje de error de email duplicado
    html = resp.get_data(as_text=True)
    assert "El email ya" in html and "registrado" in html


def test_login_correcto_guarda_sesion_y_redirige(client, app_context):
    alias = "coach_login"
    password = "secret"

    # Registrar primero
    registrar_usuario(client, alias=alias, password=password)

    # Hacer login
    resp = client.post(
        "/auth/acceso",
        data={"alias": alias, "password": password},
        follow_redirects=False,
    )

    # Debe redirigir al perfil
    assert resp.status_code == 302
    assert "/perfil/" in resp.headers["Location"]

    # Comprobar que la sesión contiene el alias
    with client.session_transaction() as sess:
        assert sess.get("usuario_alias") == alias


def test_login_alias_incorrecto_muestra_mensaje(client, app_context):
    # No registramos ningún usuario con ese alias
    resp = client.post(
        "/auth/acceso",
        data={"alias": "noexiste", "password": "secret"},
        follow_redirects=False,
    )

    assert resp.status_code == 200
    assert "Alias incorrecto" in resp.get_data(as_text=True)


def test_login_password_incorrecta_muestra_mensaje(client, app_context):
    alias = "coach_pass"
    registrar_usuario(client, alias=alias, password="correcta")

    resp = client.post(
        "/auth/acceso",
        data={"alias": alias, "password": "incorrecta"},
        follow_redirects=False,
    )

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # Mensaje contiene "Contraseña incorrecta. Por favor, intenta de nuevo."
    assert "incorrecta" in html and "Por favor" in html


def test_ruta_protegida_redirige_sin_login(client):
    # Sin usuario en sesión, acceder a /perfil/ debe redirigir a /auth/acceso
    resp = client.get("/perfil/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/auth/acceso" in resp.headers["Location"]


def test_cerrar_sesion_limpia_sesion_y_redirige(client, app_context):
    # Primero registrar y hacer login
    alias = "coach_logout"
    registrar_usuario(client, alias=alias, password="secret")
    client.post("/auth/acceso", data={"alias": alias, "password": "secret"})

    # Aseguramos que la sesión está poblada
    with client.session_transaction() as sess:
        assert sess.get("usuario_alias") == alias

    # Llamar a /auth/cerrar_sesion
    resp = client.get("/auth/cerrar_sesion", follow_redirects=False)
    assert resp.status_code == 302
    assert "/" == resp.headers["Location"] or resp.headers["Location"].endswith("/")

    # Comprobar que la sesión queda limpia
    with client.session_transaction() as sess:
        assert "usuario_alias" not in sess
