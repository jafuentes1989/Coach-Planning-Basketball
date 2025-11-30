#archivo que trabaja la autenticación de usuarios
from flask import Blueprint #importamos Blueprint para crear vistas modulares

bp=Blueprint('auth',__name__, url_prefix='/auth') #creamos bp como objeto Blueprint

@bp.route('/registro') #ruta para registro de entrenadores
def registro(): #funcion de registro
    return "registro usuario" #return de la funcion

@bp.route('/login') #ruta para login usuarios
def login(): #funcion de login
    return "login usuario" #return de la funcion