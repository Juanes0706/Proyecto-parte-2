import os
from supabase import create_client
from dotenv import load_dotenv

def main():
    # Cargar variables de entorno
    load_dotenv()

    # Conectar a Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("Error: No se encontraron las variables de entorno SUPABASE_URL y SUPABASE_KEY")
        return

    supabase = create_client(supabase_url, supabase_key)
from dotenv import load_dotenv
import os
import sys
import time
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales de Supabase desde variables de entorno
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("==== Configuración de Storage de Supabase ====\n")
print(f"URL de Supabase: {url[:15]}..." if url else "❌ URL de Supabase no configurada")
print(f"API Key: {key[:10]}..." if key else "❌ API Key no configurada")

if not url or not key:
    print("❌ Error: No se encontraron las credenciales de Supabase en las variables de entorno")
    print("   Asegúrate de tener un archivo .env con SUPABASE_URL y SUPABASE_KEY")
    sys.exit(1)

# Crear cliente de Supabase
try:
    supabase: Client = create_client(url, key)
    print("✅ Conexión a Supabase establecida correctamente")
except Exception as e:
    print(f"❌ Error al conectar con Supabase: {str(e)}")
    sys.exit(1)

# Lista de buckets a crear con configuración
buckets_to_create = [
    {
        "name": "buses-imagenes",
        "description": "Imágenes de buses",
        "public": True
    },
    {
        "name": "estaciones-imagenes",
        "description": "Imágenes de estaciones",
        "public": True
    },
    {
        "name": "prueba-storage",
        "description": "Bucket de prueba para diagnóstico",
        "public": True
    }
]

