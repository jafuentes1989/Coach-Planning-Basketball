from datetime import date

from app import db
from app.models import Usuario, Ejercicio, Sesion, Planning


def crear_usuario(alias="coach_ses"):
    return Usuario(
        alias=alias,
        nombre="Nombre",
        apellido="Apellido",
        email=f"{alias}@test.com",
        password="hashed",
        nivel="1",
        temporadas=1,
        club="Club",
    )


def hacer_login_directo(client, alias):
    with client.session_transaction() as sess:
        sess["usuario_alias"] = alias


def crear_ejercicio(autor, titulo, duracion):
    ej = Ejercicio(
        autor=autor,
        titulo=titulo,
        fundamento_trabajado="Tecnico",
        imagen_url="uploads/test.png",
        descripcion="desc",
        jugadores=5,
        duracion=duracion,
    )
    db.session.add(ej)
    db.session.commit()
    return ej


def test_crear_sesion_suma_duraciones(client, app_context):
    # Usuario y ejercicios
    usuario = crear_usuario()
    db.session.add(usuario)
    db.session.commit()

    ej1 = crear_ejercicio(usuario.alias, "Ej1", 15)
    ej2 = crear_ejercicio(usuario.alias, "Ej2", 25)

    hacer_login_directo(client, usuario.alias)

    datos = {
        "fecha": date.today().strftime("%Y-%m-%d"),
        "titulo": "Sesion test",
        "descripcion": "desc",
        "tipo_sesion": "Tecnica",
        "ejercicios_ids": f"{ej1.id},{ej2.id}",
    }

    resp = client.post("/sesiones/crear_sesion", data=datos, follow_redirects=False)

    assert resp.status_code == 302

    sesion = Sesion.query.filter_by(titulo="Sesion test").first()
    assert sesion is not None
    # 15 + 25 = 40
    assert sesion.duracion == 40
    # ids guardados como lista separada por comas
    assert str(ej1.id) in (sesion.ejercicios_ids or "")
    assert str(ej2.id) in (sesion.ejercicios_ids or "")


def test_crear_planning_calcula_num_sesiones(client, app_context):
    usuario = crear_usuario(alias="coach_plan")
    db.session.add(usuario)
    db.session.commit()

    # Crear 2 sesiones propias
    for i in range(2):
        ses = Sesion(
            autor=usuario.alias,
            fecha=date.today(),
            titulo=f"Ses {i}",
            descripcion="desc",
            duracion=30,
        )
        db.session.add(ses)
    db.session.commit()

    sesiones = Sesion.query.filter_by(autor=usuario.alias).all()
    sesiones_ids = ",".join(str(s.id) for s in sesiones)

    hacer_login_directo(client, usuario.alias)

    datos = {
        "fecha": date.today().strftime("%Y-%m-%d"),
        "titulo": "Planning test",
        "descripcion": "desc",
        "sesiones_ids": sesiones_ids,
    }

    resp = client.post("/planning/crear_planning", data=datos, follow_redirects=False)

    assert resp.status_code == 302

    planning = Planning.query.filter_by(titulo="Planning test").first()
    assert planning is not None
    assert planning.num_sesiones == len(sesiones)


def test_crear_sesion_ignora_ids_invalidos_y_no_permitidos(client, app_context):
    # usuario actual, seguido y no seguido
    actual = crear_usuario(alias="actual_ses")
    seguido = crear_usuario(alias="seg_ses")
    otro = crear_usuario(alias="otro_ses")
    db.session.add_all([actual, seguido, otro])
    db.session.commit()

    # relacion de seguimiento aceptada actual -> seguido
    from app.models import Seguimiento

    rel = Seguimiento(seguidor_alias=actual.alias, seguido_alias=seguido.alias, estado="aceptado")
    db.session.add(rel)
    db.session.commit()

    # ejercicios: propio, seguido publico, seguido confidencial, no seguido
    ej_propio = crear_ejercicio(actual.alias, "Ej propio", 10)
    ej_seg_pub = crear_ejercicio(seguido.alias, "Ej seg pub", 15)
    ej_seg_conf = Ejercicio(
        autor=seguido.alias,
        titulo="Ej seg conf",
        fundamento_trabajado="Tecnico",
        imagen_url="uploads/x.png",
        descripcion="desc",
        jugadores=5,
        duracion=20,
        confidencial=True,
    )
    ej_otro = crear_ejercicio(otro.alias, "Ej otro", 30)
    db.session.add(ej_seg_conf)
    db.session.commit()

    hacer_login_directo(client, actual.alias)

    ids_mixtos = f"{ej_propio.id},{ej_seg_pub.id},{ej_seg_conf.id},{ej_otro.id},9999"

    datos = {
        "fecha": date.today().strftime("%Y-%m-%d"),
        "titulo": "Sesion filtrada",
        "descripcion": "desc",
        "tipo_sesion": "Tecnica",
        "ejercicios_ids": ids_mixtos,
    }

    resp = client.post("/sesiones/crear_sesion", data=datos, follow_redirects=False)
    assert resp.status_code == 302

    sesion = Sesion.query.filter_by(titulo="Sesion filtrada").first()
    assert sesion is not None
    # Solo deben incluirse el propio y el del seguido no confidencial
    assert str(ej_propio.id) in (sesion.ejercicios_ids or "")
    assert str(ej_seg_pub.id) in (sesion.ejercicios_ids or "")
    assert (sesion.ejercicios_ids or "").count(",") <= 1


def test_crear_sesion_fecha_invalida_devuelve_400(client, app_context):
    usuario = crear_usuario(alias="coach_bad_date")
    db.session.add(usuario)
    db.session.commit()

    hacer_login_directo(client, usuario.alias)

    datos = {
        "fecha": "2024-99-99",  # fecha invalida
        "titulo": "Sesion mala",
        "descripcion": "desc",
        "tipo_sesion": "Tecnica",
    }

    resp = client.post("/sesiones/crear_sesion", data=datos, follow_redirects=False)
    assert resp.status_code == 400


def test_crear_planning_limita_a_10_sesiones(client, app_context):
    usuario = crear_usuario(alias="coach_limite")
    db.session.add(usuario)
    db.session.commit()

    # Crear 12 sesiones propias
    sesiones_creadas = []
    for i in range(12):
        ses = Sesion(
            autor=usuario.alias,
            fecha=date.today(),
            titulo=f"Ses L{i}",
            descripcion="desc",
            duracion=30,
        )
        db.session.add(ses)
        sesiones_creadas.append(ses)
    db.session.commit()

    ids = ",".join(str(s.id) for s in sesiones_creadas)

    hacer_login_directo(client, usuario.alias)

    datos = {
        "fecha": date.today().strftime("%Y-%m-%d"),
        "titulo": "Planning limite",
        "descripcion": "desc",
        "sesiones_ids": ids,
    }

    resp = client.post("/planning/crear_planning", data=datos, follow_redirects=False)
    assert resp.status_code == 302

    planning = Planning.query.filter_by(titulo="Planning limite").first()
    assert planning is not None
    # Solo deben contarse hasta 10 sesiones
    assert planning.num_sesiones == 10
