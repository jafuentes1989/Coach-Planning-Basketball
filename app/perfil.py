#archivo que contiene las vistas de la APP
from flask import Blueprint, render_template, g, request, flash, redirect, url_for, jsonify
#importamos Blueprint para crear vistas modulares
#importamos render_template para renderizar las vistas creadas en HTML

from app.auth import acceso_requerido
from .models import Ejercicio, Sesion, Planning, Usuario, Seguimiento
from app import db
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
#importamos el decorador acceso_requerido desde auth.py

bp=Blueprint('perfil',__name__, url_prefix='/perfil') #creamos bp como objeto Blueprint

@bp.route('/') #ruta para perfil
@acceso_requerido #decorador para requerir acceso
def perfil(): #funcion de listado
    # usuarios a los que sigo (relaciones aceptadas)
    seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').all()
    followed_aliases = [rel.seguido_alias for rel in seg_rels]

    # ejercicios: propios + de seguidos no confidenciales (o sin valor)
    ejercicios_allowed = or_(
        Ejercicio.autor == g.usuario.alias,
        and_(
            Ejercicio.autor.in_(followed_aliases),
            or_(Ejercicio.confidencial.is_(False), Ejercicio.confidencial.is_(None))
        ),
    )
    num_ejercicios = Ejercicio.query.filter(ejercicios_allowed).count()

    # sesiones: propias + de seguidos no confidenciales (o sin valor)
    sesiones_allowed = or_(
        Sesion.autor == g.usuario.alias,
        and_(
            Sesion.autor.in_(followed_aliases),
            or_(Sesion.confidencial.is_(False), Sesion.confidencial.is_(None))
        ),
    )
    num_sesiones = Sesion.query.filter(sesiones_allowed).count()

    # planning: propios + de seguidos no confidenciales (o sin valor)
    planning_allowed = or_(
        Planning.autor == g.usuario.alias,
        and_(
            Planning.autor.in_(followed_aliases),
            or_(Planning.confidencial.is_(False), Planning.confidencial.is_(None))
        ),
    )
    num_planning = Planning.query.filter(planning_allowed).count()
    num_seguidores = Seguimiento.query.filter_by(seguido_alias=g.usuario.alias, estado='aceptado').count()
    num_siguiendo = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').count()
    num_solicitudes = Seguimiento.query.filter_by(seguido_alias=g.usuario.alias, estado='pendiente').count()
    return render_template(
        'perfil/perfil.html',
        usuario=g.usuario,
        num_ejercicios=num_ejercicios,
        num_sesiones=num_sesiones,
        num_planning=num_planning,
        num_seguidores=num_seguidores,
        num_siguiendo=num_siguiendo,
        num_solicitudes=num_solicitudes
    ) #return de la funcion

@bp.route('/ver/<alias>') #ruta para ver el perfil de otro usuario
@acceso_requerido
def ver_perfil(alias):
    # si es el propio usuario, reutilizamos la vista principal
    if alias == g.usuario.alias:
        return redirect(url_for('perfil.perfil'))

    usuario = Usuario.query.get_or_404(alias)

    # Ejercicios del usuario visto; si no es el propio, ocultar confidenciales
    ejercicios_q = Ejercicio.query.filter_by(autor=alias)
    if alias != g.usuario.alias:
        ejercicios_q = ejercicios_q.filter(or_(Ejercicio.confidencial.is_(False), Ejercicio.confidencial.is_(None)))
    num_ejercicios = ejercicios_q.count()

    # Sesiones del usuario visto
    sesiones_q = Sesion.query.filter_by(autor=alias)
    if alias != g.usuario.alias:
        sesiones_q = sesiones_q.filter(or_(Sesion.confidencial.is_(False), Sesion.confidencial.is_(None)))
    num_sesiones = sesiones_q.count()

    # Plannings del usuario visto
    planning_q = Planning.query.filter_by(autor=alias)
    if alias != g.usuario.alias:
        planning_q = planning_q.filter(or_(Planning.confidencial.is_(False), Planning.confidencial.is_(None)))
    num_planning = planning_q.count()
    num_seguidores = Seguimiento.query.filter_by(seguido_alias=alias, estado='aceptado').count()
    num_siguiendo = Seguimiento.query.filter_by(seguidor_alias=alias, estado='aceptado').count()
    num_solicitudes = Seguimiento.query.filter_by(seguido_alias=alias, estado='pendiente').count()

    return render_template(
        'perfil/perfil.html',
        usuario=usuario,
        num_ejercicios=num_ejercicios,
        num_sesiones=num_sesiones,
        num_planning=num_planning,
        num_seguidores=num_seguidores,
        num_siguiendo=num_siguiendo,
        num_solicitudes=num_solicitudes
    )