# Obtener lista de buckets existentes
try:
    existing_buckets = supabase.storage.list_buckets()
    existing_bucket_names = []

    # Convertir a lista de nombres
    try:
        for bucket in existing_buckets:
            try:
                # Intentar obtener nombre como atributo
                name = bucket.name
            except AttributeError:
                # Intentar obtener nombre como diccionario
                if isinstance(bucket, dict) and 'name' in bucket:
                    name = bucket['name']
                else:
                    name = str(bucket)

            existing_bucket_names.append(name)
    except Exception as e:
        print(f"Error al procesar buckets: {e}")
        existing_bucket_names = []

    print("\nBuckets existentes:")
    for name in existing_bucket_names:
        print(f"- {name}")

    # Crear los buckets que no existen
    print("\nCreando buckets necesarios...")
    for bucket in buckets_to_create:
        bucket_name = bucket['name']
        if bucket_name in existing_bucket_names:
            print(f"ℹ️ El bucket '{bucket_name}' ya existe")
            # Probar si podemos acceder al bucket
            try:
                # Intentar obtener información del bucket
                bucket_info = supabase.storage.get_bucket(bucket_name)
                print(f"  ✅ Bucket accesible")
            except Exception as e:
                print(f"  ⚠️ No se pudo acceder al bucket: {str(e)}")
        else:
            try:
                # Intentar crear el bucket con opciones avanzadas
                supabase.storage.create_bucket(
                    bucket_name, 
                    {"public": bucket.get('public', True)}
                )
                print(f"✅ Bucket '{bucket_name}' creado correctamente")
                # Esperar un momento para que el bucket se cree completamente
                time.sleep(1)
            except Exception as e:
                print(f"❌ Error al crear bucket '{bucket_name}': {str(e)}")
                # Si falla, intentar con opciones mínimas
                try:
                    supabase.storage.create_bucket(bucket_name)
                    print(f"  ✅ Creado con opciones mínimas")
                except Exception as e2:
                    if "already exists" in str(e2).lower():
                        print(f"  ℹ️ El bucket ya existe pero no era visible en la lista")
                    else:
                        print(f"  ❌ También falló el método alternativo: {str(e2)}")

    # Configurar permisos públicos para todos los buckets
    print("\nConfigurando permisos públicos...")
    for bucket_name in buckets_to_create:
        try:
            # Actualizar política para permitir acceso público
            # Nota: esta funcionalidad puede no estar disponible en todas las versiones
            try:
                supabase.storage.update_bucket(bucket_name, {"public": True})
                print(f"✅ Permisos públicos configurados para '{bucket_name}'")
            except Exception as e:
                print(f"⚠️ No se pudieron configurar permisos programáticamente: {str(e)}")
                print(f"   Por favor, configura manualmente los permisos en la interfaz de Supabase")
        except Exception as e:
            print(f"⚠️ Error al configurar permisos para '{bucket_name}': {str(e)}")

    # Probar subida de archivo a cada bucket
    print("\n==== Probando subida de archivos ====\n")
    for bucket in buckets_to_create:
        bucket_name = bucket['name']
        print(f"Probando bucket '{bucket_name}'...")

        try:
            # Crear contenido de prueba
            test_content = f"Prueba de bucket {bucket_name} - {time.time()}".encode()
            test_path = f"test-{int(time.time())}.txt"

            # Intentar subir con el método estándar
            try:
                result = supabase.storage.from_(bucket_name).upload(
                    path=test_path,
                    file=test_content,
                    file_options={"content-type": "text/plain"}
                )
                print(f"  ✅ Archivo subido con método estándar")
                upload_success = True
            except Exception as e1:
                print(f"  ⚠️ Error con método estándar: {str(e1)}")
                # Intentar método alternativo
                try:
                    result = supabase.storage.from_(bucket_name).upload(test_path, test_content)
                    print(f"  ✅ Archivo subido con método alternativo")
                    upload_success = True
                except Exception as e2:
                    print(f"  ❌ Error con método alternativo: {str(e2)}")
                    upload_success = False

            # Si se subió correctamente, intentar obtener URL
            if upload_success:
                try:
                    # Intentar obtener URL pública
                    url = supabase.storage.from_(bucket_name).get_public_url(test_path)
                    print(f"  ✅ URL pública obtenida: {url[:60]}...")
                except Exception as e3:
                    print(f"  ⚠️ Error al obtener URL pública: {str(e3)}")
                    # Intentar URL firmada
                    try:
                        signed_url = supabase.storage.from_(bucket_name).create_signed_url(test_path, 60)
                        print(f"  ✅ URL firmada obtenida")
                    except Exception as e4:
                        print(f"  ❌ Error al obtener URL firmada: {str(e4)}")

                # Intentar eliminar el archivo de prueba
                try:
                    supabase.storage.from_(bucket_name).remove([test_path])
                    print(f"  ✅ Archivo eliminado correctamente")
                except Exception as e5:
                    print(f"  ⚠️ Error al eliminar archivo: {str(e5)}")
                    # Intentar método alternativo
                    try:
                        supabase.storage.from_(bucket_name).remove(test_path)
                        print(f"  ✅ Archivo eliminado con método alternativo")
                    except Exception as e6:
                        print(f"  ❌ Error con método alternativo: {str(e6)}")
        except Exception as e:
            print(f"  ❌ Error general: {str(e)}")

    print("\n✨ Proceso completado")
    print("IMPORTANTE: Si encontraste errores, verifica:")
    print("1. Que las credenciales de Supabase sean correctas")
    print("2. Que tengas permisos para administrar Storage")
    print("3. Configura manualmente los permisos en la interfaz de Supabase si es necesario")

except Exception as e:
    print(f"❌ Error general: {str(e)}")
    # Crear buckets para cada tipo de recurso
    buckets_to_create = [
        {
            "name": "buses-imagenes",
            "description": "Imágenes de buses"
        },
        {
            "name": "estaciones-imagenes",
            "description": "Imágenes de estaciones"
        }
    ]

    for bucket in buckets_to_create:
        try:
            # Intentar crear el bucket
            supabase.storage.create_bucket(
                bucket["name"],
                options={
                    "public": True,  # Imágenes accesibles públicamente
                    "file_size_limit": 10 * 1024 * 1024,  # Límite de 10MB por archivo
                    "allowed_mime_types": ["image/jpeg", "image/png", "image/gif", "image/webp"]
                }
            )
            print(f"✅ Bucket '{bucket['name']}' creado correctamente")
        except Exception as e:
            if "Duplicate" in str(e):
                print(f"ℹ️ El bucket '{bucket['name']}' ya existe")
            else:
                print(f"❌ Error al crear bucket '{bucket['name']}': {str(e)}")

if __name__ == "__main__":
    main()
