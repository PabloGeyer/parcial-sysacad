from app.models import Cargo
from app.repositories import CargoRepository
from app.services.base_service import BaseService


class CargoService(BaseService[Cargo, CargoRepository]):
    """
    Servicio para lógica de negocio de Cargo.
    Hereda operaciones CRUD de BaseService.
    """
    repository = CargoRepository
    
    @classmethod
    def actualizar_campos(cls, cargo_existente: Cargo, cargo: Cargo):
        """Actualiza los campos específicos de Cargo."""
        cargo_existente.nombre = cargo.nombre
        cargo_existente.puntos = cargo.puntos
        cargo_existente.categoria_cargo = cargo.categoria_cargo
        cargo_existente.tipo_dedicacion = cargo.tipo_dedicacion
