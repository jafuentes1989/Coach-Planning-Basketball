#archivo que tiene el codigo relacionado con las sesiones
from flask import Blueprint, render_template, request, redirect, url_for, g, abort
#importamos Blueprint para crear un blueprint, 
#importamos render_template para renderizar las vistas creadas en HTML
#importamos request para manejar las solicitudes HTTP
#importamos redirect y url_for para redirigir a diferentes rutas
#importamos g para manejar variables globales durante la solicitud

from app.auth import acceso_requerido #importamos el decorador acceso_requerido para proteger las vistas

from .models import Ejercicio, Usuario, Sesion, Seguimiento #importamos el modelo Ejercicio, Usuario, Sesion y Seguimiento desde models.py
from app import db #importamos el objeto db desde __init__.py para interactuar con la base de datos
from datetime import datetime #importamos datetime para manejar fechas
from sqlalchemy import or_, and_

bp=Blueprint('sesiones', __name__, url_prefix='/sesiones') #creamos el blueprint SESIONES

@bp.route('/listado') #ruta principal del blueprint sesiones
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def listado_sesiones(): #funcion para listar las sesiones
    # Redirigimos al listado filtrado de perfil, que ya muestra
    # solo las sesiones del usuario actual y de los seguidos.
    return redirect(url_for('perfil.sesiones'))


@bp.route('/crear_sesion', methods=['GET', 'POST']) #ruta para crear una nueva sesion
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def crear_sesion(): #funcion para crear una nueva sesion
    if request.method == 'POST': #si el metodo de la solicitud es POST
        fecha_raw = request.form['fecha'] #obtenemos la fecha del formulario como string
        titulo= request.form['titulo'] #obtenemos el titulo del formulario
        descripcion = request.form['descripcion'] #obtenemos la descripcion del formulario
        duracion = request.form['duracion'] #obtenemos la duracion del formulario
        tipo_sesion = (request.form.get('tipo_sesion') or '').strip() or None
        confidencial = request.form.get('confidencial') == 'on' #checkbox confidencial

        # IDs de ejercicios introducidos manualmente, separados por comas (max 10)
        ejercicios_ids_raw = (request.form.get('ejercicios_ids') or '').strip()

        # parsear a lista de enteros únicos, manteniendo orden
        ids_parseds = []
        if ejercicios_ids_raw:
            vistos = set()
            for parte in ejercicios_ids_raw.split(','):
                parte = parte.strip()
                if not parte or not parte.isdigit():
                    continue
                valor = int(parte)
                if valor not in vistos:
                    vistos.add(valor)
                    ids_parseds.append(valor)

        # limitar a max 10
        ids_parseds = ids_parseds[:10]

        # obtener ids de ejercicios permitidos para este usuario (propios + seguidos no confidenciales)
        ejercicios_ids_final = []
        if ids_parseds:
            seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').all()
            followed_aliases = [rel.seguido_alias for rel in seg_rels]

            allowed_condition = or_(
                Ejercicio.autor == g.usuario.alias,
                and_(
                    Ejercicio.autor.in_(followed_aliases),
                    or_(Ejercicio.confidencial.is_(False), Ejercicio.confidencial.is_(None))
                ),
            )

            ejercicios_permitidos = Ejercicio.query.filter(allowed_condition, Ejercicio.id.in_(ids_parseds)).all()
            ejercicios_ids_final = [str(e.id) for e in ejercicios_permitidos]

        ejercicios_ids_str = ','.join(ejercicios_ids_final) if ejercicios_ids_final else None

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
            duracion=duracion,
            tipo_sesion=tipo_sesion,
            confidencial=confidencial,
            ejercicios_ids=ejercicios_ids_str
        ) 
            

        db.session.add(nueva_sesion) #añadimos la nueva sesion a la sesión de la base de datos
        db.session.commit() #confirmamos los cambios en la base de datos
        return redirect(url_for('sesiones.listado_sesiones')) #redireccionamos al listado de sesiones
    
    return render_template('sesiones/crear_sesion.html') #renderizamos la plantilla crear_sesion.html


