#archivo que trabaja la autenticación de usuarios
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g 
#importamos Blueprint para crear vistas modulares
#importamos render_template para renderizar las vistas creadas en HTML
#importamos request para manejar las solicitudes HTTP
#importamos redirect y url_for para redirigir a diferentes rutas
#importamos flash para mostrar mensajes flash al usuario
#importamos session para manejar sesiones de usuario
#importamos g para almacenar datos durante la solicitud

from werkzeug.security import generate_password_hash, check_password_hash
#generate_password_hash para hashear contraseñas
#check_password_hash para verificar contraseñas hasheadas

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


@bp.route('/acceso', methods=('GET','POST')) #ruta para login usuarios
def acceso(): #funcion de login
    if request.method=='POST': #si el metodo de la solicitud es POST
        alias=request.form['alias'] #obtenemos el alias del formulario
        password=request.form['password'] #obtenemos la contraseña del formulario

        #validar datos
        usuario=Usuario.query.filter_by(alias=alias).first() #buscamos el usuario por alias
        if usuario==None: #si el alias no existe
            flash('Alias incorrecto. Por favor, intenta de nuevo.') #mostramos mensaje de error
        elif not check_password_hash(usuario.password, password): #si la contraseña no coincide
            flash('Contraseña incorrecta. Por favor, intenta de nuevo.') #mostramos mensaje de error

        #iniciar sesion
        else: #si el alias y la contraseña son correctos
            session.clear() #limpiamos la sesión
            session['usuario_alias']=usuario.alias #guardamos el alias del usuario en la sesión
            return redirect(url_for('perfil.perfil')) #redireccionamos a la página de perfil
            
    return render_template('auth/acceso.html') #return de la funcion


@bp.before_app_request #antes de cada solicitud
def cargar_usuario(): #funcion para cargar el usuario antes de cada solicitud
    alias=session.get('usuario_alias') #obtenemos el alias del usuario de la sesión
    if alias is None: #si no hay alias en la sesión
        g.usuario=None #establecemos g.usuario como None
    else: #si hay alias en la sesión
        g.usuario=Usuario.query.filter_by(alias=alias).first() #cargamos el usuario desde la base de datos y lo asignamos a g.usuario


@bp.route('/cerrar_sesion') #ruta para cerrar sesión
def cerrar_sesion(): #funcion para cerrar sesión
    session.clear() #limpiamos la sesión
    return redirect(url_for('inicio')) #redireccionamos a la pagina de inicio