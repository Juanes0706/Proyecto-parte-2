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
        print("Iniciando verificación de storage...")
        supabase = get_db()

        print(f"Conectado a Supabase: {supabase_url}")

        # Verificar que el cliente se inicializó correctamente
        try:
            # Prueba de conexión simple
            buckets = supabase.storage.list_buckets()
            print(f"Buckets existentes: {buckets}")
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
                    supabase.storage.create_bucket(bucket["name"], options={"public": True})
                    print(f"✓ Bucket '{bucket['name']}' creado correctamente")
                except Exception as create_error:
                    print(f"✗ Error al crear bucket '{bucket['name']}': {str(create_error)}")

        return True, supabase_url, supabase_key
    except Exception as e:
        print(f"Error general en inicializar_storage: {str(e)}")
        return False, None, None