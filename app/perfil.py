#archivo que contiene las vistas de la APP
from flask import Blueprint, render_template, g, request, flash, redirect, url_for, jsonify
#importamos Blueprint para crear vistas modulares
#importamos render_template para renderizar las vistas creadas en HTML

from app.auth import acceso_requerido
from .models import Ejercicio, Sesion, Planning, Usuario, Seguimiento
from app import db
import os
from werkzeug.utils import secure_filename
#importamos el decorador acceso_requerido desde auth.py

bp=Blueprint('perfil',__name__, url_prefix='/perfil') #creamos bp como objeto Blueprint

@bp.route('/') #ruta para perfil
@acceso_requerido #decorador para requerir acceso
def perfil(): #funcion de listado
    num_ejercicios = Ejercicio.query.filter_by(autor=g.usuario.alias).count()
    num_sesiones = Sesion.query.filter_by(autor=g.usuario.alias).count()
    num_planning = Planning.query.filter_by(autor=g.usuario.alias).count()
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

    num_ejercicios = Ejercicio.query.filter_by(autor=alias).count()
    num_sesiones = Sesion.query.filter_by(autor=alias).count()
    num_planning = Planning.query.filter_by(autor=alias).count()
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
        usuario.nivel = request.form.get('nivel') or usuario.nivel
        usuario.temporadas = request.form.get('temporadas') or usuario.temporadas
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
    # obtener ejercicios del autor logueado y pasarlos a la plantilla
    ejercicios = Ejercicio.query.filter_by(autor=g.usuario.alias).all()
    return render_template('perfil/ejercicios.html', ejercicios=ejercicios)

@bp.route('/sesiones') #ruta para listado sesiones
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def sesiones(): #funcion de listado sesiones
    sesiones = Sesion.query.filter_by(autor=g.usuario.alias).all()
    return render_template('perfil/sesiones.html', sesiones=sesiones) #return de la funcion

@bp.route('/planning') #ruta para configurar planning
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def planning(): #funcion de planning
    planning = Planning.query.filter_by(autor=g.usuario.alias).all()
    return render_template('perfil/planning.html', planning=planning) #return de la funcion

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

@bp.route('/seguidores/seguir_usuarios') #ruta para listar todos los usuarios para seguir
@acceso_requerido
def seguir_usuarios():
    # todos los usuarios excepto el propio
    usuarios = Usuario.query.filter(Usuario.alias != g.usuario.alias).all()

    # obtener el estado de seguimiento del usuario actual respecto a cada usuario listado
    seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias).all()
    estados_seguidos = {rel.seguido_alias: rel.estado for rel in seg_rels}

    return render_template('seguidores/seguir_usuarios.html', usuarios=usuarios, estados_seguidos=estados_seguidos)


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