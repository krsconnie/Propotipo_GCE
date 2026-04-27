"""
services.py - Capa de aplicación (Application Service)
Orquesta la lógica de negocio entre repositorios y adaptadores.
Sistema de Gestión de Convivencia Escolar — Panoptes

Glosario en uso:
  · Hito     = Unidad atómica de seguimiento
  · Incidente = Observación previa (puede o no derivar en Caso)
"""

from datetime import date
from typing import Optional

from models import (
    Incidente, Caso, Hito, Documento, Reporte, Involucrado,
    EstadoCaso, NivelGravedad, Coordinador
)
from repositories import RepositorioConvivencia
from adapters import AdaptadorSistemaCurricular, ComponenteCorreoElectronico


COMPONENT = "Backend"


class ConvivenciaApplicationService:
    """
    Servicio de aplicación central. Coordina el flujo completo de negocio
    entre controladores, repositorio y adaptadores externos.
    Inyección de dependencias vía constructor (Arquitectura Hexagonal).
    """

    def __init__(
        self,
        repositorio: RepositorioConvivencia,
        adaptador_curricular: AdaptadorSistemaCurricular,
        componente_correo: ComponenteCorreoElectronico,
    ) -> None:
        self._repo = repositorio
        self._curricular = adaptador_curricular
        self._correo = componente_correo
        self._hito_counter: int = 1
        self._doc_counter: int = 1

    # ── Incidentes (observaciones previas) ────────────────────────────────────

    def registrar_incidente(
        self,
        descripcion: str,
        id_estudiante: int,
        id_productor: int,
        gravedad: NivelGravedad = NivelGravedad.LEVE,
    ) -> Optional[Incidente]:
        """
        UC1 — Registrar observación previa (Incidente).
        Valida al estudiante en el Sistema Curricular y, si es válido,
        persiste el incidente como observación previa.
        """
        print(f"\n[{COMPONENT}] -> Iniciando registro de observación previa para estudiante #{id_estudiante}.")

        estudiante = self._curricular.verificar_estudiante(id_estudiante)
        if not estudiante:
            print(f"[{COMPONENT}] -> ERROR: No se puede registrar la observación. Estudiante inválido.")
            return None

        incidente = Incidente(
            id_incidente=0,
            descripcion=descripcion,
            id_estudiante=id_estudiante,
            id_productor=id_productor,
            gravedad=gravedad,
        )
        incidente = self._repo.guardar_incidente(incidente)
        print(f"[{COMPONENT}] -> Observación previa #{incidente.id_incidente} registrada con gravedad '{gravedad}'.")
        return incidente

    # ── Casos ─────────────────────────────────────────────────────────────────

    def abrir_caso(
        self,
        descripcion: str,
        id_incidente: int,
        coordinador: Coordinador,
        email_notificacion: str,
    ) -> Optional[Caso]:
        """
        UC3 — Abrir Caso formal a partir de una observación previa (Incidente).
        Notifica al destinatario indicado vía correo electrónico.
        """
        print(f"\n[{COMPONENT}] -> Coordinador '{coordinador.nombre}' solicita apertura de caso formal.")

        incidente = self._repo.obtener_incidente(id_incidente)
        if not incidente:
            print(f"[{COMPONENT}] -> ERROR: Observación previa #{id_incidente} no encontrada. No se puede abrir caso.")
            return None

        caso = Caso(
            id_caso=0,
            descripcion=descripcion,
            id_estudiante=incidente.id_estudiante,
            id_coordinador=coordinador.id_coordinador,
            incidentes=[id_incidente],
        )
        caso = self._repo.guardar_caso(caso)

        # Vincular observación previa al caso
        incidente.id_caso_asociado = caso.id_caso
        self._repo.guardar_incidente(incidente)

        # Notificación de apertura
        self._correo.notificar_apertura_caso(
            destinatario=email_notificacion,
            id_caso=caso.id_caso,
            descripcion=descripcion,
        )

        print(f"[{COMPONENT}] -> Caso #{caso.id_caso} abierto exitosamente.")
        return caso

    # Cumple UC2 — Modificar caso
    def modificar_descripcion_caso(
        self,
        id_caso: int,
        nueva_descripcion: str,
        coordinador: Coordinador,
    ) -> Optional[Caso]:
        """UC2 — Permite al Coordinador actualizar la descripción narrativa del caso."""
        print(f"\n[{COMPONENT}] -> Coordinador '{coordinador.nombre}' solicita modificar descripción del Caso #{id_caso}.")

        caso = self._repo.obtener_caso(id_caso)
        if not caso:
            print(f"[{COMPONENT}] -> ERROR: Caso #{id_caso} no encontrado.")
            return None
        if caso.eliminado:
            print(f"[{COMPONENT}] -> ERROR: El Caso #{id_caso} está eliminado y no puede modificarse.")
            return None

        caso.modificar_descripcion(nueva_descripcion)
        self._repo.actualizar_caso(caso)
        print(f"[{COMPONENT}] -> Caso #{id_caso}: descripción actualizada correctamente.")
        return caso

    def agregar_hito_a_caso(
        self,
        id_caso: int,
        descripcion_hito: str,
        email_notificacion: str,
        documentos: Optional[list[Documento]] = None,
    ) -> Optional[Hito]:
        """
        UC6 — Añadir una unidad atómica (Hito) a un Caso existente y notificar.
        Cumple RF7 — Registro de hitos con documentos adjuntos.
        """
        print(f"\n[{COMPONENT}] -> Agregando unidad atómica (hito) al Caso #{id_caso}.")

        caso = self._repo.obtener_caso(id_caso)
        if not caso:
            print(f"[{COMPONENT}] -> ERROR: Caso #{id_caso} no encontrado.")
            return None

        hito = Hito(
            id_hito=self._hito_counter,
            descripcion=descripcion_hito,
            fecha=date.today(),
        )
        self._hito_counter += 1

        if documentos:
            for doc in documentos:
                hito.agregar_documento(doc)
            print(f"[{COMPONENT}] -> {len(documentos)} documento(s) adjuntado(s) a la unidad atómica.")

        caso.agregar_hito(hito)
        self._repo.actualizar_caso(caso)

        # Notificación de nueva unidad atómica
        self._correo.notificar_nuevo_hito(
            destinatario=email_notificacion,
            id_caso=id_caso,
            desc_hito=descripcion_hito,
        )

        print(f"[{COMPONENT}] -> Unidad atómica (Hito) #{hito.id_hito} agregada al Caso #{id_caso}.")
        return hito

    # Cumple UC8 — Modificar hito (unidad atómica)
    def modificar_hito(
        self,
        id_caso: int,
        id_hito: int,
        nueva_descripcion: str,
        coordinador: Coordinador,
    ) -> Optional[Hito]:
        """
        UC8 — Permite al Coordinador corregir o ampliar el contenido de una
        unidad atómica (Hito) ya registrada en un Caso.
        """
        print(f"\n[{COMPONENT}] -> Coordinador '{coordinador.nombre}' solicita modificar "
              f"unidad atómica (Hito) #{id_hito} del Caso #{id_caso}.")

        caso = self._repo.obtener_caso(id_caso)
        if not caso:
            print(f"[{COMPONENT}] -> ERROR: Caso #{id_caso} no encontrado.")
            return None

        hito_objetivo: Optional[Hito] = None
        for h in caso.hitos:
            if h.id_hito == id_hito:
                hito_objetivo = h
                break

        if not hito_objetivo:
            print(f"[{COMPONENT}] -> ERROR: Unidad atómica (Hito) #{id_hito} no pertenece al Caso #{id_caso}.")
            return None

        hito_objetivo.modificar_descripcion(nueva_descripcion)
        self._repo.actualizar_caso(caso)
        print(f"[{COMPONENT}] -> Unidad atómica #{id_hito} modificada correctamente.")
        return hito_objetivo

    # Cumple UC5 — Ver involucrados
    def obtener_involucrados(self, id_caso: int) -> list[Involucrado]:
        """
        UC5 — Devuelve una lista estructurada (DTO Involucrado) de todas las
        personas relacionadas con el caso: Estudiante, Productor(es), Coordinador.
        """
        print(f"\n[{COMPONENT}] -> Construyendo lista de involucrados para el Caso #{id_caso}.")

        caso = self._repo.obtener_caso(id_caso)
        if not caso:
            print(f"[{COMPONENT}] -> ERROR: Caso #{id_caso} no encontrado.")
            return []

        involucrados: list[Involucrado] = []

        # Estudiante (vía Sistema Curricular)
        estudiante = self._curricular.verificar_estudiante(caso.id_estudiante)
        if estudiante:
            involucrados.append(Involucrado(
                rol="Estudiante",
                id_persona=estudiante.id_estudiante,
                nombre=estudiante.nombre,
                detalle=f"Curso: {estudiante.nombre_curso}",
            ))

        # Productores: todos los que generaron observaciones previas vinculadas
        ids_productores_vistos: set[int] = set()
        for id_inc in caso.incidentes:
            inc = self._repo.obtener_incidente(id_inc)
            if inc and inc.id_productor not in ids_productores_vistos:
                ids_productores_vistos.add(inc.id_productor)
                involucrados.append(Involucrado(
                    rol="Productor", 
                    id_persona=inc.id_productor,
                    nombre=f"Productor ID#{inc.id_productor}",
                    detalle=f"Generó la observación previa #{inc.id_incidente}",
                ))

        # Coordinador
        involucrados.append(Involucrado(
            rol="Coordinador",
            id_persona=caso.id_coordinador,
            nombre=f"Coordinador ID#{caso.id_coordinador}",
            detalle="Responsable de la gestión del caso.",
        ))

        print(f"[{COMPONENT}] -> {len(involucrados)} involucrado(s) identificados en el Caso #{id_caso}.")
        return involucrados

    # Cumple UC9 — Acceder carpeta de documentos
    def acceder_carpeta_caso(self, id_caso: int) -> list[dict]:
        """
        UC9 — Devuelve una vista estructurada (simulada) de todos los archivos
        adjuntos a cualquier unidad atómica (Hito) del Caso.
        """
        print(f"\n[{COMPONENT}] -> Accediendo a carpeta de documentos del Caso #{id_caso}.")

        caso = self._repo.obtener_caso(id_caso)
        if not caso:
            print(f"[{COMPONENT}] -> ERROR: Caso #{id_caso} no encontrado.")
            return []

        carpeta: list[dict] = []
        for hito in caso.hitos:
            for doc in hito.documentos:
                carpeta.append({
                    "id_hito"    : hito.id_hito,
                    "desc_hito"  : hito.descripcion[:50],
                    "id_doc"     : doc.id_doc,
                    "descripcion": doc.descripcion,
                    "url"        : doc.url or "[sin URL]",
                    "fecha"      : str(doc.fecha_adjunto),
                    "acceso"     : "SIMULADO — archivo disponible en almacén de evidencias",
                })

        print(f"[{COMPONENT}] -> Carpeta del Caso #{id_caso}: {len(carpeta)} documento(s) encontrados.")
        return carpeta

    # Cumple RF8 — Eliminación lógica de caso
    def eliminar_caso(self, id_caso: int, coordinador: Coordinador) -> Optional[Caso]:
        """
        RF8 — Borrado lógico: el Caso se marca como ELIMINADO pero el registro
        permanece en el repositorio para garantizar trazabilidad total.
        """
        print(f"\n[{COMPONENT}] -> Coordinador '{coordinador.nombre}' solicita eliminación lógica del Caso #{id_caso}.")

        caso = self._repo.eliminar_caso(id_caso)
        if not caso:
            print(f"[{COMPONENT}] -> ERROR: Caso #{id_caso} no encontrado.")
            return None

        print(f"[{COMPONENT}] -> RF8 cumplido: Caso #{id_caso} eliminado lógicamente (dato preservado).")
        return caso

    def cerrar_caso(self, id_caso: int, coordinador: Coordinador) -> Optional[Caso]:
        """UC4 — Cierra un caso y registra la fecha de cierre."""
        print(f"\n[{COMPONENT}] -> Coordinador '{coordinador.nombre}' solicita cierre del Caso #{id_caso}.")

        caso = self._repo.obtener_caso(id_caso)
        if not caso:
            print(f"[{COMPONENT}] -> ERROR: Caso #{id_caso} no encontrado.")
            return None

        caso.cerrar()
        self._repo.actualizar_caso(caso)
        print(f"[{COMPONENT}] -> Caso #{id_caso} cerrado exitosamente.")
        return caso

    # ── Reportes ──────────────────────────────────────────────────────────────

    def generar_reporte_caso(self, id_caso: int) -> Optional[Reporte]:
        """UC7 / RF6 — Genera un reporte detallado de un caso específico."""
        print(f"\n[{COMPONENT}] -> Generando reporte para el Caso #{id_caso}.")

        caso = self._repo.obtener_caso(id_caso)
        if not caso:
            print(f"[{COMPONENT}] -> ERROR: Caso #{id_caso} no encontrado.")
            return None

        lineas = [
            f"═══ REPORTE DEL CASO #{caso.id_caso} ═══",
            f"Estado       : {caso.estado}",
            f"Descripción  : {caso.descripcion}",
            f"Fecha inicio : {caso.fecha_inicio}",
            f"Fecha cierre : {caso.fecha_cierre or 'Aún abierto'}",
            f"Observaciones previas (Incidentes): {caso.incidentes}",
            f"Unidades atómicas (Hitos) [{len(caso.hitos)}]:",
        ]
        for h in caso.hitos:
            lineas.append(f"  • [{h.fecha}] {h.descripcion}")
            for d in h.documentos:
                lineas.append(f"      - Doc #{d.id_doc}: {d.descripcion}  [{d.url or 'sin URL'}]")

        contenido = "\n".join(lineas)

        reporte = Reporte(
            id_reporte=0,
            id_caso=id_caso,
            id_estudiante=caso.id_estudiante,
            contenido=contenido,
        )
        reporte = self._repo.guardar_reporte(reporte)
        print(f"[{COMPONENT}] -> Reporte #{reporte.id_reporte} generado.")
        return reporte

    def generar_reporte_estudiante(self, id_estudiante: int) -> Optional[Reporte]:
        """UC7 — Genera un reporte de todos los casos de un estudiante."""
        print(f"\n[{COMPONENT}] -> Generando reporte de casos para el estudiante #{id_estudiante}.")

        estudiante = self._curricular.verificar_estudiante(id_estudiante)
        if not estudiante:
            return None

        casos = [c for c in self._repo.listar_casos() if c.id_estudiante == id_estudiante]
        incidentes = [i for i in self._repo.listar_incidentes() if i.id_estudiante == id_estudiante]

        lineas = [
            f"═══ REPORTE DE ESTUDIANTE: {estudiante.nombre} (#{id_estudiante}) ═══",
            f"Curso                          : {estudiante.nombre_curso}",
            f"Total casos activos            : {len(casos)}",
            f"Total observaciones previas    : {len(incidentes)}",
        ]
        for c in casos:
            lineas.append(f"  • Caso #{c.id_caso} [{c.estado}]: {c.descripcion[:50]}")

        contenido = "\n".join(lineas)
        reporte = Reporte(
            id_reporte=0,
            id_estudiante=id_estudiante,
            contenido=contenido,
        )
        reporte = self._repo.guardar_reporte(reporte)
        print(f"[{COMPONENT}] -> Reporte #{reporte.id_reporte} de estudiante generado.")
        return reporte

