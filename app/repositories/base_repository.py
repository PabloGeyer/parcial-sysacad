"""
Repositorio base genérico para operaciones CRUD.
Implementa el principio DRY eliminando código duplicado en todos los repositorios.
"""
from typing import TypeVar, Generic, Type, List, Optional
from app import db

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Repositorio base que proporciona operaciones CRUD genéricas.
    
    Uso:
        class AlumnoRepository(BaseRepository[Alumno]):
            model = Alumno
    """
    
    model: Type[T] = None
    
    @classmethod
    def crear(cls, entity: T) -> T:
        """Crea una nueva entidad en la base de datos."""
        db.session.add(entity)
        db.session.commit()
        return entity
    
    @classmethod
    def buscar_por_id(cls, id: int) -> Optional[T]:
        """Busca una entidad por su ID."""
        return db.session.query(cls.model).filter_by(id=id).first()
    
    @classmethod
    def buscar_todos(cls) -> List[T]:
        """Retorna todas las entidades."""
        return db.session.query(cls.model).all()
    
    @classmethod
    def actualizar(cls, entity: T) -> T:
        """Actualiza una entidad existente."""
        db.session.merge(entity)
        db.session.commit()
        return entity
    
    @classmethod
    def borrar_por_id(cls, id: int) -> bool:
        """Elimina una entidad por su ID."""
        entity = cls.buscar_por_id(id)
        if not entity:
            return False
        db.session.delete(entity)
        db.session.commit()
        return True
    
    @classmethod
    def borrar(cls, entity: T) -> bool:
        """Elimina una entidad."""
        if not entity:
            return False
        db.session.delete(entity)
        db.session.commit()
        return True
