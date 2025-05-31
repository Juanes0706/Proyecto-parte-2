import os
import time
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from .. import database
from supabase import create_client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

router = APIRouter()

def get_db():
    return database.get_db()

@router.get("/api/debug/reparar-storage")
async def reparar_storage(supabase=Depends(get_db)):
    """Endpoint para diagnosticar y reparar problemas de storage"""
    result = {
        "status": "success",
        "message": "Diagnóstico completo",
        "tests": [],
    }

    # 1. Verificar buckets
    try:
        buckets = supabase.storage.list_buckets()
        bucket_names = []
        for bucket in buckets:
            try:
                if hasattr(bucket, 'name'):
                    name = bucket.name
                elif hasattr(bucket, 'id'):
                    name = bucket.id
                elif isinstance(bucket, dict) and 'name' in bucket:
                    name = bucket['name']
                else:
                    name = str(bucket)
                bucket_names.append(name)
            except Exception as e:
                bucket_names.append(f"Error: {str(e)}")

        result["tests"].append({
            "name": "listar_buckets",
            "status": "success",
            "data": bucket_names
        })
    except Exception as e:
        result["tests"].append({
            "name": "listar_buckets",
            "status": "error",
            "message": str(e)
        })

    # 2. Verificar tabla imagenes
    try:
        img_data, img_error = supabase.table("imagenes").select("*").limit(0).execute()
        if img_error:
            result["tests"].append({
                "name": "tabla_imagenes",
                "status": "error",
                "message": str(img_error)
            })
        else:
            result["tests"].append({
                "name": "tabla_imagenes",
                "status": "success",
                "message": "Tabla imagenes existe y es accesible"
            })
    except Exception as e:
        result["tests"].append({
            "name": "tabla_imagenes",
            "status": "error",
            "message": str(e)
        })

    # 3. Probar upload a storage
    bucket_name = "buses-imagenes"
    file_path = f"test-{uuid.uuid4()}.txt"
    file_content = f"Test content {time.time()}".encode()

    try:
        # Intentar subir archivo
        upload_success = False
        upload_method = ""
        upload_error = ""

        # Método 1
        try:
            result1 = supabase.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": "text/plain"}
            )
            upload_success = True
            upload_method = "method1"
        except Exception as e1:
            upload_error = f"Método 1: {str(e1)}"

            # Método 2
            try:
                result2 = supabase.storage.from_(bucket_name).upload(file_path, file_content)
                upload_success = True
                upload_method = "method2"
            except Exception as e2:
                upload_error += f", Método 2: {str(e2)}"

        if upload_success:
            result["tests"].append({
                "name": "upload_file",
                "status": "success",
                "message": f"Archivo subido exitosamente con {upload_method}"
            })

            # Obtener URL
            url = ""
            url_method = ""
            try:
                url = supabase.storage.from_(bucket_name).get_public_url(file_path)
                url_method = "public_url"
            except Exception as e1:
                try:
                    url_info = supabase.storage.from_(bucket_name).create_signed_url(file_path, 3600)
                    if isinstance(url_info, dict) and 'signedURL' in url_info:
                        url = url_info['signedURL']
                    else:
                        url = str(url_info)
                    url_method = "signed_url"
                except Exception as e2:
                    url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_path}"
                    url_method = "manual"

            result["tests"].append({
                "name": "get_url",
                "status": "success",
                "message": f"URL obtenida con {url_method}",
                "data": url
            })

            # Eliminar archivo
            try:
                supabase.storage.from_(bucket_name).remove([file_path])
                result["tests"].append({
                    "name": "remove_file",
                    "status": "success",
                    "message": "Archivo eliminado con método lista"
                })
            except Exception as e1:
                try:
                    supabase.storage.from_(bucket_name).remove(file_path)
                    result["tests"].append({
                        "name": "remove_file",
                        "status": "success",
                        "message": "Archivo eliminado con método directo"
                    })
                except Exception as e2:
                    result["tests"].append({
                        "name": "remove_file",
                        "status": "error",
                        "message": f"Error al eliminar: {str(e2)}"
                    })
        else:
            result["tests"].append({
                "name": "upload_file",
                "status": "error",
                "message": upload_error
            })
    except Exception as e:
        result["tests"].append({
            "name": "storage_test",
            "status": "error",
            "message": str(e)
        })

    # 4. Arreglo automático: Probar crear función para insertar imágenes
    try:
        # Crear o actualizar la función para insertar imágenes
        sql_funcion = """
        CREATE OR REPLACE FUNCTION insert_imagen_for_bus(bus_id_in BIGINT, url_in TEXT)
        RETURNS VOID AS $$
        BEGIN
            INSERT INTO imagenes (bus_id, url, created_at)
            VALUES (bus_id_in, url_in, NOW());
        END;
        $$ LANGUAGE plpgsql;
        """

        # Ejecutar el SQL
        try:
            rpc_result, rpc_error = supabase.rpc("insert_imagen_for_bus", {"bus_id_in": 1, "url_in": "test"}).execute()

            # Si hay error al ejecutar la función, intentar crearla
            if rpc_error:
                result["tests"].append({
                    "name": "crear_funcion",
                    "status": "info",
                    "message": "Se intentará crear la función insert_imagen_for_bus"
                })
            else:
                result["tests"].append({
                    "name": "funcion_existente",
                    "status": "success",
                    "message": "La función insert_imagen_for_bus ya existe"
                })
        except Exception:
            # La función probablemente no existe, intentamos crearla
            result["tests"].append({
                "name": "crear_funcion",
                "status": "info",
                "message": "La función no existe, se intentará crear"
            })

        # Como no podemos ejecutar SQL directo con Supabase JS, debemos usar otra estrategia
        # En un caso real, lo haríamos en la consola SQL de Supabase o con pg_client directo
    except Exception as e:
        result["tests"].append({
            "name": "test_funcion",
            "status": "error",
            "message": str(e)
        })

    return result

