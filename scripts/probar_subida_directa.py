import os
from dotenv import load_dotenv
from supabase import create_client
import uuid
import time

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print(f"URL: {supabase_url}")
print(f"KEY: {supabase_key[:10]}..." if supabase_key else "KEY: No configurada")

if not supabase_url or not supabase_key:
    print("❌ Error: Variables de entorno no configuradas")
    exit(1)

# Conectar a Supabase
try:
    print("\nConectando a Supabase...")
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Conexión exitosa")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

# Verificar buckets existentes
try:
    print("\nListando buckets...")
    buckets = supabase.storage.list_buckets()

    print("Buckets encontrados:")
    for bucket in buckets:
        try:
            if hasattr(bucket, 'name'):
                bucket_name = bucket.name
            elif hasattr(bucket, 'id'):
                bucket_name = bucket.id
            elif isinstance(bucket, dict) and 'name' in bucket:
                bucket_name = bucket['name']
            else:
                bucket_name = str(bucket)
            print(f"- {bucket_name}")
        except Exception as e:
            print(f"- Error al leer nombre: {e}")
except Exception as e:
    print(f"❌ Error al listar buckets: {e}")

# Nombre del bucket a usar
bucket_name = "buses-imagenes"

# Verificar si el bucket existe
try:
    print(f"\nVerificando bucket '{bucket_name}'...")
    supabase.storage.get_bucket(bucket_name)
    print(f"✅ Bucket '{bucket_name}' existe")
except Exception as e:
    print(f"❌ Bucket no encontrado: {e}")

    # Intentar crear el bucket
    try:
        print(f"Creando bucket '{bucket_name}'...")
        supabase.storage.create_bucket(bucket_name, {"public": True})
        print(f"✅ Bucket creado correctamente")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️ El bucket ya existe pero no es accesible")
        else:
            print(f"❌ Error al crear bucket: {e}")
            # Intentar método alternativo
            try:
                supabase.storage.create_bucket(bucket_name)
                print(f"✅ Bucket creado con método alternativo")
            except Exception as e2:
                print(f"❌ También falló método alternativo: {e2}")
                exit(1)

# Generar nombre único para prueba
file_id = uuid.uuid4()
file_path = f"test-{file_id}.txt"

# Contenido de prueba
content = f"Prueba de subida - {time.time()}".encode()

# Probar subida
print(f"\nProbando subida de archivo a {bucket_name}/{file_path}...")

# Método 1: Con parámetros extendidos
try:
    print("Método 1: API reciente...")
    result = supabase.storage.from_(bucket_name).upload(
        path=file_path,
        file=content,
        file_options={"content-type": "text/plain"}
    )
    print(f"✅ Éxito con método 1: {result}")
    upload_success = True
except Exception as e1:
    print(f"❌ Error método 1: {e1}")

    # Método 2: Versión simple
    try:
        print("Método 2: API simple...")
        result = supabase.storage.from_(bucket_name).upload(file_path, content)
        print(f"✅ Éxito con método 2: {result}")
        upload_success = True
    except Exception as e2:
        print(f"❌ Error método 2: {e2}")
        upload_success = False

# Verificar que se haya subido correctamente
if upload_success:
    # Intentar obtener URL
    try:
        print("\nObteniendo URL pública...")
        url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        print(f"✅ URL pública: {url}")

        # Verificar que la URL sea accesible
        print("\n¿La URL es accesible en el navegador? Revísala manualmente.")
    except Exception as e:
        print(f"❌ Error al obtener URL pública: {e}")

        # Intentar con URL firmada
        try:
            print("Intentando con URL firmada...")
            url_info = supabase.storage.from_(bucket_name).create_signed_url(file_path, 3600)

            # Extraer URL según formato devuelto
            if isinstance(url_info, dict) and 'signedURL' in url_info:
                url = url_info['signedURL']
            else:
                url = str(url_info)

            print(f"✅ URL firmada: {url}")
        except Exception as e2:
            print(f"❌ Error al obtener URL firmada: {e2}")

    # Eliminar archivo de prueba
    try:
        print("\nEliminando archivo de prueba...")
        supabase.storage.from_(bucket_name).remove([file_path])
        print("✅ Archivo eliminado correctamente")
    except Exception as e:
        print(f"❌ Error al eliminar con lista: {e}")

        # Intentar método alternativo
        try:
            supabase.storage.from_(bucket_name).remove(file_path)
            print("✅ Archivo eliminado con método alternativo")
        except Exception as e2:
            print(f"❌ Error al eliminar con método alternativo: {e2}")
else:
    print("❌ No se pudo subir el archivo")

print("\n==== Instrucciones para solucionar problemas ====\n")
print("1. Verifica que las URLs de las imágenes estén siendo almacenadas correctamente en la tabla 'imagenes'")
print("2. Confirma que los permisos del bucket están configurados como públicos en Supabase Dashboard")
print("3. Asegúrate de que la API key tenga permisos para operaciones de storage")
print("4. Comprueba que la versión de supabase sea compatible (v1.0.3 recomendada)")
