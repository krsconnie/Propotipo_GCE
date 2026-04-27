"""
adapters.py - Adaptadores para sistemas externos
Sistema de Gestión de Convivencia Escolar
"""

from typing import Optional
from models import Estudiante


# ─── Adaptador Sistema Curricular ─────────────────────────────────────────────

COMPONENT_CURRICULAR = "Adaptador de sistema curricular"
COMPONENT_CORREO     = "Componente de correo electrónico"


class AdaptadorSistemaCurricular:
    """
    Actúa como puente para solicitar información al Sistema Curricular externo.
    En el MVP simula respuestas con datos de muestra.
    """

    # Base de datos simulada del sistema curricular externo
    _db_estudiantes: dict[int, Estudiante] = {
        1: Estudiante(1, "Sofía Martínez",  101, "4°A Medio"),
        2: Estudiante(2, "Diego Rojas",     101, "4°A Medio"),
        3: Estudiante(3, "Valentina López", 102, "3°B Medio"),
        4: Estudiante(4, "Matías González", 103, "2°C Básico"),
    }

    def verificar_estudiante(self, id_estudiante: int) -> Optional[Estudiante]:
        """Consulta al Sistema Curricular si el estudiante existe y está activo."""
        print(f"[{COMPONENT_CURRICULAR}] -> Solicitando datos del estudiante #{id_estudiante} al Sistema Curricular externo.")
        estudiante = self._db_estudiantes.get(id_estudiante)
        if estudiante:
            print(f"[{COMPONENT_CURRICULAR}] -> Estudiante encontrado: '{estudiante.nombre}' ({estudiante.nombre_curso}).")
        else:
            print(f"[{COMPONENT_CURRICULAR}] -> ADVERTENCIA: Estudiante #{id_estudiante} no encontrado en el Sistema Curricular.")
        return estudiante

    def obtener_curso(self, id_curso: int) -> list[Estudiante]:
        """Devuelve todos los estudiantes de un curso."""
        print(f"[{COMPONENT_CURRICULAR}] -> Solicitando lista de estudiantes del curso #{id_curso}.")
        resultado = [e for e in self._db_estudiantes.values() if e.id_curso == id_curso]
        print(f"[{COMPONENT_CURRICULAR}] -> {len(resultado)} estudiante(s) encontrados en el curso #{id_curso}.")
        return resultado


# ─── Componente de Correo Electrónico ─────────────────────────────────────────

class ComponenteCorreoElectronico:
    """
    Interfaz para comunicarse con el Sistema de Correos externo.
    Simula el envío real de correos electrónicos.
    """

    def __init__(self) -> None:
        self._enviados: list[dict] = []

    def enviar_notificacion(
        self,
        destinatario: str,
        asunto: str,
        cuerpo: str,
    ) -> bool:
        """Simula el envío de un correo de notificación."""
        print(f"[{COMPONENT_CORREO}] -> Preparando correo hacia '{destinatario}'.")
        print(f"[{COMPONENT_CORREO}] -> Asunto: '{asunto}'.")
        print(f"[{COMPONENT_CORREO}] -> Conectando con Sistema de Correos externo...")

        registro = {
            "destinatario": destinatario,
            "asunto": asunto,
            "cuerpo": cuerpo,
        }
        self._enviados.append(registro)

        print(f"[{COMPONENT_CORREO}] -> ✓ Correo enviado exitosamente a '{destinatario}'.")
        return True

    def notificar_apertura_caso(self, destinatario: str, id_caso: int, descripcion: str) -> bool:
        asunto = f"[Convivencia Escolar] Apertura de Caso #{id_caso}"
        cuerpo = (
            f"Se ha abierto formalmente el Caso #{id_caso}.\n"
            f"Descripción: {descripcion}\n"
            "Por favor revise el sistema para más detalles."
        )
        return self.enviar_notificacion(destinatario, asunto, cuerpo)

    def notificar_nuevo_hito(self, destinatario: str, id_caso: int, desc_hito: str) -> bool:
        asunto = f"[Convivencia Escolar] Nuevo Hito en Caso #{id_caso}"
        cuerpo = (
            f"Se ha registrado un nuevo hito en el Caso #{id_caso}:\n"
            f"  • {desc_hito}\n"
            "Acceda al sistema para ver el detalle completo."
        )
        return self.enviar_notificacion(destinatario, asunto, cuerpo)

    def historial_enviados(self) -> list[dict]:
        return self._enviados
