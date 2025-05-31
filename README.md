# Sistema de Gestión de Buses

Una aplicación web para la gestión de buses, estaciones y rutas de transporte público.

## Requisitos

- Python 3.8+
- FastAPI
- Supabase (para la base de datos)

## Instalación

1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd sistema-gestion-buses
```

2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con:

```
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_key_de_supabase
```

## Ejecutar la aplicación

```bash
python main.py
```

Abre tu navegador en http://localhost:8000

## Estructura del Proyecto

- `main.py`: Punto de entrada principal
- `app/`: Módulo principal de la aplicación
  - `routers/`: Rutas de la API
  - `database.py`: Configuración de la base de datos
- `static/`: Archivos estáticos (CSS, JS, imágenes)
- `templates/`: Plantillas HTML

## Funcionalidades

- Gestión de buses
- Gestión de estaciones
- Asignación y monitoreo de rutas
- Estadísticas y reportes

## API

La documentación de la API está disponible en `/docs` después de iniciar la aplicación.