@bp.route('/configPerfil', methods=['GET', 'POST']) #ruta para configurar perfil de usuario
@acceso_requerido
def config(): #funcion de config
    if request.method == 'POST':
        usuario = Usuario.query.get(g.usuario.alias)
        usuario.nombre = request.form.get('nombre') or usuario.nombre
        usuario.apellido = request.form.get('apellido') or usuario.apellido

        # validar nivel (solo 1, 2 o Nacional)
        nivel_form = request.form.get('nivel')
        if nivel_form:
            if nivel_form in ['1', '2', 'Nacional']:
                usuario.nivel = nivel_form
            else:
                flash('Nivel no válido. Solo se permiten 1, 2 o Nacional.')
                return render_template('perfil/configPerfil.html')

        # validar temporadas (entre 1 y 30, sin negativos)
        temporadas_form = request.form.get('temporadas')
        if temporadas_form:
            try:
                temporadas_int = int(temporadas_form)
                if 1 <= temporadas_int <= 30:
                    usuario.temporadas = temporadas_int
                else:
                    flash('Las temporadas deben estar entre 1 y 30.')
                    return render_template('perfil/configPerfil.html')
            except ValueError:
                flash('El valor de temporadas no es válido.')
                return render_template('perfil/configPerfil.html')

        usuario.club = request.form.get('club') or usuario.club
        
        # Manejar subida de imagen
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # Crear directorio si no existe
                upload_folder = os.path.join('app', 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                usuario.profile_image = f'/static/uploads/{filename}'
        
        db.session.commit()
        flash('Perfil actualizado correctamente.')
        return redirect(url_for('perfil.perfil'))
    
    return render_template('perfil/configPerfil.html') #return de la funcion

@bp.route('/ejercicios') #ruta para listado ejercicios
@acceso_requerido #decorador para requerir acceso
def ejercicios(): #funcion de listado ejercicios
    # filtros desde la query string
    autor_f = (request.args.get('autor') or '').strip()
    fundamento_f = (request.args.get('fundamento_trabajado') or '').strip()
    descripcion_f = (request.args.get('descripcion') or '').strip()
    jugadores_f = (request.args.get('jugadores') or '').strip()
    duracion_f = (request.args.get('duracion') or '').strip()

    # obtener usuarios a los que sigo (relaciones aceptadas)
    seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').all()
    followed_aliases = [rel.seguido_alias for rel in seg_rels]

    # condición base: siempre mis ejercicios, y de usuarios seguidos solo los no confidenciales
    allowed_condition = or_(
        Ejercicio.autor == g.usuario.alias,
        and_(
            Ejercicio.autor.in_(followed_aliases),
            or_(Ejercicio.confidencial.is_(False), Ejercicio.confidencial.is_(None))
        ),
    )

    query = Ejercicio.query.filter(allowed_condition)

    # autor contiene lo buscado (puede incluir otros autores dentro del conjunto permitido)
    if autor_f:
        query = query.filter(Ejercicio.autor.ilike(f"%{autor_f}%"))

    # fundamento: valor exacto seleccionado en el select
    if fundamento_f:
        query = query.filter(Ejercicio.fundamento_trabajado == fundamento_f)

    # descripcion: contiene el texto introducido
    if descripcion_f:
        query = query.filter(Ejercicio.descripcion.ilike(f"%{descripcion_f}%"))

    # numero de jugadores: coincidencia exacta si es un número válido
    if jugadores_f:
        try:
            jugadores_int = int(jugadores_f)
            query = query.filter(Ejercicio.jugadores == jugadores_int)
        except ValueError:
            pass

    # duracion: coincidencia exacta si es un número válido
    if duracion_f:
        try:
            duracion_int = int(duracion_f)
            query = query.filter(Ejercicio.duracion == duracion_int)
        except ValueError:
            pass

    ejercicios = query.all()

    return render_template(
        'perfil/ejercicios.html',
        ejercicios=ejercicios,
        autor_filtro=autor_f,
        fundamento_filtro=fundamento_f,
        descripcion_filtro=descripcion_f,
        jugadores_filtro=jugadores_f,
        duracion_filtro=duracion_f,
        mostrar_ver=True
    )

@bp.route('/sesiones') #ruta para listado sesiones
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def sesiones(): #funcion de listado sesiones
    # usuarios a los que sigo
    seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').all()
    followed_aliases = [rel.seguido_alias for rel in seg_rels]

    # siempre mis sesiones; de seguidos solo las no confidenciales
    allowed_condition = or_(
        Sesion.autor == g.usuario.alias,
        and_(
            Sesion.autor.in_(followed_aliases),
            or_(Sesion.confidencial.is_(False), Sesion.confidencial.is_(None))
        ),
    )

    sesiones = Sesion.query.filter(allowed_condition).all()

    # preparar los ejercicios asociados a cada sesión en el orden definido en ejercicios_ids
    sesiones_ids_map = {}
    all_ej_ids = set()
    for sesion in sesiones:
        ids_list = []
        if sesion.ejercicios_ids:
            for parte in sesion.ejercicios_ids.split(','):
                parte = (parte or '').strip()
                if not parte or not parte.isdigit():
                    continue
                valor = int(parte)
                ids_list.append(valor)
                all_ej_ids.add(valor)
        sesiones_ids_map[sesion.id] = ids_list

    ejercicios_por_sesion = {}
    if all_ej_ids:
        ejercicios_objs = Ejercicio.query.filter(Ejercicio.id.in_(all_ej_ids)).all()
        ejercicios_by_id = {e.id: e for e in ejercicios_objs}

        for sesion in sesiones:
            datos_ejercicios = []
            for ej_id in sesiones_ids_map.get(sesion.id, []):
                ej = ejercicios_by_id.get(ej_id)
                if not ej:
                    continue
                datos_ejercicios.append({
                    'id': ej.id,
                    'titulo': ej.titulo,
                    'fundamento': ej.fundamento_trabajado,
                    'jugadores': ej.jugadores,
                    'duracion': ej.duracion,
                    'descripcion': ej.descripcion,
                    'imagen1': url_for('static', filename=ej.imagen_url) if ej.imagen_url else None,
                    'imagen2': url_for('static', filename=ej.imagen_url_2) if ej.imagen_url_2 else None,
                    'imagen3': url_for('static', filename=ej.imagen_url_3) if ej.imagen_url_3 else None,
                })
            ejercicios_por_sesion[sesion.id] = datos_ejercicios

    return render_template('perfil/sesiones.html', sesiones=sesiones, ejercicios_por_sesion=ejercicios_por_sesion, mostrar_ver=True, mostrar_acciones=True) #return de la funcion

@bp.route('/planning') #ruta para configurar planning
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def planning(): #funcion de planning
    # usuarios a los que sigo
    seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').all()
    followed_aliases = [rel.seguido_alias for rel in seg_rels]

    # siempre mis plannings; de seguidos solo los no confidenciales
    allowed_condition = or_(
        Planning.autor == g.usuario.alias,
        and_(
            Planning.autor.in_(followed_aliases),
            or_(Planning.confidencial.is_(False), Planning.confidencial.is_(None))
        ),
    )
    planning = Planning.query.filter(allowed_condition).all()
    return render_template('perfil/planning.html', planning=planning, mostrar_acciones=True) #return de la funcion


@bp.route('/ejercicios/<alias>')
@acceso_requerido
def ejercicios_usuario(alias):
    """Listado de ejercicios de un usuario concreto (para ver desde su perfil)."""
    usuario = Usuario.query.get_or_404(alias)

    query = Ejercicio.query.filter(Ejercicio.autor == alias)
    # si no es el propio usuario, ocultar confidenciales
    if alias != g.usuario.alias:
        query = query.filter(or_(Ejercicio.confidencial.is_(False), Ejercicio.confidencial.is_(None)))

    ejercicios = query.all()

    # reutilizamos la misma plantilla de perfil/ejercicios, sin filtros por otros autores
    return render_template(
        'perfil/ejercicios.html',
        ejercicios=ejercicios,
        autor_filtro=alias,
        fundamento_filtro='',
        descripcion_filtro='',
        jugadores_filtro='',
        duracion_filtro='',
        mostrar_ver=False,
    )


@bp.route('/sesiones/<alias>')
@acceso_requerido
def sesiones_usuario(alias):
    """Listado de sesiones de un usuario concreto (para ver desde su perfil)."""
    Usuario.query.get_or_404(alias)

    query = Sesion.query.filter(Sesion.autor == alias)
    if alias != g.usuario.alias:
        query = query.filter(or_(Sesion.confidencial.is_(False), Sesion.confidencial.is_(None)))

    sesiones = query.all()

    # preparar los ejercicios asociados a cada sesión en el orden definido en ejercicios_ids
    sesiones_ids_map = {}
    all_ej_ids = set()
    for sesion in sesiones:
        ids_list = []
        if sesion.ejercicios_ids:
            for parte in sesion.ejercicios_ids.split(','):
                parte = (parte or '').strip()
                if not parte or not parte.isdigit():
                    continue
                valor = int(parte)
                ids_list.append(valor)
                all_ej_ids.add(valor)
        sesiones_ids_map[sesion.id] = ids_list

    ejercicios_por_sesion = {}
    if all_ej_ids:
        ejercicios_objs = Ejercicio.query.filter(Ejercicio.id.in_(all_ej_ids)).all()
        ejercicios_by_id = {e.id: e for e in ejercicios_objs}

        for sesion in sesiones:
            datos_ejercicios = []
            for ej_id in sesiones_ids_map.get(sesion.id, []):
                ej = ejercicios_by_id.get(ej_id)
                if not ej:
                    continue
                datos_ejercicios.append({
                    'id': ej.id,
                    'titulo': ej.titulo,
                    'fundamento': ej.fundamento_trabajado,
                    'jugadores': ej.jugadores,
                    'duracion': ej.duracion,
                    'descripcion': ej.descripcion,
                    'imagen1': url_for('static', filename=ej.imagen_url) if ej.imagen_url else None,
                    'imagen2': url_for('static', filename=ej.imagen_url_2) if ej.imagen_url_2 else None,
                    'imagen3': url_for('static', filename=ej.imagen_url_3) if ej.imagen_url_3 else None,
                })
            ejercicios_por_sesion[sesion.id] = datos_ejercicios

    return render_template('perfil/sesiones.html', sesiones=sesiones, ejercicios_por_sesion=ejercicios_por_sesion, mostrar_ver=False, mostrar_acciones=(alias == g.usuario.alias))


@bp.route('/planning/<alias>')
@acceso_requerido
def planning_usuario(alias):
    """Listado de plannings de un usuario concreto (para ver desde su perfil)."""
    Usuario.query.get_or_404(alias)

    query = Planning.query.filter(Planning.autor == alias)
    if alias != g.usuario.alias:
        query = query.filter(or_(Planning.confidencial.is_(False), Planning.confidencial.is_(None)))

    planning = query.all()
    return render_template('perfil/planning.html', planning=planning)

@bp.route('/seguidores') #ruta para listados de usuarios que te siguen
@acceso_requerido
def seguidores(): #funcion de seguidos
    # usuarios cuyo seguidor_alias apunta al usuario actual
    seg_rels = Seguimiento.query.filter_by(seguido_alias=g.usuario.alias, estado='aceptado').all()
    aliases = [rel.seguidor_alias for rel in seg_rels]
    seguidores = Usuario.query.filter(Usuario.alias.in_(aliases)).all() if aliases else []
    return render_template('perfil/seguidores.html', seguidores=seguidores) #return de la funcion

@bp.route('/siguiendo') #ruta para listados de usuarios a los que sigue el usuario actual
@acceso_requerido
def siguiendo(): #funcion de siguiendo
    seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').all()
    aliases = [rel.seguido_alias for rel in seg_rels]
    siguiendos = Usuario.query.filter(Usuario.alias.in_(aliases)).all() if aliases else []
    return render_template('perfil/siguiendo.html', siguiendos=siguiendos) #return de la funcion

@bp.route('/siguiendo/seguir_usuarios') #ruta para listar todos los usuarios para seguir
@acceso_requerido
def seguir_usuarios():
    # filtros desde la query string
    alias_f = (request.args.get('alias') or '').strip()
    nombre_f = (request.args.get('nombre') or '').strip()
    apellido_f = (request.args.get('apellido') or '').strip()
    email_f = (request.args.get('email') or '').strip()
    nivel_f = (request.args.get('nivel') or '').strip()
    temporadas_f = (request.args.get('temporadas') or '').strip()

    # base: todos los usuarios excepto el propio
    query = Usuario.query.filter(Usuario.alias != g.usuario.alias)

    # campos de texto: contiene
    if alias_f:
        query = query.filter(Usuario.alias.ilike(f"%{alias_f}%"))
    if nombre_f:
        query = query.filter(Usuario.nombre.ilike(f"%{nombre_f}%"))
    if apellido_f:
        query = query.filter(Usuario.apellido.ilike(f"%{apellido_f}%"))
    if email_f:
        query = query.filter(Usuario.email.ilike(f"%{email_f}%"))
    if club_f := (request.args.get('club') or '').strip():
        query = query.filter(Usuario.club.ilike(f"%{club_f}%"))

    # campos numéricos / exactos
    if nivel_f:
        query = query.filter(Usuario.nivel == nivel_f)
    if temporadas_f:
        try:
            temporadas_int = int(temporadas_f)
            query = query.filter(Usuario.temporadas == temporadas_int)
        except ValueError:
            pass

    usuarios = query.all()

    # obtener el estado de seguimiento del usuario actual respecto a cada usuario listado
    seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias).all()
    estados_seguidos = {rel.seguido_alias: rel.estado for rel in seg_rels}

    return render_template(
        'seguidores/seguir_usuarios.html',
        usuarios=usuarios,
        estados_seguidos=estados_seguidos,
        alias_filtro=alias_f,
        nombre_filtro=nombre_f,
        apellido_filtro=apellido_f,
        email_filtro=email_f,
        nivel_filtro=nivel_f,
        temporadas_filtro=temporadas_f,
        club_filtro=club_f if 'club_f' in locals() else ''
    )


