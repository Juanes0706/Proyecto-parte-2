import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from app.routers import buses, estaciones
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.database import inicializar_storage

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sistema de Gestión de Buses")

# Inicializar storage con manejo de errores mejorado
try:
    logger.info("🔄 Iniciando inicialización de storage...")
    storage_ok, supabase_url, supabase_key = inicializar_storage()
    if storage_ok:
        logger.info("✅ Storage inicializado correctamente")
    else:
        logger.warning("⚠️ No se pudo inicializar el storage, verifique los logs")

    # Verificar credenciales
    if not supabase_url or not supabase_key:
        logger.error("❌ Credenciales de Supabase no configuradas correctamente")
    else:
        logger.info(f"ℹ️ Usando Supabase URL: {supabase_url}")

    # Intentar una prueba directa de storage
    try:
        from app.database import get_db
        supabase = get_db()
        test_file = "test.txt"
        test_bucket = "buses-imagenes"
        test_content = b"test content"

        # Intentar listar buckets
        buckets = supabase.storage.list_buckets()
        logger.info(f"ℹ️ Buckets disponibles: {[b['name'] for b in buckets]}")

        # Intentar subir un archivo de prueba
        supabase.storage.from_(test_bucket).upload(test_file, test_content)
        logger.info(f"✅ Prueba de subida exitosa a {test_bucket}/{test_file}")

        # Limpiar el archivo de prueba
        supabase.storage.from_(test_bucket).remove([test_file])
    except Exception as test_error:
        logger.error(f"❌ Prueba de storage falló: {str(test_error)}")

except Exception as e:
    logger.error(f"❌ Error al inicializar storage: {str(e)}")

# Archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
jinja_env = Environment(
    loader=FileSystemLoader("templates"),
    auto_reload=True,
    cache_size=0
)
templates = Jinja2Templates(directory="templates")
templates.env = jinja_env

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta principal
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    try:
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        # Fallback básico
        return HTMLResponse(content="<html><body><h1>Sistema de Gestión de Buses</h1><p>Error cargando la plantilla.</p></body></html>")

# Routers
app.include_router(buses.router)
app.include_router(estaciones.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
