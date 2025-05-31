import os
from dotenv import load_dotenv
from supabase import create_client
import json

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

# Verificar estructura de tabla buses
try:
    print("\n==== Estructura de tabla buses ====\n")
    # Ejecutar SQL para obtener estructura
    query = """SELECT column_name, data_type, column_default 
               FROM information_schema.columns 
               WHERE table_name = 'buses' 
               ORDER BY ordinal_position"""

    data, error = supabase.table("buses").select("*").limit(0).execute()

    if error:
        print(f"❌ Error al consultar tabla buses: {error}")
    else:
        # Obtener nombres de columnas de la respuesta
        if data and len(data) > 0:
            columns = data[0]
            print("Columnas detectadas:")
            for col in columns:
                print(f"- {col}")
        else:
            print("No se pudieron detectar columnas automáticamente")

    # Ejecutar SQL directo para obtener más detalles
    result, error = supabase.rpc("debug_get_table_info", {"table_name": "buses"}).execute()

    if error:
        print(f"❌ Error al ejecutar RPC: {error}")
    else:
        if result and len(result) > 0 and result[1]:
            print("\nDetalles de columnas:")
            for column in result[1]:
                print(json.dumps(column, indent=2))
        else:
            print("No se pudo obtener información detallada de la tabla")

    # Probar inserción simple para validar estructura
    test_bus = {
        "nombre": "TEST-BUS-DEBUG",
        "tipo": "TEST",
        "esta_activo": True
    }

    print("\nRealizando inserción de prueba...")
    insert_result, insert_error = supabase.table("buses").insert(test_bus).execute()

    if insert_error:
        print(f"❌ Error al insertar: {insert_error}")
    else:
        print("✅ Inserción exitosa")
        print(f"Respuesta: {insert_result}")

        # Si la inserción fue exitosa, eliminar el registro de prueba
        if insert_result and len(insert_result) > 1 and insert_result[1] and len(insert_result[1]) > 0:
            try:
                test_id = insert_result[1][0]["id"]
                print(f"ID generado: {test_id}")

                # Eliminar registro de prueba
                delete_result, delete_error = supabase.table("buses").delete().eq("id", test_id).execute()
                if not delete_error:
                    print("✅ Registro de prueba eliminado correctamente")
                else:
                    print(f"❌ Error al eliminar registro de prueba: {delete_error}")
            except Exception as e:
                print(f"❌ Error al procesar ID: {e}")
        else:
            print("No se pudo obtener el ID del registro insertado")

except Exception as e:
    print(f"❌ Error general al verificar buses: {e}")

# Verificar estructura de tabla imagenes
try:
    print("\n==== Estructura de tabla imagenes ====\n")

    # Verificar si la tabla existe
    query = """SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'imagenes'
                )"""

    try:
        data, error = supabase.table("imagenes").select("*").limit(0).execute()
        if error:
            print(f"❌ La tabla imagenes no existe o hay un error: {error}")
        else:
            print("✅ La tabla imagenes existe")

            # Obtener detalles de columnas
            if data and len(data) > 0:
                columns = data[0]
                print("Columnas detectadas:")
                for col in columns:
                    print(f"- {col}")
    except Exception as e:
        print(f"❌ Error al verificar tabla imagenes: {e}")

    # Probar inserción simple para validar estructura
    try:
        test_imagen = {
            "url": "https://test-url.com/imagen-test.jpg",
            "bus_id": None  # Intencionalmente nulo para evitar restricciones de clave foránea
        }

        print("\nRealizando inserción de prueba en imagenes...")
        insert_result, insert_error = supabase.table("imagenes").insert(test_imagen).execute()

        if insert_error:
            print(f"❌ Error al insertar en imagenes: {insert_error}")
        else:
            print("✅ Inserción exitosa en imagenes")
            # Si la inserción fue exitosa, eliminar el registro de prueba
            if insert_result and len(insert_result) > 1 and insert_result[1] and len(insert_result[1]) > 0:
                try:
                    test_id = insert_result[1][0]["id"]
                    # Eliminar registro de prueba
                    supabase.table("imagenes").delete().eq("id", test_id).execute()
                    print("✅ Registro de prueba en imagenes eliminado")
                except Exception as e:
                    print(f"❌ Error al eliminar registro de prueba en imagenes: {e}")
    except Exception as e:
        print(f"❌ Error general al probar imagenes: {e}")