@bp.route('/seguir/<alias>', methods=['POST']) #ruta para seguir a un usuario
@acceso_requerido
def seguir(alias):
    if alias == g.usuario.alias:
        flash('No puedes seguirte a ti mismo.')
        return redirect(url_for('perfil.seguir_usuarios'))

    # comprobar si ya hay alguna relacion
    existente = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, seguido_alias=alias).first()
    if existente:
        if existente.estado == 'pendiente':
            flash('Ya has enviado una solicitud a este usuario.')
        elif existente.estado == 'aceptado':
            flash('Ya sigues a este usuario.')
        else:
            flash('La solicitud anterior fue rechazada.')
        return redirect(url_for('perfil.seguir_usuarios'))

    # crear una nueva solicitud en estado pendiente
    seguimiento = Seguimiento(seguidor_alias=g.usuario.alias, seguido_alias=alias, estado='pendiente')
    db.session.add(seguimiento)
    db.session.commit()
    flash('Solicitud de seguimiento enviada.')
    return redirect(url_for('perfil.seguir_usuarios'))

@bp.route('/solicitudes') #ruta para listados de solicitudes de seguimiento
@acceso_requerido
def solicitudes(): #funcion de solicitudes
    # solicitudes pendientes donde el usuario actual es el seguido
    seg_rels = Seguimiento.query.filter_by(seguido_alias=g.usuario.alias, estado='pendiente').all()
    aliases = [rel.seguidor_alias for rel in seg_rels]
    solicitudes_usuarios = Usuario.query.filter(Usuario.alias.in_(aliases)).all() if aliases else []
    return render_template('perfil/solicitudes.html', solicitudes=solicitudes_usuarios) #return de la funcion

