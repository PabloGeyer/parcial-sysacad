from app.models import Cargo
from app.repositories.base_repository import BaseRepository


class CargoRepository(BaseRepository[Cargo]):
    """
    Repositorio para operaciones de base de datos de Cargo.
    Hereda operaciones CRUD de BaseRepository.
    """
    model = Cargo
