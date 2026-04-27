# Propotipo Contenedor Backend Panoptes

Panoptes es una solución de software diseñada para la gestión de convivencia dentro de un recinto educacional ficticio "San penquista". Este prototipo representa el **Backend MVP** del sistema, enfocado en validar la lógica del proyecto y la arquitectura propuesta. Generado con el modelo de intelingencia artificial Claude Sonnet 4.6.

## Estructura
El código se organiza en los siguientes modulos
- `models.py`: Definición de entidades del dominio.
- `services.py`: Capa de aplicación que orquesta la lógica de negocio.
- `controllers.py`: Simulación de endpoints REST para la interacción del usuario.
- `repositories.py`: Persistencia simulada en memoria con soporte para trazabilidad histórica.
- `adapters.py`: Puentes de comunicación con sistemas externos (Curricular y Email).
- `main.py`: Punto de entrada que configura la inyección de dependencias y ejecuta la simulación.

## ¿Cómo ejecutar el prototipo?
Requisitos: **Python 3.10** o superior

### Pasos de Ejecución
1. Clonar este repositorio de manera local en su computador
2. Abrir la terminal en el directorio con el repositorio clonado
3. Ejecutar el comando principal:

    Linux:
    `python3 main.py`

    Windows:
   `python main.py` o `py main.py`
