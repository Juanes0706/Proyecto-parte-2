import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# URL base de la API (usar Render si está disponible)
base_url = os.getenv("API_URL", "https://tu-app-en-render.onrender.com")
print(f"Usando URL de API: {base_url}")

def debug_crear_bus():
    """Función para probar la creación de buses sin imágenes"""
    url = f"{base_url}/api/buses"

    # Datos básicos del bus sin imagen
    data = {
        "nombre": "Bus de Prueba Debug",
        "tipo": "Alimentador",
        "esta_activo": "true"
    }

    print(f"Enviando solicitud a {url} con datos: {data}")

    try:
        # Realizar la solicitud sin imagen
        response = requests.post(url, data=data)

        # Imprimir la respuesta completa
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta: {response.text}")

        if response.status_code == 200:
            print("✅ Bus creado exitosamente sin imagen")
            return True
        else:
            print(f"❌ Error al crear bus: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Excepción al crear bus: {str(e)}")
        return False

def listar_buckets():
    """Función para listar buckets de Supabase"""
    from supabase import create_client

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ Variables de entorno de Supabase no configuradas")
        return

    try:
        supabase = create_client(url, key)
        buckets = supabase.storage.list_buckets()

        print("\n==== Buckets disponibles ====")
        for bucket in buckets:
            try:
                # Intenta acceder como atributo (versión nueva)
                bucket_name = bucket.name if hasattr(bucket, 'name') else str(bucket)
                print(f"- {bucket_name}")
            except Exception as attr_err:
                # Si falla, muestra el objeto completo
                print(f"- {str(bucket)}")

        # Intentar crear un bucket de prueba
        bucket_name = "debug-test-bucket"
        try:
            supabase.storage.create_bucket(bucket_name, {"public": True})
            print(f"✅ Bucket '{bucket_name}' creado para pruebas")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️ El bucket '{bucket_name}' ya existe")
            else:
                print(f"❌ Error al crear bucket: {str(e)}")

        # Subir un archivo pequeño
        try:
            file_content = b"Test de storage"
            file_path = "test.txt"

            print(f"\nSubiendo archivo al bucket '{bucket_name}'...")
            # Intenta diferentes métodos de upload según la versión de API
            try:
                # Método para versiones más recientes
                result = supabase.storage.from_(bucket_name).upload(
                    path=file_path,
                    file=file_content,
                    file_options={"content-type": "text/plain"}
                )
            except Exception as e1:
                print(f"Método 1 falló: {e1}")
                # Método para versiones anteriores
                result = supabase.storage.from_(bucket_name).upload(file_path, file_content)

            print(f"✅ Archivo subido: {result}")

            # Obtener URL pública (manejo múltiples versiones)
            try:
                url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            except Exception as e1:
                print(f"get_public_url falló: {e1}")
                # Alternativa: URL firmada
                url_info = supabase.storage.from_(bucket_name).create_signed_url(file_path, 3600)
                url = url_info['signedURL'] if isinstance(url_info, dict) and 'signedURL' in url_info else str(url_info)

            print(f"✅ URL pública: {url}")

            # Intentar eliminar el archivo (manejo múltiples versiones)
            try:
                # Método para versiones más recientes (lista de rutas)
                supabase.storage.from_(bucket_name).remove([file_path])
            except Exception as e1:
                print(f"Método remove con lista falló: {e1}")
                # Método para versiones anteriores (ruta directa)
                supabase.storage.from_(bucket_name).remove(file_path)

            print(f"✅ Archivo eliminado correctamente")

        except Exception as e:
            print(f"❌ Error en operaciones de archivo: {str(e)}")
            print(f"Tipo de error: {type(e).__name__}")

    except Exception as e:
        print(f"❌ Error al conectar con Supabase: {str(e)}")

if __name__ == "__main__":
    print("==== Diagnóstico de creación de buses ====\n")
    debug_crear_bus()

    print("\n==== Diagnóstico de Supabase Storage ====\n")
    listar_buckets()
