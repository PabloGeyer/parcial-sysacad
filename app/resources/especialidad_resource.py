from flask import jsonify, Blueprint, request

from app.mapping.especialidad_mapping import EspecialidadMapping
from app.services.especialidad_service import EspecialidadService

especialidad_bp = Blueprint('especialidad', __name__)
especialidad_mapping = EspecialidadMapping()

@especialidad_bp.route('/especialidad', methods=['GET'])
def buscar_todos():
    especialidades = EspecialidadService.buscar_todos()
    return especialidad_mapping.dump(especialidades, many=True), 200

@especialidad_bp.route('/especialidad/<hashid:id>', methods=['GET'])
def buscar_por_id(id):
    especialidad = EspecialidadService.buscar_por_id(id)
    return especialidad_mapping.dump(especialidad), 200

@especialidad_bp.route('/especialidad', methods=['POST'])
def crear():
    especialidad = especialidad_mapping.load(request.get_json())
    EspecialidadService.crear(especialidad)
    return jsonify("Especialidad creada exitosamente"), 200

@especialidad_bp.route('/especialidad/<hashid:id>', methods=['PUT'])
def actualizar(id):
    especialidad = especialidad_mapping.load(request.get_json())
    EspecialidadService.actualizar(id, especialidad)
    return jsonify("Especialidad actualizada exitosamente"), 200

@especialidad_bp.route('/especialidad/<hashid:id>', methods=['DELETE'])
def borrar_por_id(id):
    EspecialidadService.borrar_por_id(id)
    return jsonify("Especialidad borrada exitosamente"), 200

@especialidad_bp.route('/especialidad/<hashid:id>/alumnos', methods=['GET'])
def buscar_alumnos_por_especialidad(id):
    """
    Endpoint REST que retorna todos los alumnos de una especialidad
    junto con los datos de la facultad.
    
    Cumple con:
    - SRP: Solo maneja la petición HTTP
    - OCP: Extensible sin modificar código existente
    - DIP: Depende de la abstracción EspecialidadService
    """
    # Validar que el id sea válido
    if not id:
        return jsonify({"error": "ID de especialidad inválido"}), 400
    
    resultado = EspecialidadService.buscar_alumnos_por_especialidad(id)
    
    if not resultado:
        return jsonify({"error": "Especialidad no encontrada"}), 404
    
    return jsonify(resultado), 200
