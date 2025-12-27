#archivo que contiene los modelos de la DB
from app import db #importa la instancia de la base de datos desde la aplicación
from datetime import datetime #importa datetime para manejar fechas y horas

class Usuario(db.Model): #clase Usuario que hereda de db.Model
    alias=db.Column(db.String(20), primary_key=True, unique=True) #alias del usuario, clave primaria
    nombre=db.Column(db.String(20), nullable=False) #nombre de usuario
    apellido=db.Column(db.String(20), nullable=False) #apellido de usuario
    email=db.Column(db.String, nullable=False, unique=True) #email del usuario, debe ser único
    password=db.Column(db.Text(20), nullable=False) #password del usuario
    nivel=db.Column(db.String) #nivel de curso del usuario
    temporadas=db.Column(db.Integer) #número de temporadas completadas por el usuario
    club=db.Column(db.String) #club al que pertenece el usuario
    profile_image=db.Column(db.String) #ruta de la imagen de perfil

    def __init__(self, alias, nombre, apellido, email, password, nivel, temporadas, club, profile_image=None): #constructor de la clase Usuario
        self.alias=alias
        self.nombre=nombre
        self.apellido=apellido
        self.email=email
        self.password=password
        self.nivel=nivel
        self.temporadas=temporadas
        self.club=club
        self.profile_image=profile_image

    def __repr__(self): #representación en cadena del objeto Usuario
        return f'<Usuario: {self.alias}>'  
    

class Ejercicio(db.Model): #clase Ejercicio que hereda de db.Model
    id=db.Column(db.Integer, primary_key=True, unique=True) #id del ejercicio, clave primaria
    autor=db.Column(db.String(20), db.ForeignKey('usuario.alias'), nullable=False) #autor del ejercicio, clave foránea que referencia al alias del usuario
    titulo=db.Column(db.String(20), nullable=False) #título del ejercicio
    fundamento_trabajado=db.Column(db.String(20), nullable=False) #fundamento principal trabajado (físico/técnico/táctico)
    imagen_url=db.Column(db.String, nullable=False) #primera imagen del ejercicio
    imagen_url_2=db.Column(db.String) #segunda imagen del ejercicio (opcional)
    imagen_url_3=db.Column(db.String) #tercera imagen del ejercicio (opcional)
    descripcion=db.Column(db.String(500)) #descripcion del ejercicio
    jugadores=db.Column(db.Integer) #número de jugadores
    duracion=db.Column(db.Integer) #duración del ejercicio en minutos
    confidencial=db.Column(db.Boolean, default=False) #indica si el ejercicio es confidencial
    #visibilidad=db.Column(db.Boolean, default=True) #visibilidad del ejercicio

    def __init__(self, autor, titulo, fundamento_trabajado, imagen_url, descripcion, jugadores, duracion, imagen_url_2=None, imagen_url_3=None): #constructor de la clase Ejercicio
        self.autor=autor
        self.titulo=titulo
        self.fundamento_trabajado=fundamento_trabajado
        self.imagen_url=imagen_url
        self.imagen_url_2=imagen_url_2
        self.imagen_url_3=imagen_url_3
        self.descripcion=descripcion
        self.jugadores=jugadores
        self.duracion=duracion
        #self.visibilidad=visibilidad

    def __repr__(self): #representación en cadena del objeto Ejercicio
        return f'<Ejercicio: {self.titulo}>'  
    
    
class Sesion(db.Model): #clase Sesion que hereda de db.Model
    id=db.Column(db.Integer, primary_key=True, unique=True) #id de la sesion, clave primaria
    autor=db.Column(db.String(20), db.ForeignKey('usuario.alias'), nullable=False) #autor de la sesion, clave foránea que referencia al alias del usuario
    #idEjercicio=db.Column(db.Integer, db.ForeignKey('ejercicio.id'), nullable=False) #id del ejercicio, clave foránea que referencia al id del ejercicio
    fecha=db.Column(db.DateTime, nullable=False) #fecha de la sesión
    titulo=db.Column(db.String(20), nullable=False) #título de la sesion
    descripcion=db.Column(db.String(500)) #descripcion de la sesion
    duracion=db.Column(db.Integer) #duración de la sesion en minutos
    confidencial=db.Column(db.Boolean, default=False) #indica si la sesion es confidencial
    #visibilidad=db.Column(db.Boolean, default=True) #visibilidad de la sesion

    def __init__(self, autor, fecha, titulo, descripcion, duracion): #constructor de la clase Sesion
        self.autor=autor
        #self.idEjercicio=idEjercicio
        self.fecha=fecha
        self.titulo=titulo
        self.descripcion=descripcion
        self.duracion=duracion
        #self.visibilidad=visibilidad

    def __repr__(self): #representación en cadena del objeto Sesion
        return f'<Sesion: {self.titulo}>'
    

class Planning(db.Model): #clase Planning que hereda de db.Model
    id=db.Column(db.Integer, primary_key=True, unique=True) #id de la planning, clave primaria
    autor=db.Column(db.String(20), db.ForeignKey('usuario.alias'), nullable=False) #autor de la planning, clave foránea que referencia al alias del usuario
    #idSesion=db.Column(db.Integer, db.ForeignKey('sesion.id'), nullable=False) #id de la sesion, clave foránea que referencia al id de la sesion
    fecha=db.Column(db.DateTime, nullable=False) #fecha de la sesión
    titulo=db.Column(db.String(20), nullable=False) #título de la sesion
    descripcion=db.Column(db.String(500)) #descripcion de la sesion
    num_sesiones=db.Column(db.Integer) #numero de sesiones
    visibilidad=db.Column(db.Boolean, default=True) #visibilidad de la sesion
    confidencial=db.Column(db.Boolean, default=False) #indica si el planning es confidencial

    def __init__(self, autor, fecha, titulo, descripcion, num_sesiones): #constructor de la clase Planning
        self.autor=autor
        #self.idSesion=idSesion
        self.fecha=fecha
        self.titulo=titulo
        self.descripcion=descripcion
        self.num_sesiones=num_sesiones
        #self.visibilidad=visibilidad

    def __repr__(self): #representación en cadena del objeto Planning
        return f'<Planning: {self.titulo}>'


class Seguimiento(db.Model): #tabla de relaciones de seguidores
    id = db.Column(db.Integer, primary_key=True, unique=True)
    seguidor_alias = db.Column(db.String(20), db.ForeignKey('usuario.alias'), nullable=False) #quien sigue
    seguido_alias = db.Column(db.String(20), db.ForeignKey('usuario.alias'), nullable=False) #a quien sigue
    estado = db.Column(db.String(20), nullable=False, default='pendiente') #estado de la solicitud: pendiente/aceptado/rechazado

    def __init__(self, seguidor_alias, seguido_alias, estado='pendiente'):
        self.seguidor_alias = seguidor_alias
        self.seguido_alias = seguido_alias
        self.estado = estado

    def __repr__(self):
        return f'<Seguimiento: {self.seguidor_alias} -> {self.seguido_alias}>'