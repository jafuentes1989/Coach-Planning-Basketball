# Documentación técnica

Aplicación: **Coach-Planning-Basketball**  
Stack principal: Flask + SQLAlchemy + SQLite

## Arquitectura general

- **Entrada**: [run.py](run.py)
  - Llama a `create_app()` desde [app/__init__.py](app/__init__.py) y ejecuta `app.run()`.
- **Fábrica de aplicación**: función `create_app()` en [app/__init__.py](app/__init__.py)
  - Crea la instancia de `Flask`.
  - Configura:
    - `DEBUG`, `SECRET_KEY`
    - `SQLALCHEMY_DATABASE_URI = "sqlite:///cpb.db"`
    - `UPLOAD_FOLDER` para imágenes (`app/static/uploads`).
  - Inicializa extensiones:
    - `db = SQLAlchemy()`
    - `migrate = Migrate()` (Flask-Migrate).
  - Registra los blueprints:
    - `auth`, `perfil`, `ejercicios`, `sesiones`, `planning`.
  - Define la ruta raíz `/` que renderiza `inicio.html`.

## Módulos y blueprints

### 1. Autenticación – [app/auth.py](app/auth.py)

- Blueprint: `auth` con prefijo `/auth`.
- Funciones principales:
  - `/auth/registro`: registro de usuarios (`Usuario`).
    - Valida unicidad de `alias` y `email`.
    - Guarda la contraseña hasheada (`generate_password_hash`).
  - `/auth/acceso`: login.
    - Valida `alias` + `password` (`check_password_hash`).
    - Almacena `session['usuario_alias']`.
  - `/auth/cerrar_sesion`: logout (`session.clear()`).
- Hook global:
  - `@bp.before_app_request cargar_usuario`:
    - Carga `g.usuario` desde la sesión en cada petición.
- Decorador `acceso_requerido`:
  - Protege vistas privadas; si no hay usuario logueado, redirige a `/auth/acceso`.

### 2. Perfil y vistas generales – [app/perfil.py](app/perfil.py)

- Blueprint: `perfil` con prefijo `/perfil`.
- Funcionalidad:
  - `/perfil/` (dashboard):
    - Muestra estadísticas: nº ejercicios, sesiones, plannings, seguidores, siguiendo, solicitudes.
    - Aplica reglas de visibilidad:
      - Siempre propios.
      - De usuarios seguidos (`Seguimiento.estado='aceptado'`) solo elementos no confidenciales.
  - `/perfil/ver/<alias>`: vista de perfil ajeno con mismo layout que el propio.
  - `/perfil/configPerfil`: edición de datos de `Usuario` + subida de imagen de perfil.
  - `/perfil/ejercicios`, `/perfil/sesiones`, `/perfil/planning`:
    - Listados filtrados (con `request.args`) y lógica de visibilidad/confidencialidad.
    - Precargan las relaciones (ejercicios por sesión, sesiones por planning) para renderizar en plantillas.

### 3. Gestión de ejercicios – [app/ejercicios.py](app/ejercicios.py)

- Blueprint: `ejercicios` con prefijo `/ejercicios`.
- Rutas:
  - `/ejercicios/listado`: redirige al listado filtrado en `/perfil/ejercicios`.
  - `/ejercicios/crear_ejercicio` (GET/POST):
    - Crea un `Ejercicio` asociado a `g.usuario.alias`.
    - Gestiona subida de hasta 3 imágenes usando `UPLOAD_FOLDER` y `secure_filename`.
  - `/ejercicios/editar_ejercicio/<id>` (GET/POST):
    - Solo el autor puede editar (si no, `abort(403)`).
    - Permite reemplazar imágenes y actualizar campos.
  - `/ejercicios/eliminar_ejercicio/<id>`:
    - Solo el autor puede eliminar.

### 4. Gestión de sesiones – [app/sesiones.py](app/sesiones.py)

- Blueprint: `sesiones` con prefijo `/sesiones`.
- Rutas:
  - `/sesiones/listado`: redirige a `/perfil/sesiones`.
  - `/sesiones/crear_sesion` (GET/POST):
    - Crea una `Sesion` asociada al usuario actual.
    - Recibe una lista de `ejercicios_ids` (string de IDs separados por comas).
    - Filtra y valida que los ejercicios sean propios o de usuarios seguidos no confidenciales.
    - Calcula `duracion` como suma de `duracion` de los ejercicios permitidos.
    - Convierte `fecha` de string (`YYYY-MM-DD`) a `date`.
  - `/sesiones/editar_sesion/<id>` (GET/POST):
    - Misma lógica que crear, pero actualizando una sesión existente.
    - Solo el autor puede editar.
  - `/sesiones/eliminar_sesion/<id>`:
    - Solo el autor puede eliminar.

### 5. Gestión de plannings – [app/planning.py](app/planning.py)

