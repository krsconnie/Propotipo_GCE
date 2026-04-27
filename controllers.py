"""
controllers.py - Controladores que simulan endpoints REST
Sistema de Gestión de Convivencia Escolar — Panoptes
"""

from typing import Any, Optional
from models import NivelGravedad, Coordinador, Documento, Involucrado
from services import ConvivenciaApplicationService


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _response(ok: bool, data: Any = None, message: str = "") -> dict:
    return {"success": ok, "data": data, "message": message}


# ─── Controlador de Gestión de Casos ──────────────────────────────────────────

COMPONENT_CASOS = "Controlador de gestión de casos"


class ControladorGestionCasos:
    """
    Recibe peticiones relacionadas con Incidentes y Casos.
    Endpoints simulados:
      POST   /incidentes
      POST   /casos
      PATCH  /casos/{id}/descripcion    — UC2
      PATCH  /casos/{id}/hito           — UC6
      PATCH  /casos/{id}/hito/{hid}     — UC8
      DELETE /casos/{id}                — RF8
      PATCH  /casos/{id}/cerrar
      GET    /casos/{id}/involucrados   — UC5
      GET    /casos/{id}/carpeta        — UC9
    """

    def __init__(self, service: ConvivenciaApplicationService) -> None:
        self._service = service

    def post_incidente(
        self,
        descripcion: str,
        id_estudiante: int,
        id_productor: int,
        gravedad: str = "LEVE",
    ) -> dict:
        """POST /incidentes — Registrar una nueva observación previa (Incidente)."""
        print(f"\n[{COMPONENT_CASOS}] -> POST /incidentes recibido "
              f"(estudiante={id_estudiante}, gravedad={gravedad}).")

        try:
            nivel = NivelGravedad(gravedad.upper())
        except ValueError:
            msg = f"Gravedad '{gravedad}' no válida. Use: LEVE, MODERADO, GRAVE."
            print(f"[{COMPONENT_CASOS}] -> ERROR: {msg}")
            return _response(False, message=msg)

        incidente = self._service.registrar_incidente(
            descripcion=descripcion,
            id_estudiante=id_estudiante,
            id_productor=id_productor,
            gravedad=nivel,
        )

        if incidente:
            print(f"[{COMPONENT_CASOS}] -> 201 Created: Observación previa #{incidente.id_incidente}.")
            return _response(True, data=incidente, message="Observación previa registrada.")
        return _response(False, message="No se pudo registrar la observación previa.")

    def post_caso(
        self,
        descripcion: str,
        id_incidente: int,
        coordinador: Coordinador,
        email_notificacion: str,
    ) -> dict:
        """POST /casos — Abrir un caso formal a partir de una observación previa."""
        print(f"\n[{COMPONENT_CASOS}] -> POST /casos recibido "
              f"(incidente={id_incidente}, coordinador='{coordinador.nombre}').")

        caso = self._service.abrir_caso(
            descripcion=descripcion,
            id_incidente=id_incidente,
            coordinador=coordinador,
            email_notificacion=email_notificacion,
        )

        if caso:
            print(f"[{COMPONENT_CASOS}] -> 201 Created: Caso #{caso.id_caso}.")
            return _response(True, data=caso, message="Caso abierto exitosamente.")
        return _response(False, message="No se pudo abrir el caso.")

    # Cumple UC2 — Modificar caso
    def patch_descripcion_caso(
        self,
        id_caso: int,
        nueva_descripcion: str,
        coordinador: Coordinador,
    ) -> dict:
        """PATCH /casos/{id}/descripcion — UC2: Modificar descripción del caso."""
        print(f"\n[{COMPONENT_CASOS}] -> PATCH /casos/{id_caso}/descripcion recibido.")

        caso = self._service.modificar_descripcion_caso(id_caso, nueva_descripcion, coordinador)
        if caso:
            print(f"[{COMPONENT_CASOS}] -> 200 OK: Descripción del Caso #{id_caso} actualizada.")
            return _response(True, data=caso, message="Descripción del caso actualizada.")
        return _response(False, message="No se pudo modificar el caso.")

    def patch_agregar_hito(
        self,
        id_caso: int,
        descripcion_hito: str,
        email_notificacion: str,
        documentos: Optional[list[Documento]] = None,
    ) -> dict:
        """PATCH /casos/{id}/hito — UC6: Agregar unidad atómica (Hito) a un caso."""
        print(f"\n[{COMPONENT_CASOS}] -> PATCH /casos/{id_caso}/hito recibido.")

        hito = self._service.agregar_hito_a_caso(
            id_caso=id_caso,
            descripcion_hito=descripcion_hito,
            email_notificacion=email_notificacion,
            documentos=documentos,
        )

        if hito:
            print(f"[{COMPONENT_CASOS}] -> 200 OK: Unidad atómica #{hito.id_hito} agregada.")
            return _response(True, data=hito, message="Unidad atómica (Hito) agregada.")
        return _response(False, message="No se pudo agregar el hito.")

    # Cumple UC8 — Modificar hito (unidad atómica)
    def patch_modificar_hito(
        self,
        id_caso: int,
        id_hito: int,
        nueva_descripcion: str,
        coordinador: Coordinador,
    ) -> dict:
        """PATCH /casos/{id}/hito/{hid} — UC8: Modificar unidad atómica existente."""
        print(f"\n[{COMPONENT_CASOS}] -> PATCH /casos/{id_caso}/hito/{id_hito} recibido.")

        hito = self._service.modificar_hito(id_caso, id_hito, nueva_descripcion, coordinador)
        if hito:
            print(f"[{COMPONENT_CASOS}] -> 200 OK: Unidad atómica #{id_hito} modificada.")
            return _response(True, data=hito, message="Unidad atómica (Hito) modificada.")
        return _response(False, message="No se pudo modificar el hito.")

    # Cumple UC5 — Ver involucrados
    def get_involucrados(self, id_caso: int) -> dict:
        """GET /casos/{id}/involucrados — UC5: Lista de personas relacionadas con el caso."""
        print(f"\n[{COMPONENT_CASOS}] -> GET /casos/{id_caso}/involucrados recibido.")

        involucrados = self._service.obtener_involucrados(id_caso)
        print(f"[{COMPONENT_CASOS}] -> 200 OK: {len(involucrados)} involucrado(s) retornados.")
        return _response(True, data=involucrados, message=f"{len(involucrados)} involucrado(s).")

    # Cumple UC9 — Acceder carpeta de documentos
    def get_carpeta_documentos(self, id_caso: int) -> dict:
        """GET /casos/{id}/carpeta — UC9: Visualización de archivos adjuntos del caso."""
        print(f"\n[{COMPONENT_CASOS}] -> GET /casos/{id_caso}/carpeta recibido.")

        carpeta = self._service.acceder_carpeta_caso(id_caso)
        print(f"[{COMPONENT_CASOS}] -> 200 OK: {len(carpeta)} documento(s) en carpeta.")
        return _response(True, data=carpeta, message=f"{len(carpeta)} documento(s) encontrados.")

    # Cumple RF8 — Eliminación lógica
    def delete_caso(self, id_caso: int, coordinador: Coordinador) -> dict:
        """DELETE /casos/{id} — RF8: Borrado lógico (trazabilidad preservada)."""
        print(f"\n[{COMPONENT_CASOS}] -> DELETE /casos/{id_caso} recibido (borrado lógico).")

        caso = self._service.eliminar_caso(id_caso, coordinador)
        if caso:
            print(f"[{COMPONENT_CASOS}] -> 200 OK: Caso #{id_caso} eliminado lógicamente.")
            return _response(True, data=caso, message="Caso eliminado lógicamente (RF8).")
        return _response(False, message="No se pudo eliminar el caso.")

    def patch_cerrar_caso(self, id_caso: int, coordinador: Coordinador) -> dict:
        """PATCH /casos/{id}/cerrar — UC4: Cierra un caso abierto."""
        print(f"\n[{COMPONENT_CASOS}] -> PATCH /casos/{id_caso}/cerrar recibido.")

        caso = self._service.cerrar_caso(id_caso, coordinador)
        if caso:
            print(f"[{COMPONENT_CASOS}] -> 200 OK: Caso #{id_caso} cerrado.")
            return _response(True, data=caso, message="Caso cerrado.")
        return _response(False, message="No se pudo cerrar el caso.")


