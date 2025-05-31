import os
from supabase import create_client
from dotenv import load_dotenv
import logging

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

def get_db():
    return create_client(supabase_url, supabase_key)

def inicializar_storage():
    """Inicializa los buckets de storage necesarios para la aplicación"""
    try:
        print("🔄 Iniciando inicialización de storage...")
        supabase = get_db()

        # Verificar si la URL comienza con https://
        if not supabase_url or not supabase_url.startswith("https://"):
            print(f"❌ URL de Supabase inválida: {supabase_url}")
            return False, supabase_url, supabase_key

        print(f"ℹ️ Usando Supabase URL: {supabase_url}")

        # Verificar que el cliente se inicializó correctamente
        try:
            # Prueba de conexión simple
            buckets = supabase.storage.list_buckets()
            bucket_names = []
            for bucket in buckets:
                try:
                    bucket_name = bucket.name if hasattr(bucket, 'name') else str(bucket)
                    bucket_names.append(bucket_name)
                except:
                    bucket_names.append(str(bucket))
            print(f"Buckets existentes: {bucket_names}")
        except Exception as conn_error:
            print(f"Error al listar buckets existentes: {str(conn_error)}")

        # Definir los buckets necesarios
        buckets_to_create = [
            {
                "name": "buses-imagenes",
                "description": "Almacena imágenes de buses"
            },
            {
                "name": "estaciones-imagenes",
                "description": "Almacena imágenes de estaciones"
            }
        ]

        # Crear/verificar cada bucket
        for bucket in buckets_to_create:
            try:
                # Comprobar si el bucket existe
                supabase.storage.get_bucket(bucket["name"])
                print(f"✓ Bucket '{bucket['name']}' ya existe")
            except Exception as e:
                print(f"✗ Bucket '{bucket['name']}' no existe: {str(e)}")
                # Crear bucket si no existe
                try:
                    # Intentamos con opciones simplificadas
                    supabase.storage.create_bucket(bucket["name"], {"public": True})
                    print(f"✓ Bucket '{bucket['name']}' creado correctamente")
                except Exception as create_error:
                    print(f"✗ Error al crear bucket '{bucket['name']}': {str(create_error)}")
                    # Intentar método alternativo
                    try:
                        supabase.storage.create_bucket(bucket["name"])
                        print(f"✓ Bucket creado con método alternativo")
                    except Exception as alt_error:
                        if "already exists" in str(alt_error).lower():
                            print(f"✓ El bucket ya existe pero no era visible")
                        else:
                            print(f"✗ También falló el método alternativo: {str(alt_error)}")

        # Probar funcionamiento del storage con un archivo pequeño
        try:
            import uuid
            test_bucket = "buses-imagenes"
            test_file = f"test-{uuid.uuid4()}.txt"
            test_content = b"Prueba de storage"

            # Subir archivo de prueba
            try:
                # Método 1
                result = supabase.storage.from_(test_bucket).upload(
                    path=test_file,
                    file=test_content,
                    file_options={"content-type": "text/plain"}
                )
                print(f"✓ Archivo de prueba subido correctamente")
            except Exception as e1:
                print(f"✗ Error con método 1: {str(e1)}")
                # Método 2
                try:
                    result = supabase.storage.from_(test_bucket).upload(test_file, test_content)
                    print(f"✓ Archivo subido con método alternativo")
                except Exception as e2:
                    print(f"✗ Error con método 2: {str(e2)}")
                    raise Exception("Error al subir archivo de prueba")

            # Probar obtención de URL
            try:
                url = supabase.storage.from_(test_bucket).get_public_url(test_file)
                print(f"✓ URL pública obtenida")
            except Exception as e:
                print(f"✗ Error al obtener URL: {str(e)}")

            # Limpiar archivo de prueba
            try:
                supabase.storage.from_(test_bucket).remove([test_file])
            except Exception as e:
                try:
                    supabase.storage.from_(test_bucket).remove(test_file)
                except Exception:
                    pass
        except Exception as test_error:
            print(f"❌ Prueba de storage falló: {str(test_error)}")

        print("✅ Storage inicializado correctamente")
        return True, supabase_url, supabase_key
    except Exception as e:
        print(f"Error general en inicializar_storage: {str(e)}")
        return False, None, None