# Diagramas Backend Coach-Planning-Basketball

## 1. Arquitectura de la aplicación

```mermaid
flowchart LR
    RUN[run.py] --> APP_FACTORY[create_app]
    APP_FACTORY --> FLASK[Flask app]

    FLASK --> CFG[Config app]
    FLASK --> DB[SQLAlchemy]
    FLASK --> MIGRATE[Flask-Migrate]

    FLASK --> BP_AUTH[auth /auth]
    FLASK --> BP_PERFIL[perfil /perfil]
    FLASK --> BP_EJ[ejercicios /ejercicios]
    FLASK --> BP_SES[sesiones /sesiones]
    FLASK --> BP_PLAN[planning /planning]

    BP_AUTH --> AUTH_VISTAS[registro, acceso, logout]
    BP_PERFIL --> PERFIL_VISTAS[perfil, config, listados]
    BP_EJ --> EJ_VISTAS[crear, editar, eliminar ejercicios]
    BP_SES --> SES_VISTAS[crear, editar, eliminar sesiones]
    BP_PLAN --> PLAN_VISTAS[crear, editar, eliminar plannings]
```

## 2. Modelos y relaciones de datos

```mermaid
flowchart LR
    DB[(Base de datos cpb.db)]

    DB --> USUARIO[Usuario]
    DB --> EJERCICIO[Ejercicio]
    DB --> SESION[Sesion]
    DB --> PLANNING[Planning]
    DB --> SEGUIMIENTO[Seguimiento]

    EJERCICIO -->|autor| USUARIO
    SESION -->|autor| USUARIO
    PLANNING -->|autor| USUARIO

    SEGUIMIENTO -->|seguidor_alias| USUARIO
    SEGUIMIENTO -->|seguido_alias| USUARIO

    SESION -->|ejercicios_ids| EJERCICIO
    PLANNING -->|sesiones_ids| SESION
```

> Cada bloque es un diagrama Mermaid independiente; puedes previsualizarlos en VS Code o exportarlos a PNG.