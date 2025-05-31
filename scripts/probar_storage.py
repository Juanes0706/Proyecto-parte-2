from dotenv import load_dotenv
import os
import sys
from supabase import create_client, Client
import uuid

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales de Supabase desde variables de entorno
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

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

# Definir el nombre del bucket
bucket_name = "buses-imagenes-test"

# Probar operaciones de Storage
try:
    # Intentar crear el bucket (si no existe)
    try:
        # Primero verificamos si el bucket existe
        bucket_exists = False
        buckets = supabase.storage.list_buckets()
        for bucket in buckets:
            if bucket.name == bucket_name:
                bucket_exists = True
                break

        if not bucket_exists:
            print(f"Creando bucket '{bucket_name}'...")
            supabase.storage.create_bucket(bucket_name, {"public": True})
            print(f"✅ Bucket '{bucket_name}' creado correctamente")
        else:
            print(f"✅ Bucket '{bucket_name}' ya existe")
    except Exception as e:
        print(f"❌ Error al verificar/crear bucket: {str(e)}")
        sys.exit(1)

    # Subir un archivo de prueba
    try:
        # Crear un archivo de prueba
        test_file_content = b"Esta es una prueba de storage de Supabase"
        test_file_name = f"test-{uuid.uuid4()}.txt"

        print(f"Subiendo archivo '{test_file_name}'...")

        # Versión 1: Usando from_ (método más nuevo)
        try:
            # Usar el nuevo método upload
            response = supabase.storage.from_(bucket_name).upload(
                path=test_file_name,
                file=test_file_content,
                file_options={"content-type": "text/plain"}
            )
            print(f"✅ Archivo subido correctamente usando from_().upload()")
        except Exception as e1:
            print(f"❌ Error usando from_().upload(): {str(e1)}")

            # Intentar con el método alternativo
            try:
                response = supabase.storage.from_(bucket_name).upload(test_file_name, test_file_content)
                print(f"✅ Archivo subido correctamente usando sintaxis alternativa")
            except Exception as e2:
                print(f"❌ Error con sintaxis alternativa: {str(e2)}")
                raise e2

        # Obtener URL pública
        try:
            # Intentar obtener URL pública usando el nuevo método get_public_url
            url_publica = supabase.storage.from_(bucket_name).get_public_url(test_file_name)
            print(f"✅ URL pública obtenida correctamente: {url_publica}")
        except Exception as e:
            print(f"❌ Error al obtener URL pública: {str(e)}")

            # Intentar método alternativo
            try:
                url_publica = supabase.storage.from_(bucket_name).create_signed_url(test_file_name, 3600)
                print(f"✅ URL firmada obtenida como alternativa: {url_publica}")
            except Exception as e2:
                print(f"❌ Error al obtener URL firmada: {str(e2)}")

        # Eliminar el archivo de prueba
        try:
            supabase.storage.from_(bucket_name).remove([test_file_name])
            print(f"✅ Archivo eliminado correctamente")
        except Exception as e:
            print(f"❌ Error al eliminar archivo: {str(e)}")

    except Exception as e:
        print(f"❌ Error en operaciones de archivos: {str(e)}")

except Exception as e:
    print(f"❌ Error general en la prueba de storage: {str(e)}")

print("\n📋 Resumen de versiones:")
try:
    import pkg_resources
    print(f"- Python: {sys.version}")
    print(f"- Supabase: {pkg_resources.get_distribution('supabase').version}")
    print(f"- Storage: {type(supabase.storage).__name__}")
    print(f"- Bucket: {type(supabase.storage.from_(bucket_name)).__name__}")
except Exception as e:
    print(f"Error al obtener versiones: {str(e)}")

print("\n✨ Prueba de storage completada")
