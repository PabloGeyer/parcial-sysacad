import datetime
from io import BytesIO
from app.models import Alumno
from app.repositories import AlumnoRepository
from app.services.documentos_office_service import obtener_tipo_documento
from app.services.base_service import BaseService


class AlumnoService(BaseService[Alumno, AlumnoRepository]):
    """
    Servicio para lógica de negocio de Alumno.
    Hereda operaciones CRUD de BaseService y agrega funcionalidad específica.
    """
    repository = AlumnoRepository
    
    @classmethod
    def actualizar_campos(cls, alumno_existente: Alumno, alumno: Alumno):
        """Actualiza los campos específicos de Alumno."""
        alumno_existente.nombre = alumno.nombre
        alumno_existente.apellido = alumno.apellido
        alumno_existente.nrodocumento = alumno.nrodocumento
        alumno_existente.tipo_documento = alumno.tipo_documento
        alumno_existente.fecha_nacimiento = alumno.fecha_nacimiento
        alumno_existente.sexo = alumno.sexo
        alumno_existente.nro_legajo = alumno.nro_legajo
        alumno_existente.fecha_ingreso = alumno.fecha_ingreso
        alumno_existente.especialidad = alumno.especialidad
    
    @classmethod
    def generar_certificado_alumno_regular(cls, id: int, tipo: str) -> BytesIO:
        """Genera un certificado de alumno regular en el formato especificado."""
        alumno = cls.repository.buscar_por_id(id)
        if not alumno:
            return None
        
        context = cls._obtener_contexto_alumno(alumno)
        documento = obtener_tipo_documento(tipo)
        if not documento:
            return None
        
        return documento.generar(
            carpeta='certificado',
            plantilla='certificado_pdf',
            context=context
        )
    
    @staticmethod
    def _obtener_fecha_actual() -> str:
        """Retorna la fecha actual formateada."""
        fecha_actual = datetime.datetime.now()
        return fecha_actual.strftime('%d de %B de %Y')

    @classmethod
    def _obtener_contexto_alumno(cls, alumno: Alumno) -> dict:
        """Prepara el contexto para generar documentos del alumno."""
        especialidad = alumno.especialidad
        facultad = especialidad.facultad
        universidad = facultad.universidad
        return {
            "alumno": alumno,
            "especialidad": especialidad,
            "facultad": facultad,
            "universidad": universidad,
            "fecha": cls._obtener_fecha_actual()
        }
