from app.models import Area
from app.repositories.base_repository import BaseRepository


class AreaRepository(BaseRepository[Area]):
    """
    Repositorio para operaciones de base de datos de Area.
    Hereda operaciones CRUD de BaseRepository.
    """
    model = Area
