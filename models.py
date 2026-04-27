"""
models.py - Definición de entidades del dominio usando @dataclass
Sistema de Gestión de Convivencia Escolar — Panoptes

Glosario oficial:
  · Hito    : Unidad atómica de seguimiento dentro de un Caso. Registra un
              hecho concreto, verificable y fechado en la evolución del caso.
  · Incidente: Observación previa registrada por un Productor (ProfesorJefe o
              Inspector) que puede o no derivar en un Caso formal.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class EstadoCaso(str, Enum):
    ABIERTO     = "ABIERTO"
    EN_PROCESO  = "EN_PROCESO"
    CERRADO     = "CERRADO"
    SUSPENDIDO  = "SUSPENDIDO"
    ELIMINADO   = "ELIMINADO"   # RF8: borrado lógico — nunca se borra físicamente


class NivelGravedad(str, Enum):
    LEVE     = "LEVE"
    MODERADO = "MODERADO"
    GRAVE    = "GRAVE"


# ─── Actores ──────────────────────────────────────────────────────────────────

@dataclass
class Estudiante:
    id_estudiante: int
    nombre: str
    id_curso: int
    nombre_curso: str


@dataclass
class ProfesorJefe:
    id_pj: int
    nombre: str
    id_curso: int


@dataclass
class Inspector:
    id_inspector: int
    nombre: str


@dataclass
class Coordinador:
    id_coordinador: int
    nombre: str


# ─── Entidades del Dominio ────────────────────────────────────────────────────

@dataclass
class Documento:
    id_doc: int
    descripcion: str
    url: Optional[str] = None
    fecha_adjunto: date = field(default_factory=date.today)


@dataclass
class Hito:
    """
    Unidad atómica de seguimiento dentro de un Caso. Registra un hecho
    concreto, verificable y fechado en la evolución del caso. (Glosario)
    """
    id_hito: int
    descripcion: str
    fecha: date = field(default_factory=date.today)
    documentos: list[Documento] = field(default_factory=list)

    def agregar_documento(self, doc: Documento) -> None:
        self.documentos.append(doc)

    # Cumple UC8 — Modificar hito (unidad atómica)
    def modificar_descripcion(self, nueva_descripcion: str) -> None:
        """Actualiza el contenido textual de esta unidad atómica."""
        self.descripcion = nueva_descripcion


@dataclass
class Incidente:
    """
    Observación previa registrada por un Productor (ProfesorJefe o Inspector)
    que puede o no derivar en un Caso formal. (Glosario)
    """
    id_incidente: int
    descripcion: str
    id_estudiante: int
    id_productor: int          # quien reporta (ProfesorJefe o Inspector)
    gravedad: NivelGravedad = NivelGravedad.LEVE
    fecha: date = field(default_factory=date.today)
    id_caso_asociado: Optional[int] = None


@dataclass
class Caso:
    id_caso: int
    descripcion: str
    id_estudiante: int
    id_coordinador: int
    estado: EstadoCaso = EstadoCaso.ABIERTO
    fecha_inicio: date = field(default_factory=date.today)
    fecha_cierre: Optional[date] = None
    incidentes: list[int] = field(default_factory=list)   # ids de observaciones previas
    hitos: list[Hito] = field(default_factory=list)       # unidades atómicas de seguimiento
    eliminado: bool = False                               # RF8: flag de borrado lógico

    def agregar_hito(self, hito: Hito) -> None:
        """Añade una unidad atómica de seguimiento al caso."""
        self.hitos.append(hito)

    def cerrar(self) -> None:
        self.estado = EstadoCaso.CERRADO
        self.fecha_cierre = date.today()

    # Cumple UC2 — Modificar caso
    def modificar_descripcion(self, nueva_descripcion: str) -> None:
        """Actualiza la descripción narrativa del caso."""
        self.descripcion = nueva_descripcion

    # Cumple RF8 — Eliminación con borrado lógico
    def eliminar_logicamente(self) -> None:
        """Marca el caso como eliminado sin destruir la trazabilidad."""
        self.eliminado = True
        self.estado = EstadoCaso.ELIMINADO
        self.fecha_cierre = date.today()

    # Cumple UC9 — Acceder carpeta: lista plana de todos los documentos del caso
    def carpeta_documentos(self) -> list[Documento]:
        """Devuelve todos los documentos adjuntos a cualquier hito del caso."""
        docs: list[Documento] = []
        for hito in self.hitos:
            docs.extend(hito.documentos)
        return docs


@dataclass
class Involucrado:
    """DTO para UC5 — Ver involucrados de un caso."""
    rol: str
    id_persona: int
    nombre: str
    detalle: str = ""


@dataclass
class Reporte:
    id_reporte: int
    fecha_emision: datetime = field(default_factory=datetime.now)
    id_caso: Optional[int] = None
    id_estudiante: Optional[int] = None
    contenido: str = ""
