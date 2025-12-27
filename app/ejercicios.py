"""Vistas relacionadas con los ejercicios."""

import os

#archivo que tiene el codigo relacionado con los ejercicios
from flask import Blueprint, render_template, request, redirect, url_for, g, current_app, abort
#importamos Blueprint para crear un blueprint, 
#importamos render_template para renderizar las vistas creadas en HTML
#importamos request para manejar las solicitudes HTTP
#importamos redirect y url_for para redirigir a diferentes rutas
#importamos g para manejar variables globales durante la solicitud

from app.auth import acceso_requerido #importamos el decorador acceso_requerido para proteger las vistas

from .models import Ejercicio, Usuario #importamos el modelo Ejercicio y Usuario desde models.py
from app import db #importamos el objeto db desde __init__.py para interactuar con la base de datos
from werkzeug.utils import secure_filename

bp=Blueprint('ejercicios', __name__, url_prefix='/ejercicios') #creamos el blueprint EJERCICIOS

@bp.route('/listado') #ruta principal del blueprint ejercicios
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def listado_ejercicios(): #funcion para listar los ejercicios
    #ejercicios=Ejercicio.query.filter_by(visibilidad=True).all() #consultamos todos los ejercicios visibles en la base de datos
    ejercicios=Ejercicio.query.all() #consultamos todos los ejercicios en la base de datos
    return render_template('perfil/ejercicios.html', ejercicios=ejercicios) #renderizamos la plantilla ejercicios.html y pasamos los ejercicios como contexto

@bp.route('/crear_ejercicio', methods=['GET', 'POST']) #ruta para crear un nuevo ejercicio
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def crear_ejercicio(): #funcion para crear un nuevo ejercicio
    if request.method == 'POST': #si el metodo de la solicitud es POST
        titulo= request.form['titulo'] #obtenemos el titulo del formulario
        fundamento_trabajado = request.form['fundamento_trabajado'] #obtenemos el fundamento trabajado del formulario
        #hasta 3 imágenes
        imagenes_guardadas = []
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)

        for campo in ['imagen1', 'imagen2', 'imagen3']:
            archivo = request.files.get(campo)
            if archivo and archivo.filename:
                filename = secure_filename(archivo.filename)
                ruta_fichero = os.path.join(upload_folder, filename)
                archivo.save(ruta_fichero)
                imagenes_guardadas.append(f"uploads/{filename}")

        descripcion = request.form['descripcion'] #obtenemos la descripcion del formulario
        numero_jugadores = request.form['jugadores'] #obtenemos el numero de jugadores del formulario
        duracion = request.form['duracion'] #obtenemos la duracion del formulario
        confidencial = request.form.get('confidencial') == 'on' #checkbox confidencial

        #asignar rutas a hasta 3 columnas
        imagen_1 = imagenes_guardadas[0] if len(imagenes_guardadas) > 0 else ""
        imagen_2 = imagenes_guardadas[1] if len(imagenes_guardadas) > 1 else None
        imagen_3 = imagenes_guardadas[2] if len(imagenes_guardadas) > 2 else None

        nuevo_ejercicio = Ejercicio( #creamos un nuevo objeto Ejercicio
            autor=g.usuario.alias,
            titulo=titulo,
            fundamento_trabajado=fundamento_trabajado,
            imagen_url=imagen_1,
            descripcion=descripcion,
            jugadores=numero_jugadores,
            duracion=duracion,
            confidencial=confidencial,
            imagen_url_2=imagen_2,
            imagen_url_3=imagen_3
        ) 
            

        db.session.add(nuevo_ejercicio) #añadimos el nuevo ejercicio a la sesión de la base de datos
        db.session.commit() #confirmamos los cambios en la base de datos
        return redirect(url_for('ejercicios.listado_ejercicios')) #redireccionamos al listado de ejercicios
    
    return render_template('ejercicios/crear_ejercicio.html') #renderizamos la plantilla crear_ejercicio.html


def obtener_ejercicio(id): #funcion para obtener un ejercicio por su id
    ejercicio = Ejercicio.query.get_or_404(id) #consultamos el ejercicio en la base de datos por su id
    return ejercicio #devolvemos el ejercicio


@bp.route('/editar_ejercicio/<int:id>', methods=['GET', 'POST']) #ruta para editar un ejercicio por su id
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def editar_ejercicio(id): #funcion para editar un ejercicio
    ejercicio=obtener_ejercicio(id) #obtenemos el ejercicio por su id

    # solo el autor puede editar su ejercicio
    if ejercicio.autor != g.usuario.alias:
        abort(403)

    if request.method == 'POST': #si el metodo de la solicitud es POST
        ejercicio.titulo = request.form['titulo'] #actualizamos el titulo del ejercicio
        ejercicio.fundamento_trabajado = request.form['fundamento_trabajado'] #actualizamos el fundamento trabajado del ejercicio
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)

        #si se sube una nueva imagen en cada campo, sustituye la existente
        archivos = {
            'imagen1': 'imagen_url',
            'imagen2': 'imagen_url_2',
            'imagen3': 'imagen_url_3',
        }

        for campo, atributo in archivos.items():
            archivo = request.files.get(campo)
            if archivo and archivo.filename:
                filename = secure_filename(archivo.filename)
                ruta_fichero = os.path.join(upload_folder, filename)
                archivo.save(ruta_fichero)
                setattr(ejercicio, atributo, f"uploads/{filename}")
        ejercicio.descripcion = request.form['descripcion'] #actualizamos la descripcion del ejercicio
        ejercicio.jugadores = request.form['jugadores'] #actualizamos el numero de jugadores del ejercicio
        ejercicio.duracion = request.form['duracion'] #actualizamos la duracion del ejercicio
        ejercicio.confidencial = request.form.get('confidencial') == 'on' #actualizamos confidencial

        db.session.commit() #confirmamos los cambios en la base de datos
        return redirect(url_for('perfil.ejercicios')) #redireccionamos al listado de ejercicios

    return render_template('ejercicios/editar_ejercicio.html', ejercicio=ejercicio) #renderizamos la plantilla editar_ejercicio.html y pasamos el ejercicio como contexto


@bp.route('/eliminar_ejercicio/<int:id>') #ruta para eliminar un ejercicio por su id
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def eliminar_ejercicio(id): #funcion para eliminar un ejercicio
    ejercicio=obtener_ejercicio(id) #obtenemos el ejercicio por su id

    # solo el autor puede eliminar su ejercicio
    if ejercicio.autor != g.usuario.alias:
        abort(403)

    db.session.delete(ejercicio) #eliminamos el ejercicio de la sesión de la base de datos
    db.session.commit() #confirmamos los cambios en la base de datos
    return redirect(url_for('perfil.ejercicios')) #redireccionamos al listado de ejercicios
