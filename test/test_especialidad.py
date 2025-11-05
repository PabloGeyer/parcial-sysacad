import unittest
import os
from flask import current_app
from app import create_app
from app.models import Especialidad, TipoEspecialidad
from app.services import EspecialidadService, TipoEspecialidadService
from test.instancias import nuevaespecialidad, nuevotipoespecialidad
from app import db

class EspecialidadTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_crear(self):
        especialidad= nuevaespecialidad()
        self.assertIsNotNone(especialidad)
        self.assertIsNotNone(especialidad.id)
        self.assertGreaterEqual(especialidad.id,1)
        self.assertEqual(especialidad.nombre, "Matematicas")
        self.assertEqual(especialidad.tipoespecialidad.nombre, "Cardiologia")

    def test_buscar_por_id(self):
        especialidad = nuevaespecialidad()
        r=EspecialidadService.buscar_por_id(especialidad.id)
        self.assertIsNotNone(r)
        self.assertEqual(r.nombre, "Matematicas")
        self.assertEqual(r.letra, "A")

    def test_buscar_todos(self):
        especialidad1 =nuevaespecialidad()
        especialidad2 =nuevaespecialidad()
        especialidades = EspecialidadService.buscar_todos()
        self.assertIsNotNone(especialidades)
        self.assertEqual(len(especialidades),2)

    def test_actualizar(self):
        especialidad = nuevaespecialidad()
        especialidad.nombre = "matematica actualizada"
        especialidad_actualizada = EspecialidadService.actualizar(especialidad.id, especialidad)
        self.assertEqual(especialidad_actualizada.nombre, "matematica actualizada")

    def test_borrar(self):
        especialidad = nuevaespecialidad()
        borrado = EspecialidadService.borrar_por_id(especialidad.id)
        self.assertTrue(borrado)
        resultado = EspecialidadService.buscar_por_id(especialidad.id)
        self.assertIsNone(resultado)

    def test_buscar_alumnos_por_especialidad(self):
        """Test TDD: Buscar todos los alumnos de una especialidad con datos de facultad"""
        from test.instancias import nuevoalumno
        
        # Crear especialidad con facultad
        especialidad = nuevaespecialidad(nombre="Ingeniería Informática")
        
        # Crear varios alumnos de esa especialidad
        alumno1 = nuevoalumno(nombre="Juan", apellido="Pérez", especialidad=especialidad)
        alumno2 = nuevoalumno(nombre="María", apellido="González", especialidad=especialidad)
        alumno3 = nuevoalumno(nombre="Carlos", apellido="Rodríguez", especialidad=especialidad)
        
        # Crear otro alumno de otra especialidad (no debe aparecer)
        otra_especialidad = nuevaespecialidad(nombre="Otra Especialidad")
        alumno_otra = nuevoalumno(nombre="Pedro", apellido="López", especialidad=otra_especialidad)
        
        # Buscar alumnos de la especialidad
        resultado = EspecialidadService.buscar_alumnos_por_especialidad(especialidad.id)
        
        # Validaciones
        self.assertIsNotNone(resultado)
        self.assertIn('especialidad', resultado)
        self.assertIn('facultad', resultado)
        self.assertIn('alumnos', resultado)
        
        # Validar datos de especialidad
        self.assertEqual(resultado['especialidad']['nombre'], "Ingeniería Informática")
        self.assertEqual(resultado['especialidad']['letra'], "A")
        
        # Validar datos de facultad
        self.assertEqual(resultado['facultad']['nombre'], "Facultad de Ciencias")
        self.assertIn('universidad', resultado['facultad'])
        
        # Validar alumnos
        self.assertEqual(len(resultado['alumnos']), 3)
        nombres_alumnos = [a['nombre'] for a in resultado['alumnos']]
        self.assertIn("Juan", nombres_alumnos)
        self.assertIn("María", nombres_alumnos)
        self.assertIn("Carlos", nombres_alumnos)
        self.assertNotIn("Pedro", nombres_alumnos)  # No debe aparecer
        
        # Validar estructura de alumno
        primer_alumno = resultado['alumnos'][0]
        self.assertIn('nombre', primer_alumno)
        self.assertIn('apellido', primer_alumno)
        self.assertIn('nro_legajo', primer_alumno)

    def test_endpoint_buscar_alumnos_por_especialidad(self):
        """Test de integración: Endpoint REST para buscar alumnos por especialidad"""
        from test.instancias import nuevoalumno
        
        # Crear datos de prueba
        especialidad = nuevaespecialidad(nombre="Ingeniería en Sistemas")
        alumno1 = nuevoalumno(nombre="Ana", apellido="Martínez", especialidad=especialidad)
        alumno2 = nuevoalumno(nombre="Luis", apellido="Fernández", especialidad=especialidad)
        
        # Hacer petición al endpoint usando el hashid generado
        with self.app.test_client() as client:
            # Usar el hashid generado automáticamente con el prefijo /api/v1
            url = f'/api/v1/especialidad/{especialidad.hashid}/alumnos'
            response = client.get(url)
            
            # Validar respuesta HTTP
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            
            # Validar JSON
            data = response.get_json()
            self.assertIsNotNone(data)
            self.assertIn('especialidad', data)
            self.assertIn('facultad', data)
            self.assertIn('alumnos', data)
            
            # Validar contenido
            self.assertEqual(data['especialidad']['nombre'], "Ingeniería en Sistemas")
            self.assertEqual(len(data['alumnos']), 2)
    
    def test_endpoint_especialidad_no_encontrada(self):
        """Test: Endpoint retorna 404 si la especialidad no existe"""
        with self.app.test_client() as client:
            # Usar un ID numérico alto que probablemente no exista
            # El conversor hashid:id en Flask maneja esto
            response = client.get('/api/v1/especialidad/99999/alumnos')
            
            # Puede retornar 404 si el ID no existe
            # O 400/404 si el hashid no es válido
            self.assertIn(response.status_code, [400, 404])

    