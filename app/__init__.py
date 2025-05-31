from .database import get_db
# Importar los módulos completos en lugar de router específicos
from . import routers

__version__ = "1.0.0"

__all__ = [
    'get_db',
    'routers'
]