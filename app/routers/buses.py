from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from datetime import datetime

router = APIRouter()

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