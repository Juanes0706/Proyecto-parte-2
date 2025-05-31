from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form
from ..database import get_db
from datetime import datetime
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from pydantic import BaseModel
import uuid
import os
import shutil
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/api/buses")
async def crear_bus(
    nombre: str = Form(...),
    tipo: str = Form(...),
    esta_activo: str = Form(...),
    imagen: UploadFile = File(None),
    supabase=Depends(get_db)
):
    """Crea un nuevo bus utilizando la tabla imagenes para las fotos"""
    try:
        # Generar ID único para el bus
        bus_id = str(uuid.uuid4())
        # Convertir string a booleano
        esta_activo_bool = esta_activo.lower() == "true"

        # Datos básicos del bus (sin imagen_url)
        bus_data = {
            "id": bus_id,
            "nombre": nombre,
            "tipo": tipo,
            "esta_activo": esta_activo_bool,
            "created_at": datetime.utcnow().isoformat()
        }

        print(f"Creando bus con datos: {bus_data}")

        # Insertar el bus
        result, error = supabase.table("buses").insert(bus_data).execute()

        if error:
            print(f"Error al insertar bus: {error}")
            raise HTTPException(status_code=400, detail=str(error))

        # Si el bus se creó correctamente y hay imagen, procesarla
        imagen_url = None
        if imagen:
            try:
                print(f"Procesando imagen: {imagen.filename}")
                # Leer contenido de la imagen
                contents = await imagen.read()
                print(f"Tamaño de la imagen: {len(contents)} bytes")

                bucket_name = "buses-imagenes"

                # Intentar obtener o crear el bucket
                try:
                    supabase.storage.get_bucket(bucket_name)
                    print(f"Bucket {bucket_name} existe")
                except Exception as e:
                    print(f"Bucket {bucket_name} no existe: {str(e)}")
                    try:
                        supabase.storage.create_bucket(bucket_name, options={"public": True})
                        print(f"Bucket {bucket_name} creado exitosamente")
                    except Exception as e:
                        print(f"Error al crear bucket {bucket_name}: {str(e)}")

                # Generar nombre de archivo único
                extension = os.path.splitext(imagen.filename)[1] if '.' in imagen.filename else '.jpg'
                file_name = f"{uuid.uuid4()}{extension}"
                file_path = f"{bus_id}/{file_name}"

                print(f"Subiendo archivo a {bucket_name}/{file_path}")

                # Subir imagen al bucket
                supabase.storage.from_(bucket_name).upload(file_path, contents)
                imagen_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
                print(f"URL de imagen generada: {imagen_url}")

                # Crear registro en la tabla imagenes
                imagen_data = {
                    "url": imagen_url,
                    "bus_id": bus_id,
                    "created_at": datetime.utcnow().isoformat()
                }

                # Insertar en tabla imagenes
                imagen_result, imagen_error = supabase.table("imagenes").insert(imagen_data).execute()

                if imagen_error:
                    print(f"Error al insertar en tabla imagenes: {imagen_error}")
                    # No interrumpir la respuesta, el bus ya se creó

            except Exception as img_error:
                print(f"Error procesando imagen: {img_error}")
                # Continuar sin imagen

        # Respuesta con o sin imagen
        if imagen_url:
            return {"message": "Bus creado con imagen", "bus_id": bus_id, "imagen_url": imagen_url}
        else:
            return {"message": "Bus creado correctamente", "bus_id": bus_id}

    except Exception as e:
        print(f"Error general al crear bus: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/buses", include_in_schema=False)
async def buses_page(request: Request):
    return templates.TemplateResponse(
        "buses.html",
        {"request": request}
    )

@router.get("/buses/create", include_in_schema=False)
async def buses_create_page(request: Request):
    return templates.TemplateResponse(
        "buses_create.html",
        {"request": request}
    )

@router.get("/buses/crear", include_in_schema=False)
async def buses_crear_page(request: Request):
    return templates.TemplateResponse(
        "buses_create.html",
        {"request": request}
    )

@router.get("/buses/edit", include_in_schema=False)
async def buses_edit_page(request: Request):
    return templates.TemplateResponse(
        "buses_edit.html",
        {"request": request}
    )

@router.get("/buses/editar", include_in_schema=False)
async def buses_editar_page(request: Request):
    return templates.TemplateResponse(
        "buses_edit.html",
        {"request": request}
    )

