"""
Servicio base genérico para operaciones CRUD.
Implementa el principio DRY eliminando código duplicado en todos los servicios.
"""
from typing import TypeVar, Generic, Type, List, Optional

T = TypeVar('T')
R = TypeVar('R')


class BaseService(Generic[T, R]):
    """
    Servicio base que proporciona operaciones CRUD genéricas.
    
    Uso:
        class AlumnoService(BaseService[Alumno, AlumnoRepository]):
            repository = AlumnoRepository
            
            def actualizar_campos(self, existente, nuevo):
                existente.nombre = nuevo.nombre
                existente.apellido = nuevo.apellido
                # ... otros campos específicos
    """
    
    repository: Type[R] = None
    
    @classmethod
    def crear(cls, entity: T) -> T:
        """Crea una nueva entidad."""
        return cls.repository.crear(entity)
    
    @classmethod
    def buscar_por_id(cls, id: int) -> Optional[T]:
        """Busca una entidad por su ID."""
        return cls.repository.buscar_por_id(id)
    
    @classmethod
    def buscar_todos(cls) -> List[T]:
        """Retorna todas las entidades."""
        return cls.repository.buscar_todos()
    
    @classmethod
    def actualizar(cls, id: int, entity: T) -> Optional[T]:
        """
        Actualiza una entidad existente.
        Subclases deben implementar actualizar_campos() para especificar qué campos actualizar.
        """
        existente = cls.repository.buscar_por_id(id)
        if not existente:
            return None
        
        # Llamar al método que actualiza campos específicos
        cls.actualizar_campos(existente, entity)
        
        return cls.repository.actualizar(existente)
    
    @classmethod
    def actualizar_campos(cls, existente: T, nuevo: T):
        """
        Método a sobrescribir en subclases para especificar qué campos actualizar.
        Por defecto, copia todos los atributos excepto 'id'.
        """
        for attr, value in nuevo.__dict__.items():
            if attr not in ['_sa_instance_state', 'id'] and not attr.startswith('_'):
                setattr(existente, attr, value)
    
    @classmethod
    def borrar_por_id(cls, id: int) -> bool:
        """Elimina una entidad por su ID."""
        return cls.repository.borrar_por_id(id)
