#archivo que trabaja la autenticación de usuarios
from flask import Blueprint, render_template, request, redirect, url_for, flash 
#importamos Blueprint para crear vistas modulares
#importamos render_template para renderizar las vistas creadas en HTML
#importamos request para manejar las solicitudes HTTP
#importamos redirect y url_for para redirigir a diferentes rutas
#importamos flash para mostrar mensajes flash al usuario

from werkzeug.security import generate_password_hash, check_password_hash
#importamos funciones de seguridad para manejar contraseñas de forma segura

from .models import Usuario 
# importamos el modelo Usuario desde el archivo models.py

from app import db 
# importamos la instancia de la base de datos desde la aplicación

bp=Blueprint('auth',__name__, url_prefix='/auth') #creamos bp como objeto Blueprint

@bp.route('/registro', methods=('GET','POST')) #ruta para registro de entrenadores
def registro(): #funcion de registro
    if request.method=='POST': #si el metodo de la solicitud es POST
        alias=request.form['alias'] #obtenemos el alias del formulario
        nombre=request.form['nombre'] #obtenemos el nombre del formulario
        apellido=request.form['apellido'] #obtenemos el apellido del formulario
        email=request.form['email'] #obtenemos el email del formulario
        password=request.form['password'] #obtenemos la contraseña del formulario
        nivel=request.form['nivel'] #obtenemos el nivel del formulario
        temporadas=request.form['temporadas'] #obtenemos las temporadas del formulario
        club=request.form['club'] #obtenemos el club del formulario

        usuario_existente=Usuario.query.filter_by(alias=alias).first() #verificamos si el alias ya existe en la base de datos
        email_existente=Usuario.query.filter_by(email=email).first() #verificamos si el email ya existe en la base de datos
#//////////////////////////////////////////////////////////////////////
        if usuario_existente==None and email_existente==None : #si el alias y el email no existen
            nuevo_usuario1=Usuario( #creamos un nuevo usuario
                alias=alias,
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=generate_password_hash(password), #guardamos la contraseña hasheada
                nivel=nivel,
                temporadas=temporadas,
                club=club
            )

            db.session.add(nuevo_usuario1) #añadimos el nuevo usuario a la sesión de la base de datos
            db.session.commit() #confirmamos los cambios en la base de datos
            return redirect(url_for('auth.acceso')) #redireccionamos al login
        elif usuario_existente!=None: #si el alias ya existe
            flash('El alias ya existe. Por favor, elige otro.') #mostramos mensaje de error
        elif email_existente!=None: #si el email ya existe
            flash('El email ya está registrado. Por favor, utiliza otro.') #mostramos mensaje de error

    return render_template('auth/registro.html') #return de la funcion


@bp.route('/acceso') #ruta para login usuarios
def acceso(): #funcion de login
    return render_template('auth/acceso.html') #return de la funcion