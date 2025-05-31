import os
import json
import uuid
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

    # Datos de prueba para crear un bus
    bus_id = str(uuid.uuid4())
    test_data = {
        "id": bus_id,
        "nombre": "Bus de prueba",
        "tipo": "Urbano",
        "esta_activo": True
    }

    print(f"\nIntentando insertar bus con datos: {json.dumps(test_data, indent=2)}")

    try:
        # Intentar insertar un bus de prueba
        result, error = supabase.table("buses").insert(test_data).execute()

        if error:
            print(f"\n❌ Error al insertar bus: {error}")
            print("\n🔍 Analizando el error...")

            if "imagen_url" in str(error):
                print("\nEl error está relacionado con la columna 'imagen_url' que no existe en la tabla.")
                print("\nPosibles soluciones:")
                print("1. Añadir la columna 'imagen_url' a la tabla 'buses' en Supabase:")
                print("""
   ALTER TABLE public.buses ADD COLUMN imagen_url TEXT;""")

                print("\n2. O modificar tu código para que no intente usar esta columna")
                print("   Revisa app/routers/buses.py y asegúrate de que estás enviando solo las columnas existentes")
        else:
            print(f"\n✅ Bus insertado correctamente con ID: {bus_id}")
            print("\nDatos insertados:")
            print(json.dumps(result[1][0], indent=2))

            # Eliminar el bus de prueba
            supabase.table("buses").delete().eq("id", bus_id).execute()
            print("\n✅ Bus de prueba eliminado correctamente")
    except Exception as e:
        print(f"\n❌ Excepción al crear bus: {str(e)}")
        print("\nRecomendaciones:")
        print("1. Verifica la estructura de la tabla 'buses' en Supabase")
        print("2. Asegúrate de que tu código solo está enviando columnas que existen en la tabla")
        print("3. Comprueba que las credenciales de Supabase son correctas")

if __name__ == "__main__":
    main()