# ─── Controlador de Reportes ──────────────────────────────────────────────────

COMPONENT_REPORTES = "Controlador de reportes"


class ControladorReportes:
    """
    Recibe peticiones de generación de reportes.
    Endpoints simulados:
      GET /reportes/caso/{id}
      GET /reportes/estudiante/{id}
    """

    def __init__(self, service: ConvivenciaApplicationService) -> None:
        self._service = service

    def get_reporte_caso(self, id_caso: int) -> dict:
        """GET /reportes/caso/{id} — UC7/RF6: Reporte detallado de un caso."""
        print(f"\n[{COMPONENT_REPORTES}] -> GET /reportes/caso/{id_caso} recibido.")

        reporte = self._service.generar_reporte_caso(id_caso)
        if reporte:
            print(f"[{COMPONENT_REPORTES}] -> 200 OK: Reporte #{reporte.id_reporte} entregado.")
            return _response(True, data=reporte, message="Reporte generado.")
        return _response(False, message="No se encontró el caso para reportar.")

    def get_reporte_estudiante(self, id_estudiante: int) -> dict:
        """GET /reportes/estudiante/{id} — UC7: Historial de casos de un estudiante."""
        print(f"\n[{COMPONENT_REPORTES}] -> GET /reportes/estudiante/{id_estudiante} recibido.")

        reporte = self._service.generar_reporte_estudiante(id_estudiante)
        if reporte:
            print(f"[{COMPONENT_REPORTES}] -> 200 OK: Reporte #{reporte.id_reporte} entregado.")
            return _response(True, data=reporte, message="Reporte generado.")
        return _response(False, message="No se encontró el estudiante.")

    def get_auditoria(self, id_estudiante: int) -> dict:
            """GET /reportes/auditoria/{id} — UC13: Consulta de auditoría para estudiantes."""
            print(f"\n[{COMPONENT_REPORTES}] -> GET /reportes/auditoria/{id_estudiante} recibido.")
            reporte = self._service.generar_auditoria_estudiante(id_estudiante)
            if reporte:
                return _response(True, data=reporte, message="Auditoría generada.")
            return _response(False, message="Error al generar auditoría.")