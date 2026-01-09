# Diagramas Frontend Coach-Planning-Basketball

## 1. Navegación principal

```mermaid
flowchart TD
    U[Usuario navegador] --> R[Rutas Flask]

    subgraph Publica
        R --> R_inicio[GET / - inicio.html]
        R --> R_registro[GET /auth/registro - registro.html]
        R --> R_acceso[GET /auth/acceso - acceso.html]
    end

    subgraph Privada
        R --> R_perfil[GET /perfil/ - perfil.html]
        R --> R_config[GET /perfil/configPerfil - configPerfil.html]
    end
```

## 2. Zona privada: listados y CRUD

```mermaid
flowchart LR
    PERFIL[Vista perfil.html] --> L_EJS[GET /perfil/ejercicios - ejercicios.html]
    PERFIL --> L_SES[GET /perfil/sesiones - sesiones.html]
    PERFIL --> L_PLAN[GET /perfil/planning - planning.html]

    %% Ejercicios
    L_EJS --> EJ_CREAR[GET /ejercicios/crear_ejercicio - crear_ejercicio.html]
    L_EJS --> EJ_EDIT[GET /ejercicios/editar_ejercicio - editar_ejercicio.html]

    %% Sesiones
    L_SES --> SES_CREAR[GET /sesiones/crear_sesion - crear_sesion.html]
    L_SES --> SES_EDIT[GET /sesiones/editar_sesion - editar_sesion.html]

    %% Plannings
    L_PLAN --> PLAN_CREAR[GET /planning/crear_planning - crear_planning.html]
    L_PLAN --> PLAN_EDIT[GET /planning/editar_planning - editar_planning.html]
```

> Cada bloque es un diagrama Mermaid independiente; puedes previsualizarlos en VS Code o exportarlos a PNG.