# Cumple UC13 — Consultar auditoría
    def generar_auditoria_estudiante(self, id_estudiante: int) -> Optional[Reporte]:
        """
        UC13 — Permite al estudiante (o auditores) revisar el historial 
        de acciones y estados de sus casos para asegurar transparencia.
        """
        print(f"\n[{COMPONENT}] -> Generando registro de auditoría para estudiante #{id_estudiante}.")
        
        # Recuperamos todo, incluso lo "eliminado" para transparencia total (RF8)
        casos = [c for c in self._repo.listar_casos(incluir_eliminados=True) 
                 if c.id_estudiante == id_estudiante]
        
        lineas = [f"═══ REGISTRO DE AUDITORÍA — ESTUDIANTE #{id_estudiante} ═══"]
        for c in casos:
            audit_status = "[ELIMINADO LÓGICAMENTE]" if c.eliminado else f"[{c.estado}]"
            lineas.append(f"  • Caso #{c.id_caso} {audit_status}: {c.descripcion[:60]}")
            lineas.append(f"    - Inicio: {c.fecha_inicio} | Cierre: {c.fecha_cierre or 'N/A'}")
        
        reporte = Reporte(id_reporte=0, id_estudiante=id_estudiante, contenido="\n".join(lineas))
        return self._repo.guardar_reporte(reporte)