@router.get("/api/debug/tablas")
async def verificar_tablas(supabase=Depends(get_db)):
    """Endpoint para verificar la estructura de las tablas"""
    result = {
        "status": "success",
        "tables": {},
        "storage": {}
    }

    # 1. Verificar tabla buses
    try:
        bus_data, bus_error = supabase.table("buses").select("*").limit(1).execute()
        if bus_error:
            result["tables"]["buses"] = {
                "status": "error",
                "message": str(bus_error)
            }
        else:
            columns = []
            if bus_data and len(bus_data) > 1 and bus_data[1] and len(bus_data[1]) > 0:
                columns = list(bus_data[1][0].keys())

            result["tables"]["buses"] = {
                "status": "success",
                "columns": columns,
                "count": len(bus_data[1]) if bus_data and len(bus_data) > 1 else 0
            }
    except Exception as e:
        result["tables"]["buses"] = {
            "status": "error",
            "message": str(e)
        }

    # 2. Verificar tabla imagenes
    try:
        img_data, img_error = supabase.table("imagenes").select("*").limit(1).execute()
        if img_error:
            result["tables"]["imagenes"] = {
                "status": "error",
                "message": str(img_error)
            }
        else:
            columns = []
            if img_data and len(img_data) > 1 and img_data[1] and len(img_data[1]) > 0:
                columns = list(img_data[1][0].keys())

            result["tables"]["imagenes"] = {
                "status": "success",
                "columns": columns,
                "count": len(img_data[1]) if img_data and len(img_data) > 1 else 0
            }
    except Exception as e:
        result["tables"]["imagenes"] = {
            "status": "error",
            "message": str(e)
        }

    # 3. Verificar storage
    try:
        buckets = supabase.storage.list_buckets()
        bucket_list = []

        for bucket in buckets:
            try:
                if hasattr(bucket, 'name'):
                    name = bucket.name
                elif hasattr(bucket, 'id'):
                    name = bucket.id
                elif isinstance(bucket, dict) and 'name' in bucket:
                    name = bucket['name']
                else:
                    name = str(bucket)
                bucket_list.append(name)
            except:
                pass

        result["storage"]["buckets"] = bucket_list

        # Prueba de subida mínima
        test_bucket = "buses-imagenes"
        if test_bucket in bucket_list:
            file_path = f"test-{uuid.uuid4()}.txt"
            file_content = b"Test content"

            try:
                # Intentar subir con método 1
                supabase.storage.from_(test_bucket).upload(
                    path=file_path,
                    file=file_content,
                    file_options={"content-type": "text/plain"}
                )
                result["storage"]["upload_test"] = "success_method1"
            except Exception as e1:
                try:
                    # Intentar con método 2
                    supabase.storage.from_(test_bucket).upload(file_path, file_content)
                    result["storage"]["upload_test"] = "success_method2"
                except Exception as e2:
                    result["storage"]["upload_test"] = "error"
                    result["storage"]["upload_error"] = f"M1: {str(e1)}, M2: {str(e2)}"

            # Limpiar si se subió correctamente
            if result["storage"].get("upload_test", "").startswith("success"):
                try:
                    supabase.storage.from_(test_bucket).remove([file_path])
                except:
                    try:
                        supabase.storage.from_(test_bucket).remove(file_path)
                    except:
                        pass
    except Exception as e:
        result["storage"]["status"] = "error"
        result["storage"]["message"] = str(e)

    return result
