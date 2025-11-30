#archivo que indica que app es el paquete de la APP
from flask import Flask, render_template 
#importamos la clase Flask
#importamos render_template para renderizar las vistas creadas en HTML

def create_app(): #funcion para crear la APP
    app=Flask(__name__) #instancio APP como objeto Flask

    #configuracion del proyecto
    app.config.from_mapping( #mapeo
        DEBUG=True, #debug activado
        SECRET_KEY='dev'#key para DB
    )

    #registro de blueprints
    from . import perfil #importamos el archivo vistas
    app.register_blueprint(perfil.bp) #registramos el blueprint PERFIL
    from . import auth #importamos el archivo auth
    app.register_blueprint(auth.bp) #registramos el blueprint AUTH

    @app.route('/') #vista inicio
    def inicio(): #funcion inicio
        return render_template('inicio.html')#devolvemos inicio.html
    
    return app #salida de la funcion