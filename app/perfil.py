#archivo que contiene las vistas de la APP
from flask import Blueprint, render_template, g, request, flash, redirect, url_for, jsonify
#importamos Blueprint para crear vistas modulares
#importamos render_template para renderizar las vistas creadas en HTML

from app.auth import acceso_requerido
from .models import Ejercicio, Sesion, Planning, Usuario
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
    return render_template('perfil/perfil.html', usuario=g.usuario, num_ejercicios=num_ejercicios, num_sesiones=num_sesiones, num_planning=num_planning) #return de la funcion

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
def seguidores(): #funcion de seguidos
    return render_template('perfil/seguidores.html') #return de la funcion

@bp.route('/siguiendo') #ruta para listados de usuarios a los que siguen
def siguiendo(): #funcion de siguiendo
    return render_template('perfil/siguiendo.html') #return de la funcion

@bp.route('/solicitudes') #ruta para listados de solicitudes de seguimiento
def solicitudes(): #funcion de solicitudes
    return render_template('perfil/solicitudes.html') #return de la funcion

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