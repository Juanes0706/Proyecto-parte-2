from fastapi import APIRouter, Depends, HTTPException
from .. import database
from datetime import datetime
import os
import uuid
import json

router = APIRouter()

def get_db():
    return database.get_db()

@router.get("/api/debug/diagnostico-imagen/{bus_id}")
async def diagnostico_imagen(bus_id: int, supabase=Depends(get_db)):
    """Endpoint para diagnosticar problemas de relación entre buses e imágenes"""
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "diagnostico": {
            "bus": {},
            "imagen": {},
            "storage": {}
        }
    }

    # 1. Verificar si el bus existe
    try:
        bus_data, bus_error = supabase.table("buses").select("*").eq("id", bus_id).execute()

        if bus_error:
            result["diagnostico"]["bus"]["status"] = "error"
            result["diagnostico"]["bus"]["message"] = str(bus_error)
        elif not bus_data or len(bus_data) < 2 or not bus_data[1] or len(bus_data[1]) == 0:
            result["diagnostico"]["bus"]["status"] = "not_found"
            result["diagnostico"]["bus"]["message"] = f"No se encontró bus con ID {bus_id}"
        else:
            # Bus encontrado
            bus = bus_data[1][0]
            result["diagnostico"]["bus"]["status"] = "found"
            result["diagnostico"]["bus"]["id"] = bus["id"]
            result["diagnostico"]["bus"]["nombre"] = bus["nombre"]
            result["diagnostico"]["bus"]["tipo"] = bus["tipo"]

            # Obtener el tipo de datos del ID
            result["diagnostico"]["bus"]["id_type"] = type(bus["id"]).__name__
    except Exception as e:
        result["diagnostico"]["bus"]["status"] = "error"
        result["diagnostico"]["bus"]["message"] = f"Error al buscar bus: {str(e)}"

    # 2. Verificar imágenes asociadas
    try:
        img_data, img_error = supabase.table("imagenes").select("*").eq("bus_id", bus_id).execute()

        if img_error:
            result["diagnostico"]["imagen"]["status"] = "error"
            result["diagnostico"]["imagen"]["message"] = str(img_error)
        elif not img_data or len(img_data) < 2 or not img_data[1] or len(img_data[1]) == 0:
            result["diagnostico"]["imagen"]["status"] = "not_found"
            result["diagnostico"]["imagen"]["message"] = f"No se encontraron imágenes para el bus {bus_id}"

            # Intentar crear una imagen de prueba
            try:
                # URL de prueba
                test_url = f"https://via.placeholder.com/150?text=Test+Bus+{bus_id}"

                # Datos para la imagen
                img_data = {
                    "url": test_url,
                    "bus_id": bus_id,
                    "created_at": datetime.now().isoformat()
                }

                img_result, img_error = supabase.table("imagenes").insert(img_data).execute()

                if img_error:
                    result["diagnostico"]["imagen"]["test_insert"] = {
                        "status": "error",
                        "message": str(img_error),
                        "type": type(img_error).__name__
                    }
                else:
                    result["diagnostico"]["imagen"]["test_insert"] = {
                        "status": "success",
                        "message": "Imagen de prueba creada exitosamente"
                    }
            except Exception as e:
                result["diagnostico"]["imagen"]["test_insert"] = {
                    "status": "error",
                    "message": f"Error al crear imagen de prueba: {str(e)}"
                }
        else:
            # Imágenes encontradas
            imagenes = img_data[1]
            result["diagnostico"]["imagen"]["status"] = "found"
            result["diagnostico"]["imagen"]["count"] = len(imagenes)
            result["diagnostico"]["imagen"]["urls"] = [img["url"] for img in imagenes]

            # Obtener el tipo de datos del bus_id en la tabla imagenes
            if imagenes and len(imagenes) > 0:
                result["diagnostico"]["imagen"]["bus_id_type"] = type(imagenes[0]["bus_id"]).__name__
    except Exception as e:
        result["diagnostico"]["imagen"]["status"] = "error"
        result["diagnostico"]["imagen"]["message"] = f"Error al buscar imágenes: {str(e)}"

    # 3. Verificar funcionamiento del storage
    try:
        bucket_name = "buses-imagenes"
        file_path = f"test-{uuid.uuid4()}.txt"
        file_content = f"Test content for bus {bus_id}".encode()

        # Intentar subir archivo
        try:
            # Método 1
            upload_result = supabase.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": "text/plain"}
            )

            result["diagnostico"]["storage"]["upload"] = {
                "status": "success",
                "method": "method1",
                "result": str(upload_result)
            }

            # Obtener URL
            try:
                url = supabase.storage.from_(bucket_name).get_public_url(file_path)
                result["diagnostico"]["storage"]["url"] = {
                    "status": "success",
                    "method": "public_url",
                    "url": url
                }
            except Exception as url_error:
                result["diagnostico"]["storage"]["url"] = {
                    "status": "error",
                    "message": str(url_error)
                }

                # Intentar con URL firmada
                try:
                    url_info = supabase.storage.from_(bucket_name).create_signed_url(file_path, 3600)
                    if isinstance(url_info, dict) and 'signedURL' in url_info:
                        url = url_info['signedURL']
                    else:
                        url = str(url_info)

                    result["diagnostico"]["storage"]["url"] = {
                        "status": "success",
                        "method": "signed_url",
                        "url": url
                    }
                except Exception as e2:
                    result["diagnostico"]["storage"]["url"]["signed_url_error"] = str(e2)

            # Crear registro en tabla imagenes con esta URL
            try:
                img_data = {
                    "url": url,
                    "bus_id": bus_id,
                    "created_at": datetime.now().isoformat()
                }

                img_result, img_error = supabase.table("imagenes").insert(img_data).execute()

                if img_error:
                    result["diagnostico"]["storage"]["imagen_insert"] = {
                        "status": "error",
                        "message": str(img_error)
                    }
                else:
                    result["diagnostico"]["storage"]["imagen_insert"] = {
                        "status": "success",
                        "message": "Imagen creada con URL de storage"
                    }
            except Exception as e:
                result["diagnostico"]["storage"]["imagen_insert"] = {
                    "status": "error",
                    "message": str(e)
                }

            # Eliminar archivo de prueba
            try:
                supabase.storage.from_(bucket_name).remove([file_path])
                result["diagnostico"]["storage"]["cleanup"] = "success"
            except Exception as e:
                try:
                    supabase.storage.from_(bucket_name).remove(file_path)
                    result["diagnostico"]["storage"]["cleanup"] = "success_alt"
                except Exception as e2:
                    result["diagnostico"]["storage"]["cleanup_error"] = str(e2)
        except Exception as upload_error:
            # Método 2
            try:
                upload_result = supabase.storage.from_(bucket_name).upload(file_path, file_content)

                result["diagnostico"]["storage"]["upload"] = {
                    "status": "success",
                    "method": "method2",
                    "result": str(upload_result)
                }

                # Limpiar
                try:
                    supabase.storage.from_(bucket_name).remove(file_path)
                except:
                    pass
            except Exception as e2:
                result["diagnostico"]["storage"]["upload"] = {
                    "status": "error",
                    "method1_error": str(upload_error),
                    "method2_error": str(e2)
                }
    except Exception as e:
        result["diagnostico"]["storage"]["status"] = "error"
        result["diagnostico"]["storage"]["message"] = str(e)

    # 4. Información sobre las tablas
    try:
        # Consultas para obtener información sobre las tablas
        buses_info = supabase.table("buses").select("*").limit(0).execute()
        imagenes_info = supabase.table("imagenes").select("*").limit(0).execute()

        result["tablas"] = {
            "buses": {
                "columns": list(buses_info[0].keys()) if buses_info and len(buses_info) > 0 else []
            },
            "imagenes": {
                "columns": list(imagenes_info[0].keys()) if imagenes_info and len(imagenes_info) > 0 else []
            }
        }
    except Exception as e:
        result["tablas_error"] = str(e)

    # 5. Recomendaciones basadas en el diagnóstico
    recommendations = []

    # Verificar si hay problemas con los tipos de datos
    if ("bus" in result["diagnostico"] and "id_type" in result["diagnostico"]["bus"] and
        "imagen" in result["diagnostico"] and "bus_id_type" in result["diagnostico"]["imagen"] and
        result["diagnostico"]["bus"]["id_type"] != result["diagnostico"]["imagen"]["bus_id_type"]):

        recommendations.append({
            "tipo": "tipo_datos",
            "mensaje": f"Incompatibilidad de tipos: buses.id es {result['diagnostico']['bus']['id_type']} pero imagenes.bus_id es {result['diagnostico']['imagen']['bus_id_type']}",
            "solucion": "Ejecutar el script compatibilidad_imagenes.sql para corregir los tipos de datos"
        })

    # Verificar si hay problemas con el storage
    if ("storage" in result["diagnostico"] and "upload" in result["diagnostico"]["storage"] and
        result["diagnostico"]["storage"]["upload"].get("status") == "error"):

        recommendations.append({
            "tipo": "storage",
            "mensaje": "Problemas al subir archivos al storage",
            "solucion": "Verificar permisos del bucket y credenciales de Supabase"
        })

    # Añadir recomendaciones al resultado
    result["recomendaciones"] = recommendations

    return result

