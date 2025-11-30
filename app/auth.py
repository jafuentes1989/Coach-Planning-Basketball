#archivo que trabaja la autenticación de usuarios
from flask import Blueprint, render_template 
#importamos Blueprint para crear vistas modulares
#importamos render_template para renderizar las vistas creadas en HTML

bp=Blueprint('auth',__name__, url_prefix='/auth') #creamos bp como objeto Blueprint

@bp.route('/registro') #ruta para registro de entrenadores
def registro(): #funcion de registro
    return render_template('auth/registro.html') #return de la funcion

@bp.route('/acceso') #ruta para login usuarios
def acceso(): #funcion de login
    return render_template('auth/acceso.html') #return de la funcion