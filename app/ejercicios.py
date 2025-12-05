#archivo que tiene el codigo relacionado con los ejercicios
from flask import Blueprint, render_template, request, redirect, url_for, g
#importamos Blueprint para crear un blueprint, 
#importamos render_template para renderizar las vistas creadas en HTML
#importamos request para manejar las solicitudes HTTP
#importamos redirect y url_for para redirigir a diferentes rutas
#importamos g para manejar variables globales durante la solicitud

from app.auth import acceso_requerido #importamos el decorador acceso_requerido para proteger las vistas

from .models import Ejercicio, Usuario #importamos el modelo Ejercicio y Usuario desde models.py
from app import db #importamos el objeto db desde __init__.py para interactuar con la base de datos

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
        imagen = request.form['imagen'] #obtenemos la imagen del formulario
        descripcion = request.form['descripcion'] #obtenemos la descripcion del formulario
        numero_jugadores = request.form['jugadores'] #obtenemos el numero de jugadores del formulario
        duracion = request.form['duracion'] #obtenemos la duracion del formulario

        nuevo_ejercicio = Ejercicio( #creamos un nuevo objeto Ejercicio
            autor=g.usuario.alias,
            titulo=titulo,
            imagen_url=imagen,
            descripcion=descripcion,
            jugadores=numero_jugadores,
            duracion=duracion
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

    if request.method == 'POST': #si el metodo de la solicitud es POST
        ejercicio.titulo = request.form['titulo'] #actualizamos el titulo del ejercicio
        ejercicio.imagen_url = request.form['imagen'] #actualizamos la imagen del ejercicio
        ejercicio.descripcion = request.form['descripcion'] #actualizamos la descripcion del ejercicio
        ejercicio.jugadores = request.form['jugadores'] #actualizamos el numero de jugadores del ejercicio
        ejercicio.duracion = request.form['duracion'] #actualizamos la duracion del ejercicio

        db.session.commit() #confirmamos los cambios en la base de datos
        return redirect(url_for('perfil.ejercicios')) #redireccionamos al listado de ejercicios

    return render_template('ejercicios/editar_ejercicio.html', ejercicio=ejercicio) #renderizamos la plantilla editar_ejercicio.html y pasamos el ejercicio como contexto


@bp.route('/eliminar_ejercicio/<int:id>') #ruta para eliminar un ejercicio por su id
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def eliminar_ejercicio(id): #funcion para eliminar un ejercicio
    ejercicio=obtener_ejercicio(id) #obtenemos el ejercicio por su id

    db.session.delete(ejercicio) #eliminamos el ejercicio de la sesión de la base de datos
    db.session.commit() #confirmamos los cambios en la base de datos
    return redirect(url_for('perfil.ejercicios')) #redireccionamos al listado de ejercicios
