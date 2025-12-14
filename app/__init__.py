#archivo que indica que app es el paquete de la APP
from flask import Flask, render_template 
#importamos la clase Flask
#importamos render_template para renderizar las vistas creadas en HTML
from flask_sqlalchemy import SQLAlchemy
#Importamos SQLAlchemy para la gestion de la base de datos
from flask_migrate import Migrate
#Importamos Migrate para las migraciones de la base de datos

db=SQLAlchemy() #instanciamos SQLAlchemy como objeto DB
migrate = Migrate() #instanciamos Migrate

def create_app(): #funcion para crear la APP
    app=Flask(__name__) #instancio APP como objeto Flask

    #configuracion del proyecto
    app.config.from_mapping( #mapeo
        DEBUG=True, #debug activado
        SECRET_KEY='dev',#key para DB
        SQLALCHEMY_DATABASE_URI="sqlite:///cpb.db"#ruta de la base de datos
    )

    db.init_app(app) #inicializamos la base de datos con la APP
    migrate.init_app(app, db) #inicializamos Migrate con la APP y DB

    #registro de blueprints
    from . import perfil #importamos el archivo vistas
    app.register_blueprint(perfil.bp) #registramos el blueprint PERFIL
    from . import auth #importamos el archivo auth
    app.register_blueprint(auth.bp) #registramos el blueprint AUTH
    from . import ejercicios #importamos el archivo ejercicios
    app.register_blueprint(ejercicios.bp) #registramos el blueprint EJERCICIOS
    from . import sesiones #importamos el archivo sesiones
    app.register_blueprint(sesiones.bp) #registramos el blueprint SESIONES

    @app.route('/') #vista inicio
    def inicio(): #funcion inicio
        return render_template('inicio.html')#devolvemos inicio.html
    
    with app.app_context(): #contexto de la APP
        db.create_all() #creamos las tablas de la base de datos

    return app #salida de la funcion