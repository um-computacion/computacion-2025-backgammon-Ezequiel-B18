# Prompts de Documentación

## 2025-01-09 - Modificación del CI para ejecutar en todo el proyecto

### Prompt
I need to change the ci.yml file to run the workflow on the entire project, help me change it. This should go in prompts-documentacion.

### Respuesta Generada
Se modificó el archivo `.github/workflows/ci.yml` para que el workflow de CI ejecute las pruebas y análisis en todo el proyecto:

**Cambios realizados:**

1. **Descubrimiento de pruebas mejorado**: 
   - Cambió de `coverage run -m unittest discover` a `coverage run -m unittest discover -s tests -p "test*.py"`
   - Esto especifica que busque en el directorio `tests` archivos que coincidan con el patrón `test*.py`

2. **Análisis de Pylint en todo el proyecto**:
   - Cambió de `pylint --rcfile=.pylintrc main.py test.py` a `find . -name "*.py" -not -path "./venv/*" -not -path "./.env/*" | xargs pylint --rcfile=.pylintrc`
   - Esto encuentra y analiza todos los archivos Python del proyecto, excluyendo directorios virtuales

**Beneficios:**
- El CI ahora ejecuta todas las pruebas del proyecto automáticamente
- Pylint analiza todo el código Python, no solo archivos específicos
- Mejor cobertura de código y análisis de calidad
- Escalabilidad: nuevos archivos de prueba se detectan automáticamente

