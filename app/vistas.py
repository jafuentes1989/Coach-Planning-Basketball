#archivo que contiene las vistas de la APP
from flask import Blueprint #importamos Blueprint para crear vistas modulares

bp=Blueprint('vistas',__name__, url_prefix='/vistas') #creamos bp como objeto Blueprint

@bp.route('/listadoEntrenos') #ruta para listado de entrenos
def listado(): #funcion de listado
    return "listado entrenos" #return de la funcion

@bp.route('/crearEntrenos') #ruta para crear entrenos
def crear(): #funcion de crear
    return "crear entrenos" #return de la funcion