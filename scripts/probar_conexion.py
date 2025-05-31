import os
from dotenv import load_dotenv
from supabase import create_client
import sys

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales de Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print("==== Verificación de conexión a Supabase ====\n")
print(f"URL: {supabase_url}")
print(f"API Key: {supabase_key[:10]}..." if supabase_key else "No configurada")

if not supabase_url or not supabase_key:
    print("\n❌ Error: No se encontraron las credenciales de Supabase")
    print("   Asegúrate de tener el archivo .env con SUPABASE_URL y SUPABASE_KEY correctos")
    sys.exit(1)

try:
    # Crear cliente de Supabase
    print("\nIntentando conectar a Supabase...")
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Conexión a Supabase establecida correctamente")

    # Probar consulta a la tabla buses
    print("\nConsultando tabla buses...")
    data, error = supabase.table("buses").select("*").limit(1).execute()

    if error:
        print(f"❌ Error al consultar tabla buses: {error}")
    else:
        count = len(data[1])
        print(f"✅ Consulta exitosa. Se encontraron {count} registros.")
        if count > 0:
            print(f"   Primer registro: {data[1][0]}")

    # Probar acceso a storage
    print("\nListando buckets de storage...")
    try:
        buckets = supabase.storage.list_buckets()
        print(f"✅ Se encontraron {len(buckets)} buckets:")
        for bucket in buckets:
            try:
                name = bucket.name if hasattr(bucket, 'name') else bucket
                print(f"   - {name}")
            except:
                print(f"   - {bucket}")
    except Exception as e:
        print(f"❌ Error al listar buckets: {str(e)}")

    print("\n✅ Verificación completada con éxito")
    print("   La conexión a Supabase funciona correctamente")

except Exception as e:
    print(f"\n❌ Error de conexión: {str(e)}")
    print("   Verifica que las credenciales sean correctas y que Supabase esté disponible")
    sys.exit(1)
