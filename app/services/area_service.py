from app.models import Area
from app.repositories import AreaRepository
from app.services.base_service import BaseService


class AreaService(BaseService[Area, AreaRepository]):
    """
    Servicio para lógica de negocio de Area.
    Hereda operaciones CRUD de BaseService.
    """
    repository = AreaRepository
    
    @classmethod
    def actualizar_campos(cls, area_existente: Area, area: Area):
        """Actualiza solo el campo nombre de Area."""
        area_existente.nombre = area.nombre
    
