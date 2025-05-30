from fastapi import APIRouter
from .buses import router as buses_router
from .estaciones import router as estaciones_router

# Configurar los routers
buses_router.tags = ["Buses"]
estaciones_router.tags = ["Estaciones"]

# Exportar los routers para que estén disponibles cuando se importe el paquete
__all__ = [
    'buses_router',
    'estaciones_router'
]