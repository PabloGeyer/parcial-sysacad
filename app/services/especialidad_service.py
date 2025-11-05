from app.models import Especialidad
from app.repositories import EspecialidadRepository

class EspecialidadService:

    @staticmethod
    def crear(especialidad):
        EspecialidadRepository.crear(especialidad)

    @staticmethod
    def buscar_por_id(id: int) -> Especialidad:
        return EspecialidadRepository.buscar_por_id(id)
    
    @staticmethod
    def buscar_todos() -> list[Especialidad]:
        return EspecialidadRepository.buscar_todos()

    @staticmethod
    def actualizar(id: int, especialidad: Especialidad) -> Especialidad:
        especialidad_existente = EspecialidadRepository.buscar_por_id(id)
        if not especialidad_existente:
            return None
        especialidad_existente.nombre = especialidad.nombre
        especialidad_existente.letra = especialidad.letra
        especialidad_existente.observacion = especialidad.observacion
        especialidad_existente.tipoespecialidad = especialidad.tipoespecialidad
        especialidad_existente.facultad = especialidad.facultad
        return EspecialidadRepository.actualizar(especialidad_existente)
    
    @staticmethod
    def borrar_por_id(id: int) -> bool:
        return EspecialidadRepository.borrar_por_id(id)

    @staticmethod
    def buscar_alumnos_por_especialidad(especialidad_id: int) -> dict:
        """
        Retorna todos los alumnos de una especialidad junto con los datos
        de la facultad a la que pertenece.
        
        Returns:
            dict con estructura:
            {
                'especialidad': {...},
                'facultad': {...},
                'alumnos': [...]
            }
        """
        # SRP: Delegar búsqueda al repositorio
        especialidad = EspecialidadRepository.buscar_por_id(especialidad_id)
        
        if not especialidad:
            return None
        
        # Obtener alumnos de la especialidad
        alumnos = EspecialidadRepository.buscar_alumnos_por_especialidad(especialidad_id)
        
        # KISS: Construir respuesta simple y clara
        return {
            'especialidad': {
                'id': especialidad.id,
                'hashid': especialidad.hashid,
                'nombre': especialidad.nombre,
                'letra': especialidad.letra,
                'observacion': especialidad.observacion
            },
            'facultad': {
                'id': especialidad.facultad.id,
                'hashid': especialidad.facultad.hashid,
                'nombre': especialidad.facultad.nombre,
                'abreviatura': especialidad.facultad.abreviatura,
                'sigla': especialidad.facultad.sigla,
                'universidad': {
                    'id': especialidad.facultad.universidad.id,
                    'hashid': especialidad.facultad.universidad.hashid,
                    'nombre': especialidad.facultad.universidad.nombre,
                    'sigla': especialidad.facultad.universidad.sigla
                }
            },
            'alumnos': [
                {
                    'id': alumno.id,
                    'hashid': alumno.hashid,
                    'nombre': alumno.nombre,
                    'apellido': alumno.apellido,
                    'nrodocumento': alumno.nrodocumento,
                    'nro_legajo': alumno.nro_legajo,
                    'sexo': alumno.sexo,
                    'fecha_nacimiento': alumno.fecha_nacimiento.isoformat(),
                    'fecha_ingreso': alumno.fecha_ingreso.isoformat()
                }
                for alumno in alumnos
            ]
        }
