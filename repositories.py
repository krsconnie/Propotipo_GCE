"""
repositories.py - Capa de persistencia simulada en memoria
Sistema de Gestión de Convivencia Escolar — Panoptes

RF8: El repositorio nunca elimina físicamente registros; aplica borrado lógico.
     Los listados por defecto excluyen casos marcados como eliminados, pero el
     dato permanece para garantizar trazabilidad total.
"""

from typing import Optional
from models import Caso, Incidente, Hito, Documento, Reporte


COMPONENT = "Datos de convivencia"


class RepositorioConvivencia:
    """Gestión en memoria de Casos (con unidades atómicas/Hitos), Incidentes (observaciones previas) e Hitos."""

    def __init__(self) -> None:
        self._casos: dict[int, Caso] = {}
        self._incidentes: dict[int, Incidente] = {}
        self._reportes: dict[int, Reporte] = {}
        self._caso_counter: int = 1
        self._incidente_counter: int = 1
        self._reporte_counter: int = 1

    # ── Incidentes (observaciones previas) ────────────────────────────────────

    def guardar_incidente(self, incidente: Incidente) -> Incidente:
        if incidente.id_incidente == 0:
            incidente.id_incidente = self._incidente_counter
            self._incidente_counter += 1
        self._incidentes[incidente.id_incidente] = incidente
        print(f"[{COMPONENT}] -> Observación previa (Incidente) #{incidente.id_incidente} persistida en memoria.")
        return incidente

    def obtener_incidente(self, id_incidente: int) -> Optional[Incidente]:
        return self._incidentes.get(id_incidente)

    def listar_incidentes(self) -> list[Incidente]:
        return list(self._incidentes.values())

    # ── Casos ─────────────────────────────────────────────────────────────────

    def guardar_caso(self, caso: Caso) -> Caso:
        if caso.id_caso == 0:
            caso.id_caso = self._caso_counter
            self._caso_counter += 1
        self._casos[caso.id_caso] = caso
        print(f"[{COMPONENT}] -> Caso #{caso.id_caso} ('{caso.descripcion[:40]}...') persistido.")
        return caso

    def obtener_caso(self, id_caso: int) -> Optional[Caso]:
        return self._casos.get(id_caso)

    def listar_casos(self, incluir_eliminados: bool = False) -> list[Caso]:
        """RF8: por defecto excluye los casos con borrado lógico activo."""
        casos = list(self._casos.values())
        if not incluir_eliminados:
            casos = [c for c in casos if not c.eliminado]
        return casos

    def actualizar_caso(self, caso: Caso) -> Caso:
        self._casos[caso.id_caso] = caso
        print(f"[{COMPONENT}] -> Caso #{caso.id_caso} actualizado. Estado: {caso.estado}.")
        return caso

    # Cumple RF8 — Eliminación lógica: delega en el modelo, no borra del dict
    def eliminar_caso(self, id_caso: int) -> Optional[Caso]:
        caso = self._casos.get(id_caso)
        if not caso:
            return None
        caso.eliminar_logicamente()
        self._casos[id_caso] = caso
        print(f"[{COMPONENT}] -> Caso #{id_caso} marcado con borrado lógico (trazabilidad preservada).")
        return caso

    # ── Reportes ──────────────────────────────────────────────────────────────

    def guardar_reporte(self, reporte: Reporte) -> Reporte:
        if reporte.id_reporte == 0:
            reporte.id_reporte = self._reporte_counter
            self._reporte_counter += 1
        self._reportes[reporte.id_reporte] = reporte
        print(f"[{COMPONENT}] -> Reporte #{reporte.id_reporte} guardado.")
        return reporte

    def obtener_reporte(self, id_reporte: int) -> Optional[Reporte]:
        return self._reportes.get(id_reporte)

    def listar_reportes(self) -> list[Reporte]:
        return list(self._reportes.values())
