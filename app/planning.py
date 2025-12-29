#archivo que tiene el codigo relacionado con las planificaciones de sesiones
from flask import Blueprint, render_template, request, redirect, url_for, g
#importamos Blueprint para crear un blueprint, 
#importamos render_template para renderizar las vistas creadas en HTML
#importamos request para manejar las solicitudes HTTP
#importamos redirect y url_for para redirigir a diferentes rutas
#importamos g para manejar variables globales durante la solicitud

from app.auth import acceso_requerido #importamos el decorador acceso_requerido para proteger las vistas

from .models import Ejercicio, Usuario, Sesion, Planning, Seguimiento #importamos el modelo Ejercicio, Usuario, Sesion, Planning y Seguimiento desde models.py
from app import db #importamos el objeto db desde __init__.py para interactuar con la base de datos
from datetime import datetime #importamos datetime para manejar fechas
from sqlalchemy import or_, and_

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
        confidencial = request.form.get('confidencial') == 'on' #checkbox confidencial

        # IDs de sesiones introducidos manualmente, separados por comas (max 10)
        sesiones_ids_raw = (request.form.get('sesiones_ids') or '').strip()

        # parsear a lista de enteros únicos, manteniendo orden
        ids_parseds = []
        if sesiones_ids_raw:
            vistos = set()
            for parte in sesiones_ids_raw.split(','):
                parte = parte.strip()
                if not parte or not parte.isdigit():
                    continue
                valor = int(parte)
                if valor not in vistos:
                    vistos.add(valor)
                    ids_parseds.append(valor)

        # limitar a max 10
        ids_parseds = ids_parseds[:10]

        # obtener ids de sesiones permitidas para este usuario (propias + seguidos no confidenciales)
        sesiones_ids_final = []
        sesiones_permitidas = []
        if ids_parseds:
            seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').all()
            followed_aliases = [rel.seguido_alias for rel in seg_rels]

            allowed_condition = or_(
                Sesion.autor == g.usuario.alias,
                and_(
                    Sesion.autor.in_(followed_aliases),
                    or_(Sesion.confidencial.is_(False), Sesion.confidencial.is_(None))
                ),
            )
            sesiones_permitidas = Sesion.query.filter(allowed_condition, Sesion.id.in_(ids_parseds)).all()
            sesiones_ids_final = [str(s.id) for s in sesiones_permitidas]

        sesiones_ids_str = ','.join(sesiones_ids_final) if sesiones_ids_final else None

        # calcular num_sesiones como el número de sesiones permitidas
        num_sesiones = len(sesiones_permitidas) if sesiones_permitidas else 0

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
            num_sesiones=num_sesiones,
            confidencial=confidencial,
            sesiones_ids=sesiones_ids_str
        ) 
            

        db.session.add(nueva_planning) #añadimos la nueva planning a la sesión de la base de datos
        db.session.commit() #confirmamos los cambios en la base de datos
        # tras crear, volvemos al listado filtrado de plannings del perfil
        return redirect(url_for('perfil.planning'))

    return render_template('plannings/crear_planning.html') #renderizamos la plantilla crear_planning.html


@bp.route('/editar_planning/<int:id>', methods=['GET', 'POST']) #ruta para editar una planning existente
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def editar_planning(id): #funcion para editar una planning
    planning = Planning.query.get_or_404(id) #obtenemos la planning por id, o 404 si no existe
    if request.method == 'POST': #si el metodo de la solicitud es POST
        fecha_raw = request.form['fecha'] #obtenemos la fecha del formulario como string
        titulo = request.form['titulo'] #obtenemos el titulo del formulario
        descripcion = request.form['descripcion'] #obtenemos la descripcion del formulario
        confidencial = request.form.get('confidencial') == 'on' #checkbox confidencial

        # IDs de sesiones introducidos manualmente, separados por comas (max 10)
        sesiones_ids_raw = (request.form.get('sesiones_ids') or '').strip()

        # parsear a lista de enteros únicos, manteniendo orden
        ids_parseds = []
        if sesiones_ids_raw:
            vistos = set()
            for parte in sesiones_ids_raw.split(','):
                parte = parte.strip()
                if not parte or not parte.isdigit():
                    continue
                valor = int(parte)
                if valor not in vistos:
                    vistos.add(valor)
                    ids_parseds.append(valor)

        # limitar a max 10
        ids_parseds = ids_parseds[:10]

        # obtener ids de sesiones permitidas para este usuario (propias + seguidos no confidenciales)
        sesiones_ids_final = []
        sesiones_permitidas = []
        if ids_parseds:
            seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').all()
            followed_aliases = [rel.seguido_alias for rel in seg_rels]

            allowed_condition = or_(
                Sesion.autor == g.usuario.alias,
                and_(
                    Sesion.autor.in_(followed_aliases),
                    or_(Sesion.confidencial.is_(False), Sesion.confidencial.is_(None))
                ),
            )
            sesiones_permitidas = Sesion.query.filter(allowed_condition, Sesion.id.in_(ids_parseds)).all()
            sesiones_ids_final = [str(s.id) for s in sesiones_permitidas]

        sesiones_ids_str = ','.join(sesiones_ids_final) if sesiones_ids_final else None

        # calcular num_sesiones como el número de sesiones permitidas
        num_sesiones = len(sesiones_permitidas) if sesiones_permitidas else 0

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
        planning.confidencial = confidencial
        planning.sesiones_ids = sesiones_ids_str

        db.session.commit() #confirmamos los cambios en la base de datos
        # tras editar, volvemos al listado filtrado de plannings del perfil
        return redirect(url_for('perfil.planning'))

    return render_template('plannings/editar_planning.html', planning=planning) #renderizamos la plantilla editar_planning.html con la planning


@bp.route('/eliminar_planning/<int:id>') #ruta para eliminar una planning
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def eliminar_planning(id): #funcion para eliminar una planning
    planning = Planning.query.get_or_404(id) #obtenemos la planning por id, o 404 si no existe
    db.session.delete(planning) #eliminamos la planning de la sesión de la base de datos
    db.session.commit() #confirmamos los cambios en la base de datos
    # tras eliminar, volvemos al listado filtrado de plannings del perfil
    return redirect(url_for('perfil.planning'))