except Exception as e:
    print(f"❌ Error general al verificar imagenes: {e}")

# Probar operaciones de storage
try:
    print("\n==== Prueba de storage ====\n")

    bucket_name = "buses-imagenes"
    file_path = "debug-test-file.txt"
    file_content = b"Test content for storage debugging"

    # Verificar que el bucket existe
    try:
        bucket_info = supabase.storage.get_bucket(bucket_name)
        print(f"✅ Bucket '{bucket_name}' encontrado")
    except Exception as e:
        print(f"❌ Error al obtener bucket: {e}")
        # Intentar crear el bucket
        try:
            supabase.storage.create_bucket(bucket_name, {"public": True})
            print(f"✅ Bucket '{bucket_name}' creado")
        except Exception as e2:
            print(f"❌ Error al crear bucket: {e2}")

    # Subir archivo de prueba
    print(f"Subiendo archivo de prueba a {bucket_name}/{file_path}...")
    try:
        # Método 1
        result = supabase.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": "text/plain"}
        )
        print(f"✅ Archivo subido correctamente con método 1")
        upload_success = True
    except Exception as e1:
        print(f"❌ Error al subir con método 1: {e1}")
        try:
            # Método 2
            result = supabase.storage.from_(bucket_name).upload(file_path, file_content)
            print(f"✅ Archivo subido correctamente con método 2")
            upload_success = True
        except Exception as e2:
            print(f"❌ Error al subir con método 2: {e2}")
            upload_success = False

    # Verificar URL si la subida fue exitosa
    if upload_success:
        try:
            url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            print(f"✅ URL obtenida: {url}")
        except Exception as e:
            print(f"❌ Error al obtener URL: {e}")
            try:
                url_info = supabase.storage.from_(bucket_name).create_signed_url(file_path, 3600)
                if isinstance(url_info, dict) and 'signedURL' in url_info:
                    url = url_info['signedURL']
                else:
                    url = str(url_info)
                print(f"✅ URL firmada: {url}")
            except Exception as e2:
                print(f"❌ Error al obtener URL firmada: {e2}")

        # Crear registro en tabla imagenes con esta URL
        try:
            imagen_prueba = {
                "url": url,
                "bus_id": None  # Sin asociar a un bus específico
            }
            img_result, img_error = supabase.table("imagenes").insert(imagen_prueba).execute()
            if img_error:
                print(f"❌ Error al guardar URL en tabla imagenes: {img_error}")
            else:
                print("✅ URL guardada correctamente en tabla imagenes")
                # Eliminar registro de prueba
                if img_result and len(img_result) > 1 and img_result[1]:
                    try:
                        img_id = img_result[1][0]["id"]
                        supabase.table("imagenes").delete().eq("id", img_id).execute()
                    except Exception:
                        pass
        except Exception as e:
            print(f"❌ Error al probar inserción en tabla imagenes: {e}")

        # Limpiar archivo de prueba
        try:
            supabase.storage.from_(bucket_name).remove([file_path])
            print("✅ Archivo de prueba eliminado")
        except Exception as e:
            print(f"❌ Error al eliminar archivo: {e}")
            try:
                supabase.storage.from_(bucket_name).remove(file_path)
                print("✅ Archivo eliminado con método alternativo")
            except Exception as e2:
                print(f"❌ Error al eliminar con método alternativo: {e2}")

except Exception as e:
    print(f"❌ Error general en prueba de storage: {e}")

print("\n✨ Diagnóstico completado")
