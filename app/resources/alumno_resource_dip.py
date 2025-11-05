"""
Ejemplo de aplicación del principio DIP (Dependency Inversion) en Resources.

PROBLEMA ORIGINAL (Violación DIP):
- Resources dependen directamente de implementaciones concretas de Services
- Acoplamiento fuerte
- Difícil de testear con mocks

SOLUCIÓN DIP:
- Resources dependen de abstracciones (interfaces/protocolos)
- Inyección de dependencias
- Fácil de testear y extender
"""
from abc import ABC, abstractmethod
from typing import Protocol, List, Optional
from flask import jsonify, Blueprint, request
from app.models import Alumno


# PASO 1: Definir la abstracción (Interface/Protocol)
class IAlumnoService(Protocol):
    """
    Protocolo que define el contrato para AlumnoService.
    
    DIP: Las clases de alto nivel (Resources) dependen de esta abstracción,
    no de la implementación concreta.
    """
    
    def crear(self, alumno: Alumno) -> Alumno:
        """Crea un nuevo alumno."""
        ...
    
    def buscar_por_id(self, id: int) -> Optional[Alumno]:
        """Busca un alumno por ID."""
        ...
    
    def buscar_todos(self) -> List[Alumno]:
        """Retorna todos los alumnos."""
        ...
    
    def actualizar(self, id: int, alumno: Alumno) -> Optional[Alumno]:
        """Actualiza un alumno existente."""
        ...
    
    def borrar_por_id(self, id: int) -> bool:
        """Elimina un alumno por ID."""
        ...


# PASO 2: Resource con Inyección de Dependencias
class AlumnoResource:
    """
    Controlador HTTP para alumnos usando DIP.
    
    SOLID Benefits:
    - DIP: Depende de IAlumnoService (abstracción), no de implementación
    - SRP: Solo maneja HTTP
    - OCP: Fácil cambiar implementación sin modificar esta clase
    - Testeable: Se puede inyectar un mock de IAlumnoService
    """
    
    def __init__(self, alumno_service: IAlumnoService, alumno_mapping):
        """
        Constructor con inyección de dependencias.
        
        Args:
            alumno_service: Cualquier implementación de IAlumnoService
            alumno_mapping: Objeto para serialización
        """
        self._service = alumno_service
        self._mapping = alumno_mapping
    
    def buscar_todos(self):
        """GET /alumno - Lista todos los alumnos."""
        try:
            alumnos = self._service.buscar_todos()
            return self._mapping.dump(alumnos, many=True), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def buscar_por_id(self, id: int):
        """GET /alumno/<id> - Busca un alumno por ID."""
        try:
            alumno = self._service.buscar_por_id(id)
            if not alumno:
                return jsonify({"error": "Alumno no encontrado"}), 404
            return self._mapping.dump(alumno), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def crear(self):
        """POST /alumno - Crea un nuevo alumno."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Datos inválidos"}), 400
            
            alumno = self._mapping.load(data)
            alumno_creado = self._service.crear(alumno)
            
            return jsonify({
                "mensaje": "Alumno creado exitosamente",
                "id": alumno_creado.hashid
            }), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def actualizar(self, id: int):
        """PUT /alumno/<id> - Actualiza un alumno."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Datos inválidos"}), 400
            
            alumno = self._mapping.load(data)
            alumno_actualizado = self._service.actualizar(id, alumno)
            
            if not alumno_actualizado:
                return jsonify({"error": "Alumno no encontrado"}), 404
            
            return jsonify({"mensaje": "Alumno actualizado exitosamente"}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def borrar_por_id(self, id: int):
        """DELETE /alumno/<id> - Elimina un alumno."""
        try:
            eliminado = self._service.borrar_por_id(id)
            if not eliminado:
                return jsonify({"error": "Alumno no encontrado"}), 404
            
            return jsonify({"mensaje": "Alumno borrado exitosamente"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# PASO 3: Factory o configuración centralizada
def crear_alumno_blueprint(alumno_service: IAlumnoService, alumno_mapping) -> Blueprint:
    """
    Factory que crea el Blueprint con las dependencias inyectadas.
    
    DIP: Las dependencias se pasan desde afuera (inversión de control).
    
    Args:
        alumno_service: Implementación del servicio de alumnos
        alumno_mapping: Objeto para serialización
        
    Returns:
        Blueprint configurado
    """
    alumno_bp = Blueprint('alumno', __name__)
    resource = AlumnoResource(alumno_service, alumno_mapping)
    
    # Registrar rutas
    alumno_bp.route('/alumno', methods=['GET'])(resource.buscar_todos)
    alumno_bp.route('/alumno/<hashid:id>', methods=['GET'])(resource.buscar_por_id)
    alumno_bp.route('/alumno', methods=['POST'])(resource.crear)
    alumno_bp.route('/alumno/<hashid:id>', methods=['PUT'])(resource.actualizar)
    alumno_bp.route('/alumno/<hashid:id>', methods=['DELETE'])(resource.borrar_por_id)
    
    return alumno_bp


# EJEMPLO DE USO (en app/__init__.py o blueprints.py):
"""
from app.services.alumno_service import AlumnoService
from app.mapping.alumno_mapping import AlumnoMapping
from app.resources.alumno_resource_dip import crear_alumno_blueprint

# Inyectar dependencias
alumno_service = AlumnoService
alumno_mapping = AlumnoMapping()

# Crear blueprint con DIP
alumno_bp = crear_alumno_blueprint(alumno_service, alumno_mapping)

# Registrar en la app
app.register_blueprint(alumno_bp)
"""


# BENEFICIOS DE ESTA REFACTORIZACIÓN:

"""
1. TESTABILIDAD:
   def test_buscar_todos():
       # Mock del service
       mock_service = MockAlumnoService()
       mock_mapping = MockAlumnoMapping()
       
       # Inyectar mock
       resource = AlumnoResource(mock_service, mock_mapping)
       result = resource.buscar_todos()
       
       assert result[1] == 200

2. FLEXIBILIDAD:
   # Cambiar implementación sin modificar Resource
   alumno_bp = crear_alumno_blueprint(
       AlumnoServiceConCache(),  # Nueva implementación
       alumno_mapping
   )

3. MANTENIBILIDAD:
   # Resource no conoce detalles de implementación
   # Solo conoce la interfaz (contrato)

4. CUMPLE SOLID:
   ✅ SRP: Resource solo maneja HTTP
   ✅ OCP: Abierto a nuevas implementaciones de service
   ✅ LSP: Cualquier IAlumnoService es intercambiable
   ✅ ISP: Interface específica para lo que Resource necesita
   ✅ DIP: Depende de abstracción, no de concreción
"""
