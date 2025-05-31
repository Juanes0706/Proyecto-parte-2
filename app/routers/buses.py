from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form
from ..database import get_db
from datetime import datetime
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from pydantic import BaseModel
import uuid
import os
import shutil

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
    bus_id = str(uuid.uuid4())
    image_path = None

    if imagen:
        ext = os.path.splitext(imagen.filename)[1]
        image_filename = f"{bus_id}{ext}"
        image_dir = "static/img"
        os.makedirs(image_dir, exist_ok=True)
        image_path = os.path.join(image_dir, image_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

    esta_activo_bool = esta_activo.lower() == "true"

    data = {
        "id": bus_id,
        "nombre": nombre,
        "tipo": tipo,
        "esta_activo": esta_activo_bool,
        "created_at": datetime.utcnow().isoformat(),
        "imagen_url": image_path if image_path else None
    }
    result, error = supabase.table("buses").insert(data).execute()
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"message": "Bus creado correctamente", "bus_id": bus_id}

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
    query = supabase.table("buses").select("*, imagenes(*)").order("created_at")

    if tipo:
        query = query.eq("tipo", tipo)
    if esta_activo is not None:
        query = query.eq("esta_activo", esta_activo)

    data, error = query.execute()

    if error:
        raise HTTPException(status_code=400, detail=str(error))

    return data[1]

@router.post("/api/buses/{bus_id}/estaciones/{estacion_id}")
async def asociar_estacion(
        bus_id: str,
        estacion_id: str,
        supabase=Depends(get_db)
):
    data = {
        "bus_id": bus_id,
        "estacion_id": estacion_id,
        "created_at": datetime.utcnow().isoformat()
    }

    result, error = (
        supabase.table("bus_estacion")
        .insert(data)
        .execute()  # Aquí faltaba el paréntesis
    )

    if error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"message": "Estación asociada correctamente"}


@router.delete("/api/buses/{bus_id}/estaciones/{estacion_id}")
async def desasociar_estacion(
        bus_id: str,
        estacion_id: str,
        supabase=Depends(get_db)
):
    pass