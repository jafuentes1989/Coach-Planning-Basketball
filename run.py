#archivo para ejecutar la APP
from app import create_app #importamos la funcion create_app desde el paquete app

if __name__=='__main__': #si el archivo es main
    app=create_app() #al objeto APP le pasamos la funcion create_app
    app.run() #ejecutamos APP