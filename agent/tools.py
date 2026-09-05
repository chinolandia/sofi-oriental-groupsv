# agent/tools.py — Herramientas del agente
# Generado por AgentKit

"""
Herramientas especificas del negocio (Oriental Group).

OJO: estas funciones NO se ejecutan solas todavia. La informacion del negocio le llega
a Sofi por el system prompt (config/prompts.yaml), asi que para CONTESTAR preguntas no
hace falta nada de aca. Este archivo es el lugar para las ACCIONES —registrar un lead,
armar un pedido, dejar a alguien en seguimiento, escalar a un asesor— y conectarlas al
ciclo de tool use de Claude es un paso aparte.

Casos de uso elegidos en la entrevista:
  - Calificar y atender leads / ventas
  - Tomar pedidos por WhatsApp
  - Dar seguimiento a quienes preguntaron y no respondieron
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

logger = logging.getLogger("agentkit")

CARPETA_KNOWLEDGE = Path("knowledge")
CARPETA_DATOS = Path("data")
CARPETA_DATOS.mkdir(exist_ok=True)

ARCHIVO_LEADS = CARPETA_DATOS / "leads.jsonl"
ARCHIVO_PEDIDOS = CARPETA_DATOS / "pedidos.jsonl"
ARCHIVO_SEGUIMIENTO = CARPETA_DATOS / "seguimiento.jsonl"

# El Salvador no aplica horario de verano: siempre UTC-6.
TZ_EL_SALVADOR = timezone(timedelta(hours=-6))

FORMAS_DE_PAGO = ("contra entrega", "transferencia bancaria", "enlace de pago")


# ── Info del negocio ────────────────────────────────────────────────────


def cargar_info_negocio() -> dict:
    """Carga la informacion del negocio desde config/business.yaml."""
    try:
        with open("config/business.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.error("config/business.yaml no encontrado")
        return {}


def obtener_horario() -> dict:
    """
    Retorna el horario de atencion y si el negocio esta abierto ahora.

    Oriental Group atiende de lunes a domingo, de 6:00 a 23:00 (hora de El Salvador).
    """
    info = cargar_info_negocio()
    # business.yaml (modelo multi-tienda): el horario general vive en "defaults".
    horario_texto = (
        info.get("defaults", {}).get("horario")
        or info.get("negocio", {}).get("horario")  # compat formato viejo
        or "Lunes a Domingo, de 6:00am a 11:00pm"
    )
    hora_local = datetime.now(TZ_EL_SALVADOR)
    esta_abierto = 6 <= hora_local.hour < 23
    return {
        "horario": horario_texto,
        "esta_abierto": esta_abierto,
        "hora_local": hora_local.strftime("%A %H:%M"),
    }


def buscar_en_knowledge(consulta: str) -> str:
    """
    Busca informacion en los archivos de texto de /knowledge.
    Retorna los fragmentos que coinciden con la consulta.

    (Los PDF del negocio ya estan incorporados textualmente en el system prompt; esta
    funcion sirve para archivos .txt / .md / .csv que se agreguen despues.)
    """
    if not CARPETA_KNOWLEDGE.is_dir():
        return "No hay archivos de conocimiento disponibles."

    resultados = []
    for ruta in sorted(CARPETA_KNOWLEDGE.iterdir()):
        if ruta.name.startswith(".") or not ruta.is_file():
            continue
        try:
            contenido = ruta.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binarios y archivos ilegibles se saltean
        if consulta.lower() in contenido.lower():
            resultados.append(f"[{ruta.name}]: {contenido[:500]}")

    if resultados:
        return "\n---\n".join(resultados)
    return "No encontre informacion especifica sobre eso en mis archivos."


# ── Utilidad interna ───────────────────────────────────────────────────


def _anexar(archivo: Path, registro: dict) -> dict:
    """Agrega una linea JSON al archivo indicado y devuelve el registro con timestamp."""
    registro = {"creado_en": datetime.now(TZ_EL_SALVADOR).isoformat(), **registro}
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    logger.info(f"Registro guardado en {archivo.name}: {registro}")
    return registro


# ── Leads / ventas ─────────────────────────────────────────────────────


def registrar_lead(
    telefono: str,
    nombre: str = "",
    producto_interes: str = "",
    origen: str = "whatsapp",
    notas: str = "",
) -> dict:
    """
    Guarda un lead: alguien que pregunto por un producto y todavia no compra.
    Se usa apenas se identifica el interes, aunque falten datos.
    """
    return _anexar(
        ARCHIVO_LEADS,
        {
            "telefono": telefono,
            "nombre": nombre,
            "producto_interes": producto_interes,
            "origen": origen,
            "notas": notas,
            "estado": "nuevo",
        },
    )


def calificar_lead(telefono: str, producto_interes: str, presupuesto_ok: bool | None = None,
                   listo_para_comprar: bool = False, notas: str = "") -> dict:
    """
    Marca que tan avanzado esta un lead. 'caliente' = quiere comprar ya;
    'tibio' = interesado con dudas; 'frio' = solo curiosea.
    """
    if listo_para_comprar:
        temperatura = "caliente"
    elif producto_interes:
        temperatura = "tibio"
    else:
        temperatura = "frio"
    return _anexar(
        ARCHIVO_LEADS,
        {
            "telefono": telefono,
            "producto_interes": producto_interes,
            "presupuesto_ok": presupuesto_ok,
            "listo_para_comprar": listo_para_comprar,
            "temperatura": temperatura,
            "notas": notas,
            "estado": "calificado",
        },
    )


def escalar_a_asesor(telefono: str, nombre: str = "", motivo: str = "", contexto: str = "") -> dict:
    """
    Deja constancia de que este cliente necesita que lo contacte una persona
    (precio no disponible, reclamo, caso especial).
    """
    return _anexar(
        ARCHIVO_LEADS,
        {
            "telefono": telefono,
            "nombre": nombre,
            "motivo": motivo,
            "contexto": contexto,
            "estado": "escalado_a_asesor",
        },
    )


# ── Pedidos ────────────────────────────────────────────────────────────


def crear_pedido(
    telefono: str,
    nombre: str,
    direccion: str,
    items: list[dict],
    forma_pago: str,
    referencia: str = "",
    notas: str = "",
) -> dict:
    """
    Registra un pedido. 'items' es una lista de {"producto": str, "cantidad": int}.

    Valida que no falte nada de lo obligatorio: producto(s), nombre, direccion y forma
    de pago. El pedido queda en estado 'pendiente_confirmacion' hasta que el cliente
    confirme el resumen.
    """
    faltantes = []
    if not nombre:
        faltantes.append("nombre")
    if not direccion:
        faltantes.append("direccion")
    if not items:
        faltantes.append("productos")
    if forma_pago not in FORMAS_DE_PAGO:
        faltantes.append(f"forma_pago (una de: {', '.join(FORMAS_DE_PAGO)})")

    if faltantes:
        return {"ok": False, "faltan": faltantes}

    pedido = _anexar(
        ARCHIVO_PEDIDOS,
        {
            "telefono": telefono,
            "nombre": nombre,
            "direccion": direccion,
            "referencia": referencia,
            "items": items,
            "forma_pago": forma_pago,
            "notas": notas,
            "estado": "pendiente_confirmacion",
        },
    )
    return {"ok": True, "pedido": pedido}


def confirmar_pedido(telefono: str, notas: str = "") -> dict:
    """
    Marca el ultimo pedido del cliente como confirmado por el.
    A partir de aca ya no se puede modificar una vez despachado.
    """
    return _anexar(
        ARCHIVO_PEDIDOS,
        {"telefono": telefono, "notas": notas, "estado": "confirmado"},
    )


def cancelar_pedido(telefono: str, motivo: str = "") -> dict:
    """
    Registra la cancelacion de un pedido. Solo aplica si todavia no fue despachado
    (esa validacion la hace el equipo, aca solo queda la constancia).
    """
    return _anexar(
        ARCHIVO_PEDIDOS,
        {"telefono": telefono, "motivo": motivo, "estado": "cancelacion_solicitada"},
    )


# ── Seguimiento (re-enganche) ─────────────────────────────────────────


def programar_seguimiento(
    telefono: str, producto_interes: str, nombre: str = "", cuando_horas: int = 24,
    notas: str = "",
) -> dict:
    """
    Deja a un cliente en la lista de seguimiento: pregunto por un producto y dejo de
    responder. 'cuando_horas' es en cuanto tiempo conviene volver a escribirle.

    OJO con la ventana de 24 h de WhatsApp: si el reintento cae despues de 24 h desde
    el ultimo mensaje del cliente, hay que usar una plantilla aprobada por Meta, no
    texto libre. Este registro es la base para ese proceso; enviarlo es un paso aparte.
    """
    recordar_en = datetime.now(TZ_EL_SALVADOR) + timedelta(hours=cuando_horas)
    return _anexar(
        ARCHIVO_SEGUIMIENTO,
        {
            "telefono": telefono,
            "nombre": nombre,
            "producto_interes": producto_interes,
            "recordar_en": recordar_en.isoformat(),
            "notas": notas,
            "estado": "pendiente",
        },
    )


def seguimientos_pendientes() -> list[dict]:
    """
    Devuelve los seguimientos cuya hora de recordatorio ya paso.
    Util para un job que corra cada cierto tiempo y dispare los re-enganches.
    """
    if not ARCHIVO_SEGUIMIENTO.exists():
        return []

    ahora_local = datetime.now(TZ_EL_SALVADOR)
    pendientes = []
    for linea in ARCHIVO_SEGUIMIENTO.read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        try:
            registro = json.loads(linea)
        except json.JSONDecodeError:
            continue
        if registro.get("estado") != "pendiente":
            continue
        try:
            recordar_en = datetime.fromisoformat(registro["recordar_en"])
        except (KeyError, ValueError):
            continue
        if recordar_en <= ahora_local:
            pendientes.append(registro)
    return pendientes
