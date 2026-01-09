from app import db
from app.models import Usuario, Seguimiento


def crear_usuario(alias):
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


def test_enviar_solicitud_seguimiento(client, app_context):
    """El usuario A envía solicitud a B y queda en estado pendiente."""
    usuario_a = crear_usuario("userA")
    usuario_b = crear_usuario("userB")
    db.session.add_all([usuario_a, usuario_b])
    db.session.commit()

    hacer_login_directo(client, usuario_a.alias)

    resp = client.post(f"/perfil/seguir/{usuario_b.alias}", follow_redirects=False)

    # Redirige de vuelta a la pantalla de seguir_usuarios
    assert resp.status_code == 302
    assert "/perfil/siguiendo/seguir_usuarios" in resp.headers["Location"]

    rel = Seguimiento.query.filter_by(seguidor_alias=usuario_a.alias, seguido_alias=usuario_b.alias).first()
    assert rel is not None
    assert rel.estado == "pendiente"


def test_aceptar_solicitud_cambia_estado_a_aceptado(client, app_context):
    """El usuario B acepta la solicitud enviada por A."""
    usuario_a = crear_usuario("userA2")
    usuario_b = crear_usuario("userB2")
    db.session.add_all([usuario_a, usuario_b])
    db.session.commit()

    # Crear solicitud pendiente A -> B
    rel = Seguimiento(seguidor_alias=usuario_a.alias, seguido_alias=usuario_b.alias, estado="pendiente")
    db.session.add(rel)
    db.session.commit()

    # Login como B (el seguido) y aceptar
    hacer_login_directo(client, usuario_b.alias)

    resp = client.post(f"/perfil/solicitudes/aceptar/{usuario_a.alias}", follow_redirects=False)
    assert resp.status_code == 302

    rel_refrescada = Seguimiento.query.get(rel.id)
    assert rel_refrescada.estado == "aceptado"


def test_rechazar_solicitud_elimina_registro(client, app_context):
    """El usuario B rechaza la solicitud de A y se borra la relación."""
    usuario_a = crear_usuario("userA3")
    usuario_b = crear_usuario("userB3")
    db.session.add_all([usuario_a, usuario_b])
    db.session.commit()

    rel = Seguimiento(seguidor_alias=usuario_a.alias, seguido_alias=usuario_b.alias, estado="pendiente")
    db.session.add(rel)
    db.session.commit()

    hacer_login_directo(client, usuario_b.alias)

    resp = client.post(f"/perfil/solicitudes/rechazar/{usuario_a.alias}", follow_redirects=False)
    assert resp.status_code == 302

    rel_refrescada = Seguimiento.query.filter_by(seguidor_alias=usuario_a.alias, seguido_alias=usuario_b.alias).first()
    assert rel_refrescada is None


def test_dejar_de_seguir_elimina_relacion_aceptada(client, app_context):
    """El usuario A deja de seguir a B cuando ya había una relación aceptada."""
    usuario_a = crear_usuario("userA4")
    usuario_b = crear_usuario("userB4")
    db.session.add_all([usuario_a, usuario_b])
    db.session.commit()

    rel = Seguimiento(seguidor_alias=usuario_a.alias, seguido_alias=usuario_b.alias, estado="aceptado")
    db.session.add(rel)
    db.session.commit()

    hacer_login_directo(client, usuario_a.alias)

    resp = client.post(f"/perfil/dejar_de_seguir/{usuario_b.alias}", follow_redirects=False)
    assert resp.status_code == 302

    rel_refrescada = Seguimiento.query.filter_by(seguidor_alias=usuario_a.alias, seguido_alias=usuario_b.alias).first()
    assert rel_refrescada is None


def test_no_puede_seguirse_a_si_mismo(client, app_context):
    usuario = crear_usuario("selfuser")
    db.session.add(usuario)
    db.session.commit()

    hacer_login_directo(client, usuario.alias)

    resp = client.post(f"/perfil/seguir/{usuario.alias}", follow_redirects=False)
    assert resp.status_code == 302

    # No se crea ninguna relacion de seguimiento
    rels = Seguimiento.query.filter_by(seguidor_alias=usuario.alias, seguido_alias=usuario.alias).all()
    assert rels == []


def test_seguir_usuario_con_relacion_pendiente_no_duplica(client, app_context):
    seguidor = crear_usuario("seg_p")
    seguido = crear_usuario("seg_p2")
    db.session.add_all([seguidor, seguido])
    db.session.commit()

    rel = Seguimiento(seguidor_alias=seguidor.alias, seguido_alias=seguido.alias, estado="pendiente")
    db.session.add(rel)
    db.session.commit()

    hacer_login_directo(client, seguidor.alias)

    resp = client.post(f"/perfil/seguir/{seguido.alias}", follow_redirects=False)
    assert resp.status_code == 302

    rels = Seguimiento.query.filter_by(seguidor_alias=seguidor.alias, seguido_alias=seguido.alias).all()
    assert len(rels) == 1


def test_seguir_usuario_con_relacion_aceptada_no_duplica(client, app_context):
    seguidor = crear_usuario("seg_a")
    seguido = crear_usuario("seg_a2")
    db.session.add_all([seguidor, seguido])
    db.session.commit()

    rel = Seguimiento(seguidor_alias=seguidor.alias, seguido_alias=seguido.alias, estado="aceptado")
    db.session.add(rel)
    db.session.commit()

    hacer_login_directo(client, seguidor.alias)

    resp = client.post(f"/perfil/seguir/{seguido.alias}", follow_redirects=False)
    assert resp.status_code == 302

    rels = Seguimiento.query.filter_by(seguidor_alias=seguidor.alias, seguido_alias=seguido.alias).all()
    assert len(rels) == 1


def test_seguir_usuario_con_relacion_rechazada_no_duplica(client, app_context):
    seguidor = crear_usuario("seg_r")
    seguido = crear_usuario("seg_r2")
    db.session.add_all([seguidor, seguido])
    db.session.commit()

    rel = Seguimiento(seguidor_alias=seguidor.alias, seguido_alias=seguido.alias, estado="rechazado")
    db.session.add(rel)
    db.session.commit()

    hacer_login_directo(client, seguidor.alias)

    resp = client.post(f"/perfil/seguir/{seguido.alias}", follow_redirects=False)
    assert resp.status_code == 302

    rels = Seguimiento.query.filter_by(seguidor_alias=seguidor.alias, seguido_alias=seguido.alias).all()
    assert len(rels) == 1
