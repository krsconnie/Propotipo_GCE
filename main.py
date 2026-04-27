"""
main.py - Punto de entrada y simulación (Versión Texto Plano)
Sistema de Gestión de Convivencia Escolar — Panoptes
"""

from models import Coordinador, ProfesorJefe, Documento
from repositories import RepositorioConvivencia
from adapters import AdaptadorSistemaCurricular, ComponenteCorreoElectronico
from services import ConvivenciaApplicationService
from controllers import ControladorGestionCasos, ControladorReportes

# ── UTILIDADES DE LOG (TEXTO PLANO) ───────────────────────────────────────────

def ok(msg: str) -> None:
    print(f"[Main] -> ✓ {msg}")

def fail(msg: str) -> None:
    print(f"[Main] -> ✗ {msg}")

# ── INYECCIÓN DE DEPENDENCIAS ─────────────────────────────────────────────────

def build_container() -> tuple[ControladorGestionCasos, ControladorReportes]:
    repositorio          = RepositorioConvivencia()
    adaptador_curricular = AdaptadorSistemaCurricular()
    componente_correo    = ComponenteCorreoElectronico()

    service = ConvivenciaApplicationService(
        repositorio=repositorio,
        adaptador_curricular=adaptador_curricular,
        componente_correo=componente_correo,
    )

    return ControladorGestionCasos(service), ControladorReportes(service)

# ── ESCENARIO DE SIMULACIÓN ───────────────────────────────────────────────────

def ejecutar_simulacion() -> None:
    print("INICIANDO PANOPTES MVP...")
    
    # Inicialización
    ctrl_casos, ctrl_reportes = build_container()
    
    # Actores y Datos
    profesor_jefe = ProfesorJefe(id_pj=10, nombre="Ana Fuentes", id_curso=101)
    coordinador   = Coordinador(id_coordinador=30, nombre="Luisa Vargas")
    EMAIL_COORD   = "luisa.vargas@colegio.cl"
    EMAIL_APOD    = "apoderado.martinez@mail.com"

    # UC11 / UC1 — Registro de Incidente (Observación previa)
    r_inc = ctrl_casos.post_incidente(
        descripcion="Agresión verbal en recreo.",
        id_estudiante=1,
        id_productor=profesor_jefe.id_pj,
        gravedad="GRAVE"
    )
    if r_inc["success"]: ok("UC11: Incidente registrado.")

    # UC1 — Apertura de Caso formal
    r_caso = ctrl_casos.post_caso(
        descripcion="Seguimiento agresión verbal.",
        id_incidente=r_inc["data"].id_incidente,
        coordinador=coordinador,
        email_notificacion=EMAIL_COORD
    )
    if r_caso["success"]: ok("UC1: Caso formal abierto.")

    # UC2 — Modificación de Caso
    r_mod = ctrl_casos.patch_descripcion_caso(
        id_caso=r_caso["data"].id_caso,
        nueva_descripcion="Descripción actualizada con nuevos antecedentes.",
        coordinador=coordinador
    )
    if r_mod["success"]: ok("UC2: Descripción del caso modificada.")

    # UC6 / UC9 — Agregar Hito con documento
    doc = Documento(id_doc=1, descripcion="Evidencia acta")
    r_hito = ctrl_casos.patch_agregar_hito(
        id_caso=r_caso["data"].id_caso,
        descripcion_hito="Reunión con apoderados.",
        email_notificacion=EMAIL_APOD,
        documentos=[doc]
    )
    if r_hito["success"]: ok("UC6/UC9: Hito añadido con documento.")

    # UC8 — Modificar Hito (Actualización de hito existente)
    r_mod_hito = ctrl_casos.patch_modificar_hito(
        id_caso=r_caso["data"].id_caso,
        id_hito=r_hito["data"].id_hito,
        nueva_descripcion="Reunión con apoderados y psicólogo escolar (actualizado).",
        coordinador=coordinador
    )
    if r_mod_hito["success"]: ok("UC8: Hito modificado exitosamente.")

    # UC5 — Ver involucrados
    r_inv = ctrl_casos.get_involucrados(r_caso["data"].id_caso)
    if r_inv["success"]: ok(f"UC5: Lista de {len(r_inv['data'])} involucrados generada.")

    # UC10 / UC7 / UC3 — Reportes y Visualización
    ctrl_reportes.get_reporte_caso(r_caso["data"].id_caso)
    ctrl_reportes.get_reporte_estudiante(1)
    ok("UC10/UC7: Reportes generados.")

    # UC13 — Consultar auditoría (NUEVO)
    r_aud = ctrl_reportes.get_auditoria(1)
    if r_aud["success"]: ok("UC13: Reporte de auditoría de estudiante generado.")

    # UC2 — Cierre de Caso
    r_fin = ctrl_casos.patch_cerrar_caso(r_caso["data"].id_caso, coordinador)
    if r_fin["success"]: ok(f"UC2: Simulación terminada. Caso #{r_fin['data'].id_caso} cerrado.")

    print("\nPANOPTES MVP FINALIZADO CORRECTAMENTE.")

if __name__ == "__main__":
    ejecutar_simulacion()