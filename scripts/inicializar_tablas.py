import os
import logging
from supabase import create_client
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

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

    # Imprimir información de depuración
    print("\n===== INFORMACIÓN DE TABLAS EN SUPABASE =====\n")

    # Listar todas las tablas
    try:
        # Usar una consulta de SQL para obtener las tablas existentes
        response = supabase.table('buses').select('*').limit(1).execute()
        print(f"Prueba de conexión a tabla 'buses': {response}")

        # Intentar imprimir la estructura de la tabla buses
        try:
            # Ejecutar SQL para obtener la estructura de la tabla
            sql = """SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'buses' AND table_schema = 'public';"""
            # Esta es una función más avanzada que podría no estar disponible en todas las versiones
            print("Intentando obtener la estructura de la tabla 'buses'...")
            # Aquí no podemos ejecutar SQL directo con el cliente Python, solo mostraremos mensaje
            print("Para verificar la estructura de la tabla, debes revisar en el panel de Supabase")
        except Exception as e:
            print(f"No se pudo obtener la estructura de la tabla: {e}")
    except Exception as e:
        print(f"Error al intentar acceder a las tablas: {e}")

    print("\n===== VERIFICANDO ESTRUCTURA NECESARIA =====\n")
    print("La tabla 'buses' debe tener las siguientes columnas:")
    print("- id (UUID): Identificador único del bus")
    print("- nombre (TEXT): Nombre del bus")
    print("- tipo (TEXT): Tipo de bus")
    print("- esta_activo (BOOLEAN): Indica si el bus está activo")
    print("- created_at (TIMESTAMP): Fecha de creación (generado automáticamente)")
    print("- updated_at (TIMESTAMP): Fecha de actualización (generado automáticamente)")

    print("\nLa tabla 'imagenes' debe tener las siguientes columnas:")
    print("- id (UUID): Identificador único de la imagen")
    print("- url (TEXT): URL de la imagen")
    print("- bus_id (UUID): Referencia al bus (puede ser NULL)")
    print("- estacion_id (UUID): Referencia a la estación (puede ser NULL)")
    print("- created_at (TIMESTAMP): Fecha de creación (generado automáticamente)")

    print("\n===== EJEMPLO DE SQL PARA CREAR LAS TABLAS =====\n")

    print("Para crear la tabla 'buses':")
    buses_sql = """
    CREATE TABLE IF NOT EXISTS public.buses (
        id UUID PRIMARY KEY,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        esta_activo BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    print(buses_sql)

    print("\nPara crear la tabla 'imagenes':")
    imagenes_sql = """
    CREATE TABLE IF NOT EXISTS public.imagenes (
        id UUID PRIMARY KEY,
        url TEXT NOT NULL,
        bus_id UUID REFERENCES public.buses(id) ON DELETE CASCADE,
        estacion_id UUID REFERENCES public.estaciones(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        CHECK (bus_id IS NOT NULL OR estacion_id IS NOT NULL)
    );
    """
    print(imagenes_sql)

    print("\n===== INSTRUCCIONES =====\n")
    print("1. Abre el panel de Supabase y ve a la sección 'SQL Editor'")
    print("2. Ejecuta las consultas SQL mostradas arriba para crear o modificar las tablas")
    print("3. Verifica que las tablas tengan la estructura correcta")
    print("4. Una vez que las tablas estén correctamente configuradas, vuelve a ejecutar la aplicación")

if __name__ == "__main__":
    main()