- Blueprint: `planning` con prefijo `/planning`.
- Rutas:
  - `/planning/listado`: redirige a `/perfil/planning`.
  - `/planning/crear_planning` (GET/POST):
    - Crea un `Planning` asociado al usuario actual.
    - Recibe una lista de `sesiones_ids` (IDs separados por comas).
    - Valida que las sesiones sean propias o de usuarios seguidos no confidenciales.
    - Calcula `num_sesiones` como número de sesiones válidas.
    - Convierte `fecha` de string a `date`.
  - `/planning/editar_planning/<id>` (GET/POST):
    - Misma lógica que crear, pero actualizando un planning existente.
  - `/planning/eliminar_planning/<id>`:
    - Elimina un planning existente.

## Persistencia y migraciones

- ORM: SQLAlchemy, con modelos en [app/models.py](app/models.py).
- Motor de BBDD: SQLite (`cpb.db`).
- Migraciones: Flask-Migrate con ficheros en `migrations/`.
  - Script principal: [migrations/env.py](migrations/env.py).
  - Migraciones de versiones en `migrations/versions/`.

## Ficheros estáticos y subidas

- Directorio de estáticos: `app/static/`.
- Imágenes de ejercicios y perfiles:
  - Carpeta: `app/static/uploads/`.
  - La ruta almacenada en BBDD es relativa (por ejemplo, `uploads/archivo.png` o `/static/uploads/archivo.png` para perfil).

## Seguridad y control de acceso

- Autenticación por sesión (cookie de sesión de Flask).
- Contraseñas:
  - Nunca se guardan en texto plano.
  - Se almacenan con hash vía `werkzeug.security.generate_password_hash`.
- Autorización:
  - Decorador `acceso_requerido` obliga a estar logueado para acceder a la mayoría de vistas.
  - Control de propiedad en edición/eliminación de `Ejercicio` y `Sesion`.
  - Campo `confidencial` en `Ejercicio`, `Sesion` y `Planning` + tabla `Seguimiento` determinan qué ve cada usuario.

## Scripts auxiliares

- [recalcular_duracion_sesiones.py](recalcular_duracion_sesiones.py)
  - Probable uso: recalcular el campo `duracion` de las sesiones a partir de los ejercicios asociados.
- [recalcular_num_sesiones_planning.py](recalcular_num_sesiones_planning.py)
  - Probable uso: recalcular `num_sesiones` de los plannings a partir de `sesiones_ids`.

## Cómo ejecutar la aplicación (resumen)

1. Crear/activar entorno virtual (opcional pero recomendado).
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Ejecutar la app:
   - `python run.py`
4. Acceder en el navegador a `http://127.0.0.1:5000/`.

## Testing

- Framework: `pytest` (incluido en `requirements.txt`).
- Ubicación de tests: carpeta `tests/` en la raíz del proyecto.

### Configuración de la app para tests

- La función `create_app(test_config=None)` en [app/__init__.py](app/__init__.py) permite inyectar una configuración específica para testing.
- En [tests/conftest.py](tests/conftest.py) se define:
  - `TESTING = True`.
  - BBDD SQLite aislada: `sqlite:///test_cpb.db` (fichero en la raíz del proyecto).
  - Carpeta de uploads de prueba: `./test_uploads` (se crea y elimina automáticamente).
- Fixtures principales:
  - `app`: instancia de la aplicación para toda la sesión de tests, creando y eliminando las tablas.
  - `client`: cliente de pruebas de Flask (`app.test_client()`).
  - `app_context`: contexto de aplicación para poder trabajar con la BBDD en cada test.

### Áreas cubiertas por la suite

- Autenticación ([tests/test_auth.py](tests/test_auth.py))
  - Registro correcto de nuevo usuario.
  - Detección de alias y email duplicados.
  - Login correcto (crea sesión y redirige al perfil).
  - Mensajes de error para alias/contraseña incorrectos.
  - Cierre de sesión y protección de rutas mediante `acceso_requerido`.

- Ejercicios ([tests/test_ejercicios.py](tests/test_ejercicios.py))
  - Creación de ejercicios asociados al usuario logueado.
  - Edición de ejercicios (actualización de campos y confidencialidad).
  - Permisos: solo el autor puede editar o eliminar (otros usuarios reciben 403).

- Sesiones y plannings ([tests/test_sesiones_planning.py](tests/test_sesiones_planning.py))
  - Cálculo de `duracion` de una `Sesion` como suma de duraciones de ejercicios permitidos.
  - Cálculo de `num_sesiones` de un `Planning` a partir de `sesiones_ids`.
  - Filtrado de ejercicios no permitidos (no seguidos / confidenciales / IDs inválidos) al crear sesiones.
  - Manejo de fechas inválidas (respuesta 400).
  - Límite de 10 sesiones por planning.

