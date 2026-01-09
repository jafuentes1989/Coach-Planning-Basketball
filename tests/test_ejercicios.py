from app import db
from app.models import Usuario, Ejercicio


def crear_usuario_basico(alias="coach_ej"):
    """Crea un usuario basico con alias y email derivados del alias."""
    return Usuario(
        alias=alias,
        nombre="Nombre",
        apellido="Apellido",
        email=f"{alias}@test.com",
        password="hashed",  # el valor real no importa aquí
        nivel="1",
        temporadas=1,
        club="Club",
    )


def hacer_login_directo(client, alias):
    """Coloca el alias en la sesión sin pasar por /auth/acceso."""
    with client.session_transaction() as sess:
        sess["usuario_alias"] = alias


def test_crear_ejercicio_crea_registro(client, app_context):
    # Crear usuario en la BBDD
    usuario = crear_usuario_basico(alias="coach_ej_crear")
    db.session.add(usuario)
    db.session.commit()

    hacer_login_directo(client, usuario.alias)

    datos = {
        "titulo": "Ejercicio test",
        "fundamento_trabajado": "Tecnico",
        "descripcion": "Descripcion de prueba",
        "jugadores": 10,
        "duracion": 20,
        # checkbox confidencial desmarcado
    }

    resp = client.post("/ejercicios/crear_ejercicio", data=datos, follow_redirects=False)

    # Debe redirigir al listado de ejercicios del perfil
    assert resp.status_code == 302
    assert "/perfil/ejercicios" in resp.headers["Location"]

    # Comprobar que se ha creado el ejercicio
    ejercicio = Ejercicio.query.filter_by(titulo="Ejercicio test").first()
    assert ejercicio is not None
    assert ejercicio.autor == usuario.alias
    assert ejercicio.duracion == 20


def test_editar_ejercicio_actualiza_campos(client, app_context):
    # Usuario y ejercicio inicial
    usuario = crear_usuario_basico(alias="coach_ej_editar")
    db.session.add(usuario)
    db.session.commit()

    ejercicio = Ejercicio(
        autor=usuario.alias,
        titulo="Titulo inicial",
        fundamento_trabajado="Fisico",
        imagen_url="uploads/x.png",
        descripcion="desc",
        jugadores=5,
        duracion=10,
    )
    db.session.add(ejercicio)
    db.session.commit()

    hacer_login_directo(client, usuario.alias)

    datos = {
        "titulo": "Titulo editado",
        "fundamento_trabajado": "Tecnico",
        "descripcion": "nueva desc",
        "jugadores": 8,
        "duracion": 25,
        "confidencial": "on",
    }

    resp = client.post(
        f"/ejercicios/editar_ejercicio/{ejercicio.id}", data=datos, follow_redirects=False
    )
    assert resp.status_code == 302

    ej_ref = Ejercicio.query.get(ejercicio.id)
    assert ej_ref.titulo == "Titulo editado"
    assert ej_ref.fundamento_trabajado == "Tecnico"
    assert ej_ref.descripcion == "nueva desc"
    assert ej_ref.jugadores == 8
    assert ej_ref.duracion == 25
    assert ej_ref.confidencial is True


def test_editar_ejercicio_solo_autor_puede_modificar(client, app_context):
    autor = crear_usuario_basico(alias="coach_ej_autor1")
    otro = Usuario(
        alias="otro",
        nombre="Nombre",
        apellido="Apellido",
        email="otro@test.com",
        password="hash",
        nivel="1",
        temporadas=1,
        club="Club",
    )
    db.session.add_all([autor, otro])
    db.session.commit()

    ejercicio = Ejercicio(
        autor=autor.alias,
        titulo="Titulo",
        fundamento_trabajado="Fisico",
        imagen_url="uploads/x.png",
        descripcion="desc",
        jugadores=5,
        duracion=10,
    )
    db.session.add(ejercicio)
    db.session.commit()

    hacer_login_directo(client, otro.alias)

    resp = client.post(
        f"/ejercicios/editar_ejercicio/{ejercicio.id}",
        data={"titulo": "hack"},
        follow_redirects=False,
    )

    assert resp.status_code == 403


def test_eliminar_ejercicio_solo_autor_puede_borrar(client, app_context):
    autor = crear_usuario_basico(alias="coach_ej_autor2")
    otro = Usuario(
        alias="otro2",
        nombre="Nombre",
        apellido="Apellido",
        email="otro2@test.com",
        password="hash",
        nivel="1",
        temporadas=1,
        club="Club",
    )
    db.session.add_all([autor, otro])
    db.session.commit()

    ejercicio = Ejercicio(
        autor=autor.alias,
        titulo="Titulo",
        fundamento_trabajado="Fisico",
        imagen_url="uploads/x.png",
        descripcion="desc",
        jugadores=5,
        duracion=10,
    )
    db.session.add(ejercicio)
    db.session.commit()

    # Intento de borrar por usuario no autor
    hacer_login_directo(client, otro.alias)
    resp_forbidden = client.get(f"/ejercicios/eliminar_ejercicio/{ejercicio.id}")
    assert resp_forbidden.status_code == 403

    # Borrado correcto por el autor
    hacer_login_directo(client, autor.alias)
    resp_ok = client.get(f"/ejercicios/eliminar_ejercicio/{ejercicio.id}")
    assert resp_ok.status_code == 302
    assert Ejercicio.query.get(ejercicio.id) is None
