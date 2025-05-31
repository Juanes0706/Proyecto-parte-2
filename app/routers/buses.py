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
# Importar nuestra utilidad para convertir IDs
from ..utils.id_converter import parse_id, is_valid_id

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
    """Crea un nuevo bus con un enfoque simplificado para resolver errores"""
    try:
        # Convertimos a booleano
        esta_activo_bool = esta_activo.lower() == "true"

        # Crear datos básicos del bus SIN ID - será generado por la secuencia en Supabase
        bus_data = {
            "nombre": nombre,
            "tipo": tipo,
            "esta_activo": esta_activo_bool,
            "imagen_url": None  # Establecer explícitamente como NULL
        }

        print(f"Creando bus con datos: {bus_data}")

        # Insertar el bus y dejar que Supabase genere el ID automáticamente
        result, error = supabase.table("buses").insert(bus_data).execute()

        if error:
            print(f"Error al insertar bus: {error}")
            raise HTTPException(status_code=400, detail=str(error))

        # Obtener el ID numérico generado por la base de datos
        bus_id = result[1][0]["id"]
        print(f"Bus creado con ID: {bus_id}")

        # Si el bus se creó correctamente y hay imagen, procesarla después
        if imagen:
            try:
                print(f"Procesando imagen: {imagen.filename}")
                # Verificar si la imagen tiene contenido
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
                    except Exception as e2:
                        print(f"Error al crear bucket {bucket_name}: {str(e2)}")

                # Simplificar la subida de imágenes y usar la tabla de imagenes
                extension = os.path.splitext(imagen.filename)[1] if '.' in imagen.filename else '.jpg'
                file_name = f"{uuid.uuid4()}{extension}"

                # Usar ruta con ID del bus para organizar imágenes
                file_path = f"{bus_id}/{file_name}"
                print(f"Intentando subir archivo a {bucket_name}/{file_path}")
            except Exception as e:
                print(f"Error al procesar imagen: {str(e)}")
                # Continuar con el flujo normal

            try:
                # Subir la imagen al bucket
                result = supabase.storage.from_(bucket_name).upload(file_path, contents)
                print(f"Resultado de subida: {result}")
                imagen_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
                print(f"URL de imagen generada: {imagen_url}")

                # Crear registro en la tabla imagenes en lugar de actualizar buses
                imagen_data = {
                    "url": imagen_url,
                    "bus_id": bus_id,  # Asociar con el bus
                    "created_at": datetime.utcnow().isoformat()
                }

                print(f"Guardando imagen en la tabla imagenes: {imagen_data}")
                imagen_result, imagen_error = supabase.table("imagenes").insert(imagen_data).execute()

                if imagen_error:
                    print(f"Error al guardar en tabla imagenes: {imagen_error}")
                    # No interrumpir la respuesta, el bus y la imagen ya existen
            except Exception as img_error:
                print(f"Error procesando imagen: {img_error}")
                # Continuar sin imagen

        # Respuesta básica si no hay imagen o hubo error al procesarla
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

@router.get("/buses/edit", include_in_schema=False)
async def buses_edit_page(request: Request):
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

@router.get("/api/buses")
async def listar_buses(
        tipo: Optional[str] = None,
        esta_activo: Optional[bool] = None,
        supabase=Depends(get_db)
):
    # Seleccionamos todos los buses con sus imágenes asociadas
    query = supabase.table("buses").select("*, imagenes(*)")

    # Si hay created_at en la tabla, ordenamos por él
    try:
        query = query.order("created_at")
    except Exception:
        # Si hay un error, probablemente created_at no es ordenable o no existe
        pass

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
            print(f"Error al procesar imágenes en listar_buses: {e}")
            bus["imagen_url"] = None

    return buses

@router.post("/api/buses/{bus_id}/estaciones/{estacion_id}")
async def asociar_estacion(
        bus_id: str,
        estacion_id: str,
        supabase=Depends(get_db)
):
    # Convertir bus_id usando parse_id
    bus_id_int = parse_id(bus_id)
    if bus_id_int is None:
        raise HTTPException(status_code=400, detail="ID de bus inválido")

    # Comprobar si estacion_id es un UUID y convertirlo a bigint
    if '-' in estacion_id:
        try:
            # Convertir el UUID a un entero (bigint)
            import uuid
            estacion_id_int = int(uuid.UUID(estacion_id).int & (1<<63)-1)
            # La tabla bus_estacion tiene: bus_id, estacion_id, created_at (automático)
            data = {
                "bus_id": bus_id_int,
                "estacion_id": estacion_id_int  # Usar el valor convertido
            }
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="ID de estación inválido")
    else:
        # Si no parece un UUID, intentar usarlo como está (podría ser ya un entero)
        try:
            data = {
                "bus_id": bus_id_int,
                "estacion_id": int(estacion_id)  # Asegurar que sea un entero
            }
        except ValueError:
            raise HTTPException(status_code=400, detail="ID de estación debe ser un número")

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
        bus_id: str,
        estacion_id: str,
        supabase=Depends(get_db)
):
    # Convertir bus_id usando parse_id
    bus_id_int = parse_id(bus_id)
    if bus_id_int is None:
        raise HTTPException(status_code=400, detail="ID de bus inválido")

    # Eliminamos la relación entre el bus y la estación
    try:
        # Comprobar si estacion_id es un UUID y convertirlo a bigint
        if '-' in estacion_id:
            try:
                # Convertir el UUID a un entero (bigint)
                import uuid
                estacion_id_int = int(uuid.UUID(estacion_id).int & (1<<63)-1)
                # Usar el valor convertido
                estacion_id_param = estacion_id_int
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="ID de estación inválido")
        else:
            # Si no parece un UUID, intentar usarlo como está (podría ser ya un entero)
            try:
                estacion_id_param = int(estacion_id)  # Asegurar que sea un entero
            except ValueError:
                raise HTTPException(status_code=400, detail="ID de estación debe ser un número")

        result, error = (
            supabase.table("bus_estacion")
            .delete()
            .eq("bus_id", bus_id_int)
            .eq("estacion_id", estacion_id_param)
            .execute()
        )

        if error:
            raise HTTPException(status_code=400, detail=str(error))

        return {"message": "Estación desasociada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/buses/{bus_id}/imagen")
