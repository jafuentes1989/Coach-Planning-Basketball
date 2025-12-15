#archivo que tiene el codigo relacionado con las planificaciones de sesiones
from flask import Blueprint, render_template, request, redirect, url_for, g
#importamos Blueprint para crear un blueprint, 
#importamos render_template para renderizar las vistas creadas en HTML
#importamos request para manejar las solicitudes HTTP
#importamos redirect y url_for para redirigir a diferentes rutas
#importamos g para manejar variables globales durante la solicitud

from app.auth import acceso_requerido #importamos el decorador acceso_requerido para proteger las vistas

from .models import Ejercicio, Usuario, Sesion, Planning #importamos el modelo Ejercicio, Usuario, Sesion y Planning desde models.py
from app import db #importamos el objeto db desde __init__.py para interactuar con la base de datos
from datetime import datetime #importamos datetime para manejar fechas

bp=Blueprint('planning', __name__, url_prefix='/planning') #creamos el blueprint PLANNING

@bp.route('/listado') #ruta principal del blueprint planning
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def listado_planning(): #funcion para listar las plannings
    #sesiones=Sesion.query.filter_by(visibilidad=True).all() #consultamos todas las sesiones visibles en la base de datos
    planning=Planning.query.all() #consultamos todas las planning en la base de datos
    return render_template('perfil/planning.html', planning=planning) #renderizamos la plantilla planning.html y pasamos las plannings como contexto


@bp.route('/crear_planning', methods=['GET', 'POST']) #ruta para crear una nueva planning
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def crear_planning(): #funcion para crear una nueva planning
    if request.method == 'POST': #si el metodo de la solicitud es POST
        fecha_raw = request.form['fecha'] #obtenemos la fecha del formulario como string
        titulo= request.form['titulo'] #obtenemos el titulo del formulario
        descripcion = request.form['descripcion'] #obtenemos la descripcion del formulario
        num_sesiones = request.form['num_sesiones'] #obtenemos el numero de sesiones del formulario

        # convertir fecha string a datetime object
        try:
            fecha = datetime.strptime(fecha_raw, '%Y-%m-%d').date()  # si es date, usar .date()
        except ValueError:
            # manejar error de formato
            return "Formato de fecha inválido", 400

        nueva_planning = Planning( #creamos un nuevo objeto Planning
            autor=g.usuario.alias,
            fecha=fecha,
            titulo=titulo,
            descripcion=descripcion,
            num_sesiones=num_sesiones
        ) 
            

        db.session.add(nueva_planning) #añadimos la nueva planning a la sesión de la base de datos
        db.session.commit() #confirmamos los cambios en la base de datos
        return redirect(url_for('planning.listado_planning')) #redireccionamos al listado de plannings

    return render_template('plannings/crear_planning.html') #renderizamos la plantilla crear_planning.html


@bp.route('/editar_planning/<int:id>', methods=['GET', 'POST']) #ruta para editar una planning existente
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def editar_planning(id): #funcion para editar una planning
    planning = Planning.query.get_or_404(id) #obtenemos la planning por id, o 404 si no existe
    if request.method == 'POST': #si el metodo de la solicitud es POST
        fecha_raw = request.form['fecha'] #obtenemos la fecha del formulario como string
        titulo = request.form['titulo'] #obtenemos el titulo del formulario
        descripcion = request.form['descripcion'] #obtenemos la descripcion del formulario
        num_sesiones = request.form['num_sesiones'] #obtenemos el numero de sesiones del formulario

        # convertir fecha string a datetime object
        try:
            fecha = datetime.strptime(fecha_raw, '%Y-%m-%d').date()  # si es date, usar .date()
        except ValueError:
            # manejar error de formato
            return "Formato de fecha inválido", 400

        # actualizamos los campos de la planning
        planning.fecha = fecha
        planning.titulo = titulo
        planning.descripcion = descripcion
        planning.num_sesiones = num_sesiones

        db.session.commit() #confirmamos los cambios en la base de datos
        return redirect(url_for('planning.listado_planning')) #redireccionamos al listado de plannings

    return render_template('plannings/editar_planning.html', planning=planning) #renderizamos la plantilla editar_planning.html con la planning


@bp.route('/eliminar_planning/<int:id>') #ruta para eliminar una planning
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def eliminar_planning(id): #funcion para eliminar una planning
    planning = Planning.query.get_or_404(id) #obtenemos la planning por id, o 404 si no existe
    db.session.delete(planning) #eliminamos la planning de la sesión de la base de datos
    db.session.commit() #confirmamos los cambios en la base de datos
    return redirect(url_for('planning.listado_planning')) #redireccionamos al listado de plannings