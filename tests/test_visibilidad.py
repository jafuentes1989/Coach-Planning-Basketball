from datetime import date

from app import db
from app.models import Usuario, Ejercicio, Sesion, Planning, Seguimiento


def crear_usuario(alias):
    return Usuario(
        alias=alias,
        nombre="Nombre",
        apellido="Apellido",
        email=f"{alias}_vis@test.com",
        password="hashed",
        nivel="1",
        temporadas=1,
        club="Club",
    )


def hacer_login_directo(client, alias):
    with client.session_transaction() as sess:
        sess["usuario_alias"] = alias


def test_visibilidad_ejercicios_confidencial_y_seguidos(client, app_context):
    # usuario actual y dos autores: seguido y no seguido
    actual = crear_usuario("actual_vis1")
    seguido = crear_usuario("seguido_vis1")
    otro = crear_usuario("otro_vis1")
    db.session.add_all([actual, seguido, otro])
    db.session.commit()

    # relacion de seguimiento aceptada entre actual -> seguido
    rel = Seguimiento(seguidor_alias=actual.alias, seguido_alias=seguido.alias, estado="aceptado")
    db.session.add(rel)

    # ejercicios: propio, seguido (pub+conf), otro (pub)
    ej_propio = Ejercicio(
        autor=actual.alias,
        titulo="Ej propio",
        fundamento_trabajado="Tecnico",
        imagen_url="uploads/a.png",
        descripcion="desc",
        jugadores=5,
        duracion=10,
        confidencial=False,
    )
    ej_seguido_pub = Ejercicio(
        autor=seguido.alias,
        titulo="Ej seguido pub",
        fundamento_trabajado="Tecnico",
        imagen_url="uploads/b.png",
        descripcion="desc",
        jugadores=5,
        duracion=10,
        confidencial=False,
    )
    ej_seguido_conf = Ejercicio(
        autor=seguido.alias,
        titulo="Ej seguido conf",
        fundamento_trabajado="Tecnico",
        imagen_url="uploads/c.png",
        descripcion="desc",
        jugadores=5,
        duracion=10,
        confidencial=True,
    )
    ej_otro = Ejercicio(
        autor=otro.alias,
        titulo="Ej otro",
        fundamento_trabajado="Tecnico",
        imagen_url="uploads/d.png",
        descripcion="desc",
        jugadores=5,
        duracion=10,
        confidencial=False,
    )

    db.session.add_all([ej_propio, ej_seguido_pub, ej_seguido_conf, ej_otro])
    db.session.commit()

    hacer_login_directo(client, actual.alias)

    resp = client.get("/perfil/ejercicios")
    html = resp.get_data(as_text=True)

    # Deben aparecer: propio y seguido no confidencial
    assert "Ej propio" in html
    assert "Ej seguido pub" in html
    # No deben aparecer: seguido confidencial ni de usuarios no seguidos
    assert "Ej seguido conf" not in html
    assert "Ej otro" not in html


def test_visibilidad_sesiones_y_planning_confidencial(client, app_context):
    actual = crear_usuario("coach")
    seguido = crear_usuario("seg")
    db.session.add_all([actual, seguido])
    db.session.commit()

    rel = Seguimiento(seguidor_alias=actual.alias, seguido_alias=seguido.alias, estado="aceptado")
    db.session.add(rel)

    # Sesiones del seguido: una publica y otra confidencial
    ses_pub = Sesion(
        autor=seguido.alias,
        fecha=date.today(),
        titulo="Ses pub",
        descripcion="desc",
        duracion=30,
    )
    ses_conf = Sesion(
        autor=seguido.alias,
        fecha=date.today(),
        titulo="Ses conf",
        descripcion="desc",
        duracion=30,
        confidencial=True,
    )
    db.session.add_all([ses_pub, ses_conf])
    db.session.commit()

    # Planning del seguido con ambas sesiones
    planning = Planning(
        autor=seguido.alias,
        fecha=date.today(),
        titulo="Plan seg",
        descripcion="desc",
        num_sesiones=2,
        sesiones_ids=f"{ses_pub.id},{ses_conf.id}",
        confidencial=False,
    )
    db.session.add(planning)
    db.session.commit()

    hacer_login_directo(client, actual.alias)

    # En listado de sesiones de perfil, solo debe verse la sesion publica del seguido
    resp_ses = client.get("/perfil/sesiones")
    html_ses = resp_ses.get_data(as_text=True)
    assert "Ses pub" in html_ses
    assert "Ses conf" not in html_ses

    # En planning del perfil, el planning del seguido es visible pero
    # al expandir sus sesiones solo debería incluir la sesión pública
    resp_pl = client.get("/perfil/planning")
    html_pl = resp_pl.get_data(as_text=True)
    assert "Plan seg" in html_pl
    assert "Ses pub" in html_pl
    assert "Ses conf" not in html_pl
