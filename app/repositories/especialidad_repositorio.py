from app import db
from app.models import Especialidad, Alumno

class EspecialidadRepository:

    @staticmethod
    def crear(especialidad):
        db.session.add(especialidad)
        db.session.commit()

    @staticmethod
    def buscar_por_id(id: int):
        return db.session.query(Especialidad).filter_by(id=id).first()

    @staticmethod
    def buscar_todos():
        return db.session.query(Especialidad).all()

    @staticmethod
    def actualizar(especialidad) -> Especialidad:
        db.session.merge(especialidad)
        db.session.commit()
        return especialidad
    
    @staticmethod
    def borrar_por_id(id: int) -> bool:
        especialidad = db.session.query(Especialidad).filter_by(id=id).first()
        if not especialidad:
            return False
        db.session.delete(especialidad)
        db.session.commit()
        return True

    @staticmethod
    def buscar_alumnos_por_especialidad(especialidad_id: int) -> list[Alumno]:
        """
        Busca todos los alumnos que pertenecen a una especialidad específica.
        SRP: Este método solo se encarga de la consulta a la base de datos.
        """
        return db.session.query(Alumno).filter_by(especialidad_id=especialidad_id).all()