@bp.route('/solicitudes/aceptar/<alias>', methods=['POST'])
@acceso_requerido
def aceptar_solicitud(alias):
    seguimiento = Seguimiento.query.filter_by(seguidor_alias=alias, seguido_alias=g.usuario.alias, estado='pendiente').first()
    if not seguimiento:
        flash('No se ha encontrado la solicitud.')
        return redirect(url_for('perfil.solicitudes'))

    seguimiento.estado = 'aceptado'
    db.session.commit()
    flash('Solicitud aceptada correctamente.')
    return redirect(url_for('perfil.solicitudes'))

@bp.route('/solicitudes/rechazar/<alias>', methods=['POST'])
@acceso_requerido
def rechazar_solicitud(alias):
    seguimiento = Seguimiento.query.filter_by(seguidor_alias=alias, seguido_alias=g.usuario.alias, estado='pendiente').first()
    if not seguimiento:
        flash('No se ha encontrado la solicitud.')
        return redirect(url_for('perfil.solicitudes'))

    db.session.delete(seguimiento)
    db.session.commit()
    flash('Solicitud rechazada correctamente.')
    return redirect(url_for('perfil.solicitudes'))

@bp.route('/dejar_de_seguir/<alias>', methods=['POST'])
@acceso_requerido
def dejar_de_seguir(alias):
    seguimiento = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, seguido_alias=alias, estado='aceptado').first()
    if not seguimiento:
        flash('No se ha encontrado la relación de seguimiento.')
        return redirect(url_for('perfil.seguir_usuarios'))

    db.session.delete(seguimiento)
    db.session.commit()
    flash('Has dejado de seguir a este usuario.')
    return redirect(url_for('perfil.seguir_usuarios'))

@bp.route('/upload_image', methods=['POST'])
@acceso_requerido
def upload_image():
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_folder = os.path.join('app', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            usuario = Usuario.query.get(g.usuario.alias)
            usuario.profile_image = f'/static/uploads/{filename}'
            db.session.commit()
            return jsonify({'success': True, 'image_url': usuario.profile_image})
    return jsonify({'success': False})