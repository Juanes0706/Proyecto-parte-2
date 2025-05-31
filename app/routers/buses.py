from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile
from ..database import get_db
from datetime import datetime
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/buses", include_in_schema=False)
async def buses_page(request: Request):
    return templates.TemplateResponse(
        "buses.html",
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