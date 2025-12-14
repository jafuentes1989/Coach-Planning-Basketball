#archivo que tiene el codigo relacionado con las sesiones
from flask import Blueprint, render_template, request, redirect, url_for, g
#importamos Blueprint para crear un blueprint, 
#importamos render_template para renderizar las vistas creadas en HTML
#importamos request para manejar las solicitudes HTTP
#importamos redirect y url_for para redirigir a diferentes rutas
#importamos g para manejar variables globales durante la solicitud

from app.auth import acceso_requerido #importamos el decorador acceso_requerido para proteger las vistas

from .models import Ejercicio, Usuario, Sesion #importamos el modelo Ejercicio, Usuario y Sesion desde models.py
from app import db #importamos el objeto db desde __init__.py para interactuar con la base de datos
from datetime import datetime #importamos datetime para manejar fechas

bp=Blueprint('sesiones', __name__, url_prefix='/sesiones') #creamos el blueprint SESIONES

@bp.route('/listado') #ruta principal del blueprint sesiones
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def listado_sesiones(): #funcion para listar las sesiones
    #sesiones=Sesion.query.filter_by(visibilidad=True).all() #consultamos todas las sesiones visibles en la base de datos
    sesiones=Sesion.query.all() #consultamos todas las sesiones en la base de datos
    return render_template('perfil/sesiones.html', sesiones=sesiones) #renderizamos la plantilla sesiones.html y pasamos las sesiones como contexto


@bp.route('/crear_sesion', methods=['GET', 'POST']) #ruta para crear una nueva sesion
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def crear_sesion(): #funcion para crear una nueva sesion
    if request.method == 'POST': #si el metodo de la solicitud es POST
        fecha_raw = request.form['fecha'] #obtenemos la fecha del formulario como string
        titulo= request.form['titulo'] #obtenemos el titulo del formulario
        descripcion = request.form['descripcion'] #obtenemos la descripcion del formulario
        duracion = request.form['duracion'] #obtenemos la duracion del formulario

        # convertir fecha string a datetime object
        try:
            fecha = datetime.strptime(fecha_raw, '%Y-%m-%d').date()  # si es date, usar .date()
        except ValueError:
            # manejar error de formato
            return "Formato de fecha inválido", 400

        nueva_sesion = Sesion( #creamos un nuevo objeto Sesion
            autor=g.usuario.alias,
            #idEjercicio=g.ejercicio.id,
            fecha=fecha,
            titulo=titulo,
            descripcion=descripcion,
            duracion=duracion
        ) 
            

        db.session.add(nueva_sesion) #añadimos la nueva sesion a la sesión de la base de datos
        db.session.commit() #confirmamos los cambios en la base de datos
        return redirect(url_for('sesiones.listado_sesiones')) #redireccionamos al listado de sesiones
    
    return render_template('sesiones/crear_sesion.html') #renderizamos la plantilla crear_sesion.html


@bp.route('/editar_sesion/<int:id>', methods=['GET', 'POST']) #ruta para editar una sesion existente
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def editar_sesion(id): #funcion para editar una sesion
    sesion = Sesion.query.get_or_404(id) #obtenemos la sesion por id, o 404 si no existe
    if request.method == 'POST': #si el metodo de la solicitud es POST
        fecha_raw = request.form['fecha'] #obtenemos la fecha del formulario como string
        titulo = request.form['titulo'] #obtenemos el titulo del formulario
        descripcion = request.form['descripcion'] #obtenemos la descripcion del formulario
        duracion = request.form['duracion'] #obtenemos la duracion del formulario

        # convertir fecha string a datetime object
        try:
            fecha = datetime.strptime(fecha_raw, '%Y-%m-%d').date()  # si es date, usar .date()
        except ValueError:
            # manejar error de formato
            return "Formato de fecha inválido", 400

        # actualizamos los campos de la sesion
        sesion.fecha = fecha
        sesion.titulo = titulo
        sesion.descripcion = descripcion
        sesion.duracion = duracion

        db.session.commit() #confirmamos los cambios en la base de datos
        return redirect(url_for('sesiones.listado_sesiones')) #redireccionamos al listado de sesiones
    
    return render_template('sesiones/editar_sesion.html', sesion=sesion) #renderizamos la plantilla editar_sesion.html con la sesion


@bp.route('/eliminar_sesion/<int:id>') #ruta para eliminar una sesion
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def eliminar_sesion(id): #funcion para eliminar una sesion
    sesion = Sesion.query.get_or_404(id) #obtenemos la sesion por id, o 404 si no existe
    db.session.delete(sesion) #eliminamos la sesion de la sesión de la base de datos
    db.session.commit() #confirmamos los cambios en la base de datos
    return redirect(url_for('sesiones.listado_sesiones')) #redireccionamos al listado de sesiones