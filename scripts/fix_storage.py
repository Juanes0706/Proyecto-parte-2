import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(levelname)s:%(name)s:%(message)s')

logger = logging.getLogger('main')

# Cargar variables de entorno
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

def comprobar_conexion() -> bool:
    """Comprobar conexión a Supabase"""
    try:
        logger.info("Comprobando conexión a Supabase...")
        supabase = create_client(supabase_url, supabase_key)

        # Probar una consulta simple
        data, error = supabase.table("buses").select("count").execute()
        if error:
            logger.error(f"❌ Error al consultar Supabase: {error}")
            return False

        logger.info("✅ Conexión a Supabase exitosa")
        return True
    except Exception as e:
        logger.error(f"❌ Error de conexión: {str(e)}")
        return False

def reparar_storage():
    """Reparar y verificar el acceso al storage de Supabase"""
    try:
        logger.info("Iniciando reparación de storage...")
        supabase = create_client(supabase_url, supabase_key)

        # 1. Listar buckets existentes
        try:
            buckets = supabase.storage.list_buckets()
            logger.info("Buckets encontrados:")
            for bucket in buckets:
                try:
                    # Diferentes formas de acceder al nombre según la versión
                    if hasattr(bucket, 'name'):
                        bucket_name = bucket.name
                    elif hasattr(bucket, 'id'):
                        bucket_name = bucket.id
                    elif isinstance(bucket, dict) and 'name' in bucket:
                        bucket_name = bucket['name']
                    else:
                        bucket_name = str(bucket)
                    logger.info(f"  - {bucket_name}")
                except Exception as e:
                    logger.info(f"  - {str(bucket)} (error al leer nombre: {e})")
        except Exception as e:
            logger.error(f"❌ Error al listar buckets: {str(e)}")

        # 2. Crear bucket de prueba
        bucket_nombre = "buses-imagenes"
        try:
            # Primero verificar si existe
            bucket_existe = False
            try:
                supabase.storage.get_bucket(bucket_nombre)
                bucket_existe = True
                logger.info(f"✅ Bucket '{bucket_nombre}' ya existe")
            except Exception:
                bucket_existe = False

            # Si no existe, crearlo
            if not bucket_existe:
                try:
                    # Método 1: Con opciones (versiones más recientes)
                    supabase.storage.create_bucket(bucket_nombre, {"public": True})
                except Exception as e1:
                    logger.warning(f"Método 1 falló: {e1}")
                    try:
                        # Método 2: Sin opciones (versiones anteriores)
                        supabase.storage.create_bucket(bucket_nombre)
                    except Exception as e2:
                        logger.error(f"❌ Ambos métodos fallaron: {e2}")
                        raise e2

                logger.info(f"✅ Bucket '{bucket_nombre}' creado")
        except Exception as e:
            logger.error(f"❌ Error al crear bucket: {str(e)}")

        # 3. Probar operaciones de archivo
        try:
            logger.info("Probando operaciones de archivos...")
            archivo_contenido = b"Test de storage"
            archivo_ruta = "test_fix.txt"

            # Subir archivo
            try:
                # Método 1: API más reciente
                result = supabase.storage.from_(bucket_nombre).upload(
                    path=archivo_ruta,
                    file=archivo_contenido,
                    file_options={"content-type": "text/plain"}
                )
                logger.info("✅ Archivo subido correctamente con API reciente")
            except Exception as e1:
                logger.warning(f"Método de subida 1 falló: {e1}")
                try:
                    # Método 2: API anterior
                    result = supabase.storage.from_(bucket_nombre).upload(archivo_ruta, archivo_contenido)
                    logger.info("✅ Archivo subido correctamente con API anterior")
                except Exception as e2:
                    logger.error(f"❌ Ambos métodos de subida fallaron: {e2}")
                    raise e2

            # Obtener URL
            try:
                # Método 1: get_public_url
                url = supabase.storage.from_(bucket_nombre).get_public_url(archivo_ruta)
                logger.info(f"✅ URL pública obtenida: {url}")
            except Exception as e1:
                logger.warning(f"Método URL 1 falló: {e1}")
                try:
                    # Método 2: signed URL
                    url_info = supabase.storage.from_(bucket_nombre).create_signed_url(archivo_ruta, 3600)
                    url = url_info['signedURL'] if isinstance(url_info, dict) and 'signedURL' in url_info else str(url_info)
                    logger.info(f"✅ URL firmada obtenida: {url}")
                except Exception as e2:
                    logger.error(f"❌ Ambos métodos de URL fallaron: {e2}")

            # Eliminar archivo
            try:
                # Método 1: lista de rutas
                supabase.storage.from_(bucket_nombre).remove([archivo_ruta])
                logger.info("✅ Archivo eliminado correctamente con método 1")
            except Exception as e1:
                logger.warning(f"Método de eliminación 1 falló: {e1}")
                try:
                    # Método 2: ruta simple
                    supabase.storage.from_(bucket_nombre).remove(archivo_ruta)
                    logger.info("✅ Archivo eliminado correctamente con método 2")
                except Exception as e2:
                    logger.error(f"❌ Ambos métodos de eliminación fallaron: {e2}")

            logger.info("✅ Prueba de storage completada con éxito")
            return True
        except Exception as e:
            logger.error(f"❌ Prueba de storage falló: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"❌ Error general: {str(e)}")
        return False

def mostrar_instrucciones():
    logger.info("""\n==== INSTRUCCIONES PARA RESOLVER PROBLEMAS DE STORAGE ====

1. Asegúrate de tener la versión correcta de la biblioteca supabase:
   pip install supabase==1.0.3

2. Verifica las credenciales en tu archivo .env:
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-api-key

3. Modifica las funciones que trabajan con storage para que funcionen
   con diferentes versiones de la API:

   # Ejemplo para subir archivos:
   try:
       # Intenta con API más reciente
       supabase.storage.from_(bucket).upload(
           path=ruta_archivo,
           file=contenido,
           file_options={"content-type": "image/jpeg"}
       )
   except Exception as e:
       # Si falla, intenta con API anterior
       supabase.storage.from_(bucket).upload(ruta_archivo, contenido)

4. Para cualquier operación con buckets, usa estructuras try-except
   para manejar diferentes versiones de la API.\n""")

if __name__ == "__main__":
    if not comprobar_conexion():
        logger.error("No se pudo conectar a Supabase. Revisa tu URL y API Key.")
    else:
        if reparar_storage():
            logger.info("✅ Todo está funcionando correctamente.")
        else:
            logger.warning("⚠️ Se encontraron problemas con el storage.")
            mostrar_instrucciones()
