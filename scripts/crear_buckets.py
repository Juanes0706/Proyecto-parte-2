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
