from app.models import Alumno
from app.repositories.base_repository import BaseRepository


class AlumnoRepository(BaseRepository[Alumno]):
    """
    Repositorio para operaciones de base de datos de Alumno.
    Hereda operaciones CRUD de BaseRepository.
    """
    model = Alumno
