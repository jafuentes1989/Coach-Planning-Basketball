#archivo que contiene las vistas de la APP
from flask import Blueprint, render_template, g, g
#importamos Blueprint para crear vistas modulares
#importamos render_template para renderizar las vistas creadas en HTML

from app.auth import acceso_requerido
from .models import Ejercicio, Sesion
#importamos el decorador acceso_requerido desde auth.py

bp=Blueprint('perfil',__name__, url_prefix='/perfil') #creamos bp como objeto Blueprint

@bp.route('/') #ruta para perfil
@acceso_requerido #decorador para requerir acceso
def perfil(): #funcion de listado
    return render_template('perfil/perfil.html') #return de la funcion

@bp.route('/configPerfil') #ruta para configurar perfil de usuario
def config(): #funcion de config
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
def planning(): #funcion de planning
    return render_template('perfil/planning.html') #return de la funcion

@bp.route('/seguidores') #ruta para listados de usuarios que te siguen
def seguidores(): #funcion de seguidos
    return render_template('perfil/seguidores.html') #return de la funcion

@bp.route('/siguiendo') #ruta para listados de usuarios a los que siguen
def siguiendo(): #funcion de siguiendo
    return render_template('perfil/siguiendo.html') #return de la funcion

@bp.route('/solicitudes') #ruta para ver solicitudes
def solicitudes(): #funcion de solicitudes
    return render_template('perfil/solicitudes.html') #return de la funcion