@router.get("/buses/delete", include_in_schema=False)
async def buses_delete_page(request: Request):
    return templates.TemplateResponse(
        "buses_delete.html",
        {"request": request}
    )

@router.get("/buses/eliminar", include_in_schema=False)
async def buses_eliminar_page(request: Request):
    return templates.TemplateResponse(
        "buses_delete.html",
        {"request": request}
    )

@router.get("/api/buses")
async def listar_buses(
        tipo: Optional[str] = None,
        esta_activo: Optional[bool] = None,
        supabase=Depends(get_db)
):
    # Seleccionar buses con sus imágenes asociadas
    query = supabase.table("buses").select("*, imagenes(*)").order("created_at")

    if tipo:
        query = query.eq("tipo", tipo)
    if esta_activo is not None:
        query = query.eq("esta_activo", esta_activo)

    data, error = query.execute()

    if error:
        raise HTTPException(status_code=400, detail=str(error))

    # Procesar buses para añadir campo imagen_url basado en la primera imagen
    buses = data[1]
    for bus in buses:
        try:
            # Si el bus tiene imágenes, usar la primera como imagen_url
            if "imagenes" in bus and bus["imagenes"]:
                bus["imagen_url"] = bus["imagenes"][0]["url"]
            else:
                bus["imagen_url"] = None
        except Exception as e:
            print(f"Error al procesar imágenes: {e}")
            bus["imagen_url"] = None

    return buses

@router.post("/api/buses/{bus_id}/estaciones/{estacion_id}")
async def asociar_estacion(
                bus_id: int,
        estacion_id: str,
        supabase=Depends(get_db)
):
    # La tabla bus_estacion tiene: bus_id, estacion_id, created_at (automático)
    data = {
        "bus_id": bus_id,
        "estacion_id": estacion_id
    }

    try:
        result, error = (
            supabase.table("bus_estacion")
            .insert(data)
            .execute()
        )

        if error:
            raise HTTPException(status_code=400, detail=str(error))

        return {"message": "Estación asociada correctamente"}
    except Exception as e:
        print(f"Error al asociar estación: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/buses/{bus_id}/estaciones/{estacion_id}")
async def desasociar_estacion(
        bus_id: int,
        estacion_id: int,
        supabase=Depends(get_db)
):
    # Eliminamos la relación entre el bus y la estación
    try:
        result, error = (
            supabase.table("bus_estacion")
            .delete()
            .eq("bus_id", bus_id)
            .eq("estacion_id", estacion_id)
            .execute()
        )

        if error:
            raise HTTPException(status_code=400, detail=str(error))

        return {"message": "Estación desasociada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/buses/{bus_id}/imagen")
async def subir_imagen_bus(
        bus_id: int,
        imagen: UploadFile = File(...),
        supabase=Depends(get_db)
):
    """Sube una imagen para un bus existente"""
    try:
        # Verificar que el bus existe
        bus_data, bus_error = (
            supabase.table("buses")
            .select("id")
            .eq("id", bus_id)
            .execute()
        )

        if bus_error:
            raise HTTPException(status_code=400, detail=str(bus_error))

        if not bus_data[1]:
            raise HTTPException(status_code=404, detail="Bus no encontrado")

        # Leer contenido de la imagen
        contents = await imagen.read()

        # Generar un nombre único para la imagen
        extension = os.path.splitext(imagen.filename)[1]
        nombre_archivo = f"{uuid.uuid4()}{extension}"
        file_path = f"{bus_id}/{nombre_archivo}"

        bucket_name = "buses-imagenes"

        try:
            # Comprobar si existe el bucket
            supabase.storage.get_bucket(bucket_name)
        except Exception as e:
            print(f"Error al acceder al bucket '{bucket_name}': {e}")
            # Intentar crear el bucket si no existe
            try:
                supabase.storage.create_bucket(
                    bucket_name,
                    options={"public": True}
                )
                print(f"Bucket '{bucket_name}' creado correctamente")
            except Exception as bucket_error:
                print(f"Error al crear bucket '{bucket_name}': {bucket_error}")
                raise HTTPException(status_code=500, detail="Error al configurar el almacenamiento")

        # Subir imagen a Supabase Storage
        try:
            # Subir la imagen al bucket específico
            supabase.storage.from_(bucket_name).upload(file_path, contents)
            print(f"Imagen subida correctamente a '{bucket_name}/{file_path}'")

            # Obtener URL pública del bucket específico
            url = supabase.storage.from_(bucket_name).get_public_url(file_path)

            # Crear registro en la tabla imagenes
            imagen_data = {
                "url": url,
                "bus_id": bus_id,
                "created_at": datetime.utcnow().isoformat()
            }

            # Insertar en la tabla imagenes
            imagen_result, imagen_error = supabase.table("imagenes").insert(imagen_data).execute()

            if imagen_error:
                print(f"Error al insertar en tabla imagenes: {imagen_error}")
                raise HTTPException(status_code=400, detail=str(imagen_error))

            return {"message": "Imagen subida correctamente", "url": url}
        except Exception as storage_error:
            print(f"Error al subir imagen a storage: {storage_error}")
            raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(storage_error)}")
    except Exception as e:
        print(f"Error general al subir imagen: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/buses/{bus_id}")
async def obtener_bus(
        bus_id: int,
        supabase=Depends(get_db)
):
    """Obtiene los detalles de un bus específico con sus imágenes"""
    try:
        # Seleccionar bus con sus imágenes asociadas
        data, error = (
            supabase.table("buses")
            .select("*, imagenes(*)")
            .eq("id", bus_id)
            .execute()
        )

        if error:
            raise HTTPException(status_code=400, detail=str(error))

        if not data[1]:
            raise HTTPException(status_code=404, detail="Bus no encontrado")

        # Añadir imagen_url como primera imagen para compatibilidad
        bus = data[1][0]
        try:
            if "imagenes" in bus and bus["imagenes"]:
                bus["imagen_url"] = bus["imagenes"][0]["url"]
            else:
                bus["imagen_url"] = None
        except Exception as e:
            print(f"Error al procesar imágenes: {e}")
            bus["imagen_url"] = None

        return bus
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/buses/{bus_id}")
async def eliminar_bus(
        bus_id: int,
        supabase=Depends(get_db)
):
    """Elimina un bus y todos sus recursos asociados"""
    try:
        # Primero eliminar relaciones con estaciones
        supabase.table("bus_estacion").delete().eq("bus_id", bus_id).execute()

        # Obtener y eliminar imágenes asociadas al bus
        imagenes, img_error = (
            supabase.table("imagenes")
            .select("*")
            .eq("bus_id", bus_id)
            .execute()
        )

        if not img_error and imagenes[1]:
            # Eliminar archivos del bucket específico de buses
            bucket_name = "buses-imagenes"
            for imagen in imagenes[1]:
                try:
                    # Extraer solo el nombre del archivo de la URL
                    path_parts = imagen["url"].split("/")
                    file_name = path_parts[-1]
                    # La ruta ahora es solo bus_id/nombre_archivo
                    supabase.storage.from_(bucket_name).remove([f"{bus_id}/{file_name}"])
                except Exception as e:
                    print(f"Error eliminando archivo de {bucket_name}: {e}")

        # Eliminar registros de imágenes
        supabase.table("imagenes").delete().eq("bus_id", bus_id).execute()

        # Finalmente eliminar el bus
        data, error = supabase.table("buses").delete().eq("id", bus_id).execute()

        if error:
            raise HTTPException(status_code=400, detail=str(error))

        if not data[1]:
            raise HTTPException(status_code=404, detail="Bus no encontrado")

        return {"message": "Bus eliminado correctamente"}
    except Exception as e:
        print(f"Error al eliminar bus: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/debug/tablas")
async def verificar_tablas(
        supabase=Depends(get_db)
):
    """Endpoint de depuración para verificar la estructura de las tablas"""
    try:
        # Intentar leer un registro de cada tabla principal
        buses, buses_error = supabase.table("buses").select("*").limit(1).execute()
        imagenes, imagenes_error = supabase.table("imagenes").select("*").limit(1).execute()

        return {
            "mensaje": "Información de depuración de tablas",
            "tablas": {
                "buses": {
                    "error": str(buses_error) if buses_error else None,
                    "campos_disponibles": list(buses[1][0].keys()) if buses[1] else []
                },
                "imagenes": {
                    "error": str(imagenes_error) if imagenes_error else None,
                    "campos_disponibles": list(imagenes[1][0].keys()) if imagenes[1] else []
                }
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "mensaje": "No se pudo obtener información de las tablas",
            "recomendación": "Ejecuta el script migrations/add_imagenes_table.sql para verificar la estructura"
        }