@bp.route('/editar_sesion/<int:id>', methods=['GET', 'POST']) #ruta para editar una sesion existente
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def editar_sesion(id): #funcion para editar una sesion
    sesion = Sesion.query.get_or_404(id) #obtenemos la sesion por id, o 404 si no existe

    # solo el autor puede editar su sesion
    if sesion.autor != g.usuario.alias:
        abort(403)
    if request.method == 'POST': #si el metodo de la solicitud es POST
        fecha_raw = request.form['fecha'] #obtenemos la fecha del formulario como string
        titulo = request.form['titulo'] #obtenemos el titulo del formulario
        descripcion = request.form['descripcion'] #obtenemos la descripcion del formulario
        duracion = request.form['duracion'] #obtenemos la duracion del formulario
        tipo_sesion = (request.form.get('tipo_sesion') or '').strip() or None
        confidencial = request.form.get('confidencial') == 'on' #checkbox confidencial

        # IDs de ejercicios introducidos manualmente, separados por comas (max 10)
        ejercicios_ids_raw = (request.form.get('ejercicios_ids') or '').strip()

        # parsear a lista de enteros únicos, manteniendo orden
        ids_parseds = []
        if ejercicios_ids_raw:
            vistos = set()
            for parte in ejercicios_ids_raw.split(','):
                parte = parte.strip()
                if not parte or not parte.isdigit():
                    continue
                valor = int(parte)
                if valor not in vistos:
                    vistos.add(valor)
                    ids_parseds.append(valor)

        # limitar a max 10
        ids_parseds = ids_parseds[:10]

        # obtener ids de ejercicios permitidos para este usuario (propios + seguidos no confidenciales)
        ejercicios_ids_final = []
        if ids_parseds:
            seg_rels = Seguimiento.query.filter_by(seguidor_alias=g.usuario.alias, estado='aceptado').all()
            followed_aliases = [rel.seguido_alias for rel in seg_rels]

            allowed_condition = or_(
                Ejercicio.autor == g.usuario.alias,
                and_(
                    Ejercicio.autor.in_(followed_aliases),
                    or_(Ejercicio.confidencial.is_(False), Ejercicio.confidencial.is_(None))
                ),
            )

            ejercicios_permitidos = Ejercicio.query.filter(allowed_condition, Ejercicio.id.in_(ids_parseds)).all()
            ejercicios_ids_final = [str(e.id) for e in ejercicios_permitidos]

        ejercicios_ids_str = ','.join(ejercicios_ids_final) if ejercicios_ids_final else None

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
        sesion.tipo_sesion = tipo_sesion
        sesion.confidencial = confidencial
        sesion.ejercicios_ids = ejercicios_ids_str

        db.session.commit() #confirmamos los cambios en la base de datos
        return redirect(url_for('sesiones.listado_sesiones')) #redireccionamos al listado de sesiones
    
    return render_template('sesiones/editar_sesion.html', sesion=sesion) #renderizamos la plantilla editar_sesion.html con la sesion


@bp.route('/eliminar_sesion/<int:id>') #ruta para eliminar una sesion
@acceso_requerido #protegemos la vista con el decorador acceso_requerido
def eliminar_sesion(id): #funcion para eliminar una sesion
    sesion = Sesion.query.get_or_404(id) #obtenemos la sesion por id, o 404 si no existe

    # solo el autor puede eliminar su sesion
    if sesion.autor != g.usuario.alias:
        abort(403)
    db.session.delete(sesion) #eliminamos la sesion de la sesión de la base de datos
    db.session.commit() #confirmamos los cambios en la base de datos
    return redirect(url_for('sesiones.listado_sesiones')) #redireccionamos al listado de sesiones