- Visibilidad y confidencialidad ([tests/test_visibilidad.py](tests/test_visibilidad.py))
  - Listados de ejercicios/sesiones/plannings muestran:
    - Siempre los propios.
    - De usuarios seguidos solo elementos no confidenciales.
  - Verificación de que contenido confidencial o de usuarios no seguidos no aparece en los listados del perfil.

- Seguimiento de usuarios ([tests/test_seguimiento.py](tests/test_seguimiento.py))
  - Envío de solicitud de seguimiento (estado `pendiente`).
  - Aceptar/rechazar solicitudes desde el perfil del usuario seguido.
  - Dejar de seguir (elimina relaciones en estado `aceptado`).
  - Casos límite: no seguirse a uno mismo, no duplicar relaciones ya existentes (pendientes, aceptadas o rechazadas).

### Cómo ejecutar los tests

1. Crear/activar el entorno virtual.
2. Instalar dependencias (si no se han instalado):
   - `pip install -r requirements.txt`
3. Desde la raíz del proyecto, ejecutar:
   - `pytest`
4. Por defecto se ejecutan todos los tests de la carpeta `tests/`. Se pueden filtrar, por ejemplo:
   - `pytest tests/test_auth.py` para ejecutar solo los tests de autenticación.

## Ejemplos de flujos completos

### Flujo 1: Crear ejercicio → sesión → planning

1. **Crear ejercicio**
  - Ir a `/ejercicios/crear_ejercicio`.
  - Rellenar los campos del formulario (nombre, descripción, objetivo, categoría, fundamento trabajado, duración, etc.).
  - (Opcional) Subir hasta 3 imágenes del ejercicio.
  - Enviar el formulario; se crea un registro `Ejercicio` asociado al usuario logueado (`g.usuario.alias`).

2. **Crear sesión con los ejercicios anteriores**
  - Ir a `/sesiones/crear_sesion`.
  - Seleccionar fecha, título y resto de metadatos de la sesión (por ejemplo, categoría, tipo de sesión, confidencialidad).
  - Indicar la lista de ejercicios a usar mediante sus IDs en el campo `ejercicios_ids` (IDs separados por comas) o a través del selector de la interfaz.
  - El backend valida que cada ejercicio pertenece al usuario actual o a usuarios seguidos con contenido no confidencial.
  - La duración total de la `Sesion` se calcula automáticamente como la suma de las duraciones de los ejercicios válidos.
  - Guardar; se persiste la sesión vinculada al usuario.

3. **Crear planning con varias sesiones**
  - Ir a `/planning/crear_planning`.
  - Definir nombre, descripción, fecha de inicio/fin y nivel o categoría del planning.
  - Seleccionar las sesiones que formarán parte del planning (campo `sesiones_ids`, listado de IDs separados por comas o selector en la interfaz).
  - El backend valida las sesiones igual que en el caso de ejercicios (propias o de usuarios seguidos no confidenciales).
  - `num_sesiones` se calcula automáticamente como el número de sesiones válidas.
  - Guardar; se persiste el `Planning` asociado al usuario actual.

4. **Consulta del contenido creado**
  - Desde `/perfil/` se pueden ver los contadores globales (nº ejercicios, sesiones, plannings).
  - En `/perfil/ejercicios`, `/perfil/sesiones` y `/perfil/planning` se listan los objetos creados, aplicando filtros por fecha, categoría o confidencialidad según los parámetros de `request.args`.

### Flujo 2: Visualizar contenido de otros usuarios (seguimiento + confidencialidad)

1. **Seguir a otro usuario**
  - Localizar al usuario objetivo en las pantallas de búsqueda/listado de usuarios (blueprint de seguidores, por ejemplo `/seguidores/seguir_usuarios`).
  - Enviar una solicitud de seguimiento; se crea un registro en `Seguimiento` con `estado` inicial (por ejemplo, `pendiente`).

2. **Aceptar solicitud de seguimiento**
  - El usuario objetivo ve sus solicitudes en `/perfil/solicitudes`.
  - Al aceptar, el registro `Seguimiento` pasa a `estado='aceptado'`.

3. **Visualizar ejercicios, sesiones y plannings de usuarios seguidos**
  - En `/perfil/ejercicios`, `/perfil/sesiones` y `/perfil/planning`, además de los objetos propios, se muestran también los de usuarios seguidos con `Seguimiento.estado='aceptado'`.
  - La lógica de consulta filtra para que solo se muestren aquellos marcados como no confidenciales (`confidencial=False`).
  - De esta forma, un usuario puede reutilizar ejercicios y sesiones ajenas en sus propias sesiones/plannings, respetando siempre la configuración de confidencialidad.

Estos flujos complementan la descripción de módulos y modelos, y sirven como guía de alto nivel para entender cómo se usan las diferentes piezas de la aplicación en escenarios reales.