@router.get("/api/debug/reparar-imagen/{bus_id}")
async def reparar_imagen(bus_id: int, supabase=Depends(get_db)):
    """Endpoint para intentar reparar problemas de imágenes para un bus"""
    # Verificar si el bus existe
    bus_data, bus_error = supabase.table("buses").select("*").eq("id", bus_id).execute()

    if bus_error or not bus_data or len(bus_data) < 2 or not bus_data[1] or len(bus_data[1]) == 0:
        raise HTTPException(status_code=404, detail=f"Bus con ID {bus_id} no encontrado")

    # Verificar si ya tiene imágenes
    img_data, img_error = supabase.table("imagenes").select("*").eq("bus_id", bus_id).execute()

    if not img_error and img_data and len(img_data) > 1 and img_data[1] and len(img_data[1]) > 0:
        # Ya tiene imágenes, verificar si son accesibles
        imagenes = img_data[1]
        valid_images = []
        invalid_images = []

        for img in imagenes:
            if "url" in img and img["url"] and img["url"].startswith("http"):
                valid_images.append(img)
            else:
                invalid_images.append(img)

        if len(valid_images) > 0:
            return {
                "status": "success",
                "message": f"El bus ya tiene {len(valid_images)} imágenes válidas",
                "valid_count": len(valid_images),
                "invalid_count": len(invalid_images)
            }

    # Si llegamos aquí, necesitamos crear una imagen para el bus
    # Subir una imagen de prueba
    try:
        bucket_name = "buses-imagenes"
        file_name = f"bus-{bus_id}-{uuid.uuid4()}.txt"
        file_content = f"Contenido de prueba para bus {bus_id}".encode()

        # Intentar subir el archivo
        try:
            upload_result = supabase.storage.from_(bucket_name).upload(
                path=file_name,
                file=file_content,
                file_options={"content-type": "text/plain"}
            )
        except Exception as e1:
            try:
                upload_result = supabase.storage.from_(bucket_name).upload(file_name, file_content)
            except Exception as e2:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error al subir archivo: {str(e1)}. Método alternativo: {str(e2)}"
                )

        # Obtener URL
        try:
            url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        except Exception as e1:
            try:
                url_info = supabase.storage.from_(bucket_name).create_signed_url(file_name, 31536000)  # 1 año
                if isinstance(url_info, dict) and 'signedURL' in url_info:
                    url = url_info['signedURL']
                else:
                    url = str(url_info)
            except Exception as e2:
                # Construir URL manualmente
                supabase_url = os.getenv("SUPABASE_URL")
                url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_name}"

        # Crear registro en tabla imagenes
        img_data = {
            "url": url,
            "bus_id": bus_id,
            "created_at": datetime.now().isoformat()
        }

        img_result, img_error = supabase.table("imagenes").insert(img_data).execute()

        if img_error:
            raise HTTPException(status_code=500, detail=f"Error al guardar imagen: {str(img_error)}")

        return {
            "status": "success",
            "message": "Imagen creada exitosamente",
            "url": url,
            "image_id": img_result[1][0]["id"] if img_result and len(img_result) > 1 and img_result[1] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error general: {str(e)}")
