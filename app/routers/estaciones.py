from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from typing import List, Optional
from ..database import get_db
from datetime import datetime
import uuid
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/estaciones", include_in_schema=False)
async def estaciones_page(request: Request):
    return templates.TemplateResponse(
        "estaciones.html",
        {"request": request}
    )


@router.post("/api/estaciones")
async def crear_estacion(
        nombre: str,
        localidad: str,
        esta_activo: bool = True,
        imagenes: List[UploadFile] = File(...),
        supabase=Depends(get_db)
):
    estacion_data = {
        "nombre": nombre,
        "localidad": localidad,
        "esta_activo": esta_activo,
        "created_at": datetime.utcnow().isoformat()
    }

    data, error = supabase.table("estaciones").insert(estacion_data).execute()
    if error:
        raise HTTPException(status_code=400, detail=str(error))

    estacion_id = data[1][0]["id"]
    imagenes_urls = []

    bucket_name = "estaciones-imagenes"

    for imagen in imagenes:
        contents = await imagen.read()
        # Usar una ruta más simple dentro del bucket específico
        file_path = f"{estacion_id}/{imagen.filename}"

        # Subir imagen al bucket específico de estaciones
        supabase.storage.from_(bucket_name).upload(file_path, contents)
        url = supabase.storage.from_(bucket_name).get_public_url(file_path)

        imagen_data = {
            "url": url,
            "estacion_id": estacion_id,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("imagenes").insert(imagen_data).execute()
        imagenes_urls.append(url)

    return {**estacion_data, "imagenes": imagenes_urls}


@router.get("/api/estaciones")
async def listar_estaciones(
        localidad: Optional[str] = None,
        esta_activo: Optional[bool] = None,
        supabase=Depends(get_db)
):
    query = supabase.table("estaciones").select("*, imagenes(*)").order("created_at")

    if localidad:
        query = query.eq("localidad", localidad)
    if esta_activo is not None:
        query = query.eq("esta_activo", esta_activo)

    data, error = query.execute()

    if error:
        raise HTTPException(status_code=400, detail=str(error))

    return data[1]


@router.get("/api/estaciones/{estacion_id}")
async def obtener_estacion(
        estacion_id: str,
        supabase=Depends(get_db)
):
    data, error = (
        supabase.table("estaciones")
        .select("*, imagenes(*), buses!bus_estacion(*)")
        .eq("id", estacion_id)
        .execute()
    )

    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not data[1]:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    return data[1][0]


@router.put("/api/estaciones/{estacion_id}")
async def actualizar_estacion(
        estacion_id: str,
        nombre: Optional[str] = None,
        localidad: Optional[str] = None,
        esta_activo: Optional[bool] = None,
        imagenes: Optional[List[UploadFile]] = File(None),
        supabase=Depends(get_db)
):
    update_data = {
        "updated_at": datetime.utcnow().isoformat()
    }

    if nombre is not None:
        update_data["nombre"] = nombre
    if localidad is not None:
        update_data["localidad"] = localidad
    if esta_activo is not None:
        update_data["esta_activo"] = esta_activo

    # Actualizar datos de la estación
    data, error = (
        supabase.table("estaciones")
        .update(update_data)
        .eq("id", estacion_id)
        .execute()
    )

    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not data[1]:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    # Procesar nuevas imágenes si se proporcionaron
    if imagenes:
        imagenes_urls = []
        bucket_name = "estaciones-imagenes"

        for imagen in imagenes:
            contents = await imagen.read()
            # Usar una ruta más simple dentro del bucket específico
            file_path = f"{estacion_id}/{imagen.filename}"

            supabase.storage.from_(bucket_name).upload(file_path, contents)
            url = supabase.storage.from_(bucket_name).get_public_url(file_path)

            imagen_data = {
                "url": url,
                "estacion_id": estacion_id,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.table("imagenes").insert(imagen_data).execute()
            imagenes_urls.append(url)

        data[1][0]["nuevas_imagenes"] = imagenes_urls

    return data[1][0]


@router.delete("/api/estaciones/{estacion_id}")
async def eliminar_estacion(
        estacion_id: str,
        supabase=Depends(get_db)
):
    # Eliminar asociaciones con buses
    supabase.table("bus_estacion").delete().eq("estacion_id", estacion_id).execute()

    # Obtener y eliminar imágenes
    imagenes, error = (
        supabase.table("imagenes")
        .select("url")
        .eq("estacion_id", estacion_id)
        .execute()
    )

    if error:
        raise HTTPException(status_code=400, detail=str(error))

    # Eliminar archivos del bucket específico de estaciones
    bucket_name = "estaciones-imagenes"
    for imagen in imagenes[1]:
        try:
            file_path = imagen["url"].split("/")[-1]
            supabase.storage.from_(bucket_name).remove([f"{estacion_id}/{file_path}"])
        except Exception as e:
            print(f"Error eliminando archivo: {e}")

    # Eliminar registros de imágenes
    supabase.table("imagenes").delete().eq("estacion_id", estacion_id).execute()

    # Eliminar la estación
    data, error = supabase.table("estaciones").delete().eq("id", estacion_id).execute()

    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not data[1]:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    return {"message": "Estación eliminada correctamente"}


@router.delete("/api/estaciones/{estacion_id}/imagenes/{imagen_id}")
async def eliminar_imagen_estacion(
        estacion_id: str,
        imagen_id: str,
        supabase=Depends(get_db)
):
    # Obtener la imagen
    imagen, error = (
        supabase.table("imagenes")
        .select("url")
        .eq("id", imagen_id)
        .eq("estacion_id", estacion_id)
        .execute()
    )

    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not imagen[1]:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # Eliminar archivo del bucket específico de estaciones
    bucket_name = "estaciones-imagenes"
    try:
        file_path = imagen[1][0]["url"].split("/")[-1]
        supabase.storage.from_(bucket_name).remove([f"{estacion_id}/{file_path}"])
    except Exception as e:
        print(f"Error eliminando archivo: {e}")

    # Eliminar registro de la imagen
    data, error = (
        supabase.table("imagenes")
        .delete()
        .eq("id", imagen_id)
        .execute()
    )

    if error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"message": "Imagen eliminada correctamente"}


@router.get("/api/estaciones/{estacion_id}/buses")
async def listar_buses_estacion(
        estacion_id: str,
        supabase=Depends(get_db)
):
    data, error = (
        supabase.table("buses")
        .select("*")
        .eq("bus_estacion.estacion_id", estacion_id)
        .execute()
    )

    if error:
        raise HTTPException(status_code=400, detail=str(error))

    return data[1]


@router.get("/api/estaciones/localidades")
async def listar_localidades(
        supabase=Depends(get_db)
):
    data, error = (
        supabase.table("estaciones")
        .select("localidad")
        .execute()
    )

    if error:
        raise HTTPException(status_code=400, detail=str(error))

    # Obtener lista única de localidades
    localidades = list(set(item["localidad"] for item in data[1]))
    return sorted(localidades)