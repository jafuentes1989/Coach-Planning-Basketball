#archivo que indica que app es el paquete de la APP
from flask import Flask #importamos la clase Flask

def create_app(): #funcion para crear la APP
    app=Flask(__name__) #instancio APP como objeto Flask

    #configuracion del proyecto
    app.config.from_mapping( #mapeo
        DEBUG=True, #debug activado
        SECRET_KEY='dev'#key para DB
    )

    @app.route('/') #vista inicio
    def inicio(): #funcion inicio
        return "¡Hola, Mundo!"
    
    return app #salida de la funcion