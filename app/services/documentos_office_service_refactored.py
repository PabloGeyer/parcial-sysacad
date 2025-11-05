"""
Refactorización del sistema de generación de documentos aplicando OCP y LSP.

PROBLEMA ORIGINAL (Violación OCP + LSP):
- Factory method hardcodeado
- Firmas inconsistentes entre clase base e implementaciones
- No extensible sin modificar código

SOLUCIÓN SOLID:
- Registro dinámico de generadores (OCP)
- Firma consistente en todas las implementaciones (LSP)
- Fácil agregar nuevos formatos (DIP)
"""
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Dict, Type
import os
from flask import current_app, render_template, url_for
from python_odt_template import ODTTemplate

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False
    HTML = None

from python_odt_template.jinja import get_odt_renderer
from docxtpl import DocxTemplate
import jinja2


class DocumentGenerator(ABC):
    """
    Clase base abstracta para generadores de documentos.
    
    SOLID: Cumple LSP - Todas las subclases tienen la misma firma.
    """
    
    @abstractmethod
    def generar(self, carpeta: str, plantilla: str, context: dict) -> BytesIO:
        """
        Genera un documento en el formato específico.
        
        Args:
            carpeta: Carpeta donde está la plantilla
            plantilla: Nombre de la plantilla (sin extensión)
            context: Contexto para renderizar
            
        Returns:
            BytesIO con el documento generado
        """
        pass
    
    @property
    @abstractmethod
    def extension(self) -> str:
        """Extensión del archivo (ej: 'pdf', 'odt')"""
        pass


class PDFDocumentGenerator(DocumentGenerator):
    """Generador de documentos PDF usando WeasyPrint."""
    
    @property
    def extension(self) -> str:
        return 'pdf'
    
    def generar(self, carpeta: str, plantilla: str, context: dict) -> BytesIO:
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                "WeasyPrint no está disponible. "
                "Para generar PDFs, instala GTK+ en Windows o usa un ambiente Linux."
            )
        
        html_string = render_template(f'{carpeta}/{plantilla}.html', context=context)
        base_url = url_for('static', filename='', _external=True)
        bytes_data = HTML(string=html_string, base_url=base_url).write_pdf()
        
        pdf_io = BytesIO(bytes_data)
        return pdf_io


class ODTDocumentGenerator(DocumentGenerator):
    """Generador de documentos ODT (OpenDocument Text)."""
    
    @property
    def extension(self) -> str:
        return 'odt'
    
    def generar(self, carpeta: str, plantilla: str, context: dict) -> BytesIO:
        import tempfile
        
        odt_renderer = get_odt_renderer(media_path=url_for('static', filename='media'))
        path_template = os.path.join(current_app.root_path, f'{carpeta}', f'{plantilla}.odt')
        
        odt_io = BytesIO()
        with tempfile.NamedTemporaryFile(suffix='.odt', delete=False) as temp_file:
            temp_path = temp_file.name

        with ODTTemplate(path_template) as template:
            odt_renderer.render(template, context=context)
            template.pack(temp_path)
            with open(temp_path, 'rb') as f:
                odt_io.write(f.read())
            
        os.unlink(temp_path)
        odt_io.seek(0)
        return odt_io


class DOCXDocumentGenerator(DocumentGenerator):
    """Generador de documentos DOCX (Microsoft Word)."""
    
    @property
    def extension(self) -> str:
        return 'docx'
    
    def generar(self, carpeta: str, plantilla: str, context: dict) -> BytesIO:
        import tempfile
        
        path_template = os.path.join(current_app.root_path, f'{carpeta}', f'{plantilla}.docx')
        doc = DocxTemplate(path_template)
        
        docx_io = BytesIO()
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_path = temp_file.name

        jinja_env = jinja2.Environment()
        doc.render(context, jinja_env)
        doc.save(temp_path)
        
        with open(temp_path, 'rb') as f:
            docx_io.write(f.read())
            
        os.unlink(temp_path)
        docx_io.seek(0)
        return docx_io


class DocumentGeneratorFactory:
    """
    Factory para generadores de documentos.
    
    SOLID Improvements:
    - OCP: Se pueden registrar nuevos generadores sin modificar esta clase
    - DIP: Depende de la abstracción DocumentGenerator
    - SRP: Solo se encarga de crear y registrar generadores
    """
    
    _generators: Dict[str, Type[DocumentGenerator]] = {}
    
    @classmethod
    def register(cls, format_type: str, generator_class: Type[DocumentGenerator]):
        """
        Registra un nuevo generador de documentos.
        
        OCP: Permite EXTENDER sin MODIFICAR.
        
        Args:
            format_type: Tipo de formato ('pdf', 'odt', 'docx', etc.)
            generator_class: Clase del generador
        """
        cls._generators[format_type.lower()] = generator_class
    
    @classmethod
    def create(cls, format_type: str) -> DocumentGenerator:
        """
        Crea una instancia del generador solicitado.
        
        Args:
            format_type: Tipo de documento ('pdf', 'odt', 'docx')
            
        Returns:
            Instancia del generador
            
        Raises:
            ValueError: Si el formato no está registrado
        """
        generator_class = cls._generators.get(format_type.lower())
        if not generator_class:
            available = ', '.join(cls._generators.keys())
            raise ValueError(
                f"Formato '{format_type}' no soportado. "
                f"Formatos disponibles: {available}"
            )
        return generator_class()
    
    @classmethod
    def get_available_formats(cls) -> list[str]:
        """Retorna lista de formatos disponibles."""
        return list(cls._generators.keys())


# Registro automático de generadores al importar el módulo
# OCP: Para agregar un nuevo formato, solo se agrega una línea aquí
DocumentGeneratorFactory.register('pdf', PDFDocumentGenerator)
DocumentGeneratorFactory.register('odt', ODTDocumentGenerator)
DocumentGeneratorFactory.register('docx', DOCXDocumentGenerator)


# Compatibilidad con código existente (API legacy)
def obtener_tipo_documento(tipo: str) -> DocumentGenerator:
    """
    Función legacy para compatibilidad con código existente.
    
    Deprecated: Usar DocumentGeneratorFactory.create() directamente.
    """
    return DocumentGeneratorFactory.create(tipo)


# Alias para compatibilidad con código viejo
Document = DocumentGenerator
PDFDocument = PDFDocumentGenerator
ODTDocument = ODTDocumentGenerator
DOCXDocument = DOCXDocumentGenerator