async def subir_imagen_bus(
        bus_id: str,
        imagen: UploadFile = File(...),
        supabase=Depends(get_db)
):
    """Sube una imagen para un bus existente"""
    try:
        # Convertir bus_id usando parse_id
        bus_id_int = parse_id(bus_id)
        if bus_id_int is None:
            raise HTTPException(status_code=400, detail="ID de bus inválido")

        # Verificar que el bus existe
        bus_data, bus_error = (
            supabase.table("buses")
            .select("id")
            .eq("id", bus_id_int)
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
        # La ruta ahora solo necesita el ID del bus y nombre del archivo
        # ya que estamos usando un bucket específico para buses
        file_path = f"{bus_id_int}/{nombre_archivo}"

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
            # Intentar subir la imagen al bucket específico
            supabase.storage.from_(bucket_name).upload(file_path, contents)
            print(f"Imagen subida correctamente a '{bucket_name}/{file_path}'")

            # Obtener URL pública del bucket específico
            url = supabase.storage.from_(bucket_name).get_public_url(file_path)

            # Crear un registro en la tabla imagenes en lugar de actualizar buses
            imagen_data = {
                "url": url,
                "bus_id": bus_id_int,
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
            "recomendación": "Ejecuta el script scripts/inicializar_tablas.py para verificar la estructura"
        }

@router.get("/api/buses/{bus_id}")
async def obtener_bus(
        bus_id: str,
        supabase=Depends(get_db)
):
    """Obtiene los detalles de un bus específico"""
    try:
        # Convertir bus_id usando parse_id
        bus_id_int = parse_id(bus_id)
        if bus_id_int is None:
            raise HTTPException(status_code=400, detail="ID de bus inválido")

        # Seleccionar el bus y sus imágenes asociadas de la tabla imagenes
        data, error = (
            supabase.table("buses")
            .select("*, imagenes(*)")
            .eq("id", bus_id_int)
            .execute()
        )

        if error:
            raise HTTPException(status_code=400, detail=str(error))

        if not data[1]:
            raise HTTPException(status_code=404, detail="Bus no encontrado")

        # Extraer datos del bus y procesar imágenes desde la relación
        bus = data[1][0]

        # Añadir URL de la primera imagen como imagen_url para mantener compatibilidad
        try:
            # Verificar si hay imágenes asociadas
            if "imagenes" in bus and bus["imagenes"]:
                # Usar la primera imagen como principal
                primera_imagen = bus["imagenes"][0]
                bus["imagen_url"] = primera_imagen["url"]
            else:
                bus["imagen_url"] = None
        except Exception as e:
            print(f"Error al procesar imágenes para el bus: {e}")
            bus["imagen_url"] = None

        return bus
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/buses/{bus_id}")
async def eliminar_bus(
        bus_id: str,
        supabase=Depends(get_db)
):
    """Elimina un bus y todos sus recursos asociados"""
    try:
        # Convertir bus_id usando parse_id
        bus_id_int = parse_id(bus_id)
        if bus_id_int is None:
            raise HTTPException(status_code=400, detail="ID de bus inválido")

        # Primero eliminar relaciones con estaciones
        supabase.table("bus_estacion").delete().eq("bus_id", bus_id_int).execute()

        # Obtener y eliminar imágenes asociadas al bus
        imagenes, img_error = (
            supabase.table("imagenes")
            .select("*")
            .eq("bus_id", bus_id_int)
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
                    supabase.storage.from_(bucket_name).remove([f"{bus_id_int}/{file_name}"])
                except Exception as e:
                    print(f"Error eliminando archivo de {bucket_name}: {e}")

        # Eliminar registros de imágenes
        supabase.table("imagenes").delete().eq("bus_id", bus_id_int).execute()

        # Finalmente eliminar el bus
        data, error = supabase.table("buses").delete().eq("id", bus_id_int).execute()

        if error:
            raise HTTPException(status_code=400, detail=str(error))

        if not data[1]:
            raise HTTPException(status_code=404, detail="Bus no encontrado")

        return {"message": "Bus eliminado correctamente"}
    except Exception as e:
        print(f"Error al eliminar bus: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
