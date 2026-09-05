# agent/tiendas.py — Registro de tiendas del paraguas y detección por anuncio
# Generado por AgentKit

"""
Oriental Group agrupa varias tiendas. Cada mensaje pertenece a UNA tienda.

Deteccion (Opcion B): con un solo numero de WhatsApp compartido, se identifica la
tienda por el anuncio de Facebook/Instagram de origen. El primer mensaje de una
conversacion iniciada desde un anuncio trae un objeto "referral":

    referral = {
        "source_url": "https://fb.me/...",
        "source_id":  "<AD_ID>",
        "source_type": "ad" | "post",
        "headline": "...",
        "body": "...",            # texto del anuncio
        "media_type": "image" | "video",
        ...
    }

Solo el PRIMER mensaje trae referral. Por eso, una vez detectada, la tienda se
fija para esa conversacion (agent/memory.py) y los mensajes siguientes la
recuperan de ahi.
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger("agentkit")

CONFIG_DIR = Path("config")
BUSINESS_YAML = CONFIG_DIR / "business.yaml"
TIENDAS_DIR = CONFIG_DIR / "tiendas"

_cache: dict | None = None


def _cargar() -> dict:
    """Lee business.yaml + todas las fichas de tienda una sola vez y cachea."""
    global _cache
    if _cache is not None:
        return _cache

    try:
        with open(BUSINESS_YAML, "r", encoding="utf-8") as f:
            paraguas = yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.error("config/business.yaml no encontrado")
        paraguas = {}

    defaults = paraguas.get("defaults", {}) or {}
    tiendas: dict[str, dict] = {}

    for tienda_id in paraguas.get("tiendas", []) or []:
        ruta = TIENDAS_DIR / f"{tienda_id}.yaml"
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                ficha = yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.error(f"Ficha de tienda no encontrada: {ruta}")
            continue

        # Politicas: defaults del paraguas, sobrescritas por las de la tienda
        politicas = {**defaults, **(ficha.get("politicas") or {})}

        # Catalogo: se lee el archivo de texto referenciado
        catalogo_texto = ""
        cat_ruta = ficha.get("catalogo")
        if cat_ruta:
            try:
                catalogo_texto = Path(cat_ruta).read_text(encoding="utf-8").strip()
            except FileNotFoundError:
                logger.error(f"Catalogo no encontrado para {tienda_id}: {cat_ruta}")

        ficha["_politicas_efectivas"] = politicas
        ficha["_catalogo_texto"] = catalogo_texto
        tiendas[tienda_id] = ficha

    _cache = {"paraguas": paraguas, "tiendas": tiendas}
    return _cache


def recargar():
    """Fuerza releer la config (util en tests o tras editar los YAML)."""
    global _cache
    _cache = None


def tienda_por_defecto() -> str | None:
    """Tienda a usar si la deteccion falla. Puede ser None."""
    valor = _cargar()["paraguas"].get("agente", {}).get("tienda_por_defecto")
    if valor in (None, "", "null"):
        return None
    if valor not in _cargar()["tiendas"]:
        logger.warning(f"tienda_por_defecto '{valor}' no existe entre las tiendas activas")
        return None
    return valor


def existe(tienda_id: str | None) -> bool:
    return bool(tienda_id) and tienda_id in _cargar()["tiendas"]


def resolver_por_referral(referral: dict | None) -> str | None:
    """
    Devuelve el id de la tienda que corresponde al anuncio de origen, o None.

    Orden de prueba por tienda:
      1. source_id exacto en deteccion.ad_ids
      2. alguna palabra clave de deteccion.palabras_clave dentro de headline/body
      3. algun fragmento de deteccion.fuentes_url dentro de source_url
    """
    if not referral:
        return None

    source_id = str(referral.get("source_id") or "").strip()
    texto = " ".join(
        str(referral.get(k) or "") for k in ("headline", "body", "source_type")
    ).lower()
    source_url = str(referral.get("source_url") or "").lower()

    for tienda_id, ficha in _cargar()["tiendas"].items():
        det = ficha.get("deteccion") or {}

        ad_ids = [str(x).strip() for x in (det.get("ad_ids") or [])]
        if source_id and source_id in ad_ids:
            logger.info(f"Tienda '{tienda_id}' detectada por ad_id {source_id}")
            return tienda_id

        for palabra in det.get("palabras_clave") or []:
            if palabra and palabra.lower() in texto:
                logger.info(f"Tienda '{tienda_id}' detectada por palabra clave '{palabra}'")
                return tienda_id

        for frag in det.get("fuentes_url") or []:
            if frag and frag.lower() in source_url:
                logger.info(f"Tienda '{tienda_id}' detectada por source_url '{frag}'")
                return tienda_id

    logger.info("No se pudo detectar la tienda desde el referral")
    return None


def _bloque_politicas(politicas: dict) -> str:
    formas = politicas.get("formas_de_pago") or []
    datos = politicas.get("datos_para_pedido") or []
    lineas = [
        f"Horario de atención: {politicas.get('horario', 'no especificado')}",
        f"Envío: {politicas.get('envio', 'no especificado')}",
        f"Formas de pago: {', '.join(formas) if formas else 'no especificado'}",
        f"Para tomar un pedido pedí: {', '.join(datos) if datos else 'los datos necesarios'}",
        f"Devoluciones: {politicas.get('devoluciones', 'no especificado')}",
        f"Garantía: {politicas.get('garantia', 'no especificado')}",
        f"Reservas: {politicas.get('reservas', 'no especificado')}",
    ]
    if politicas.get("descuento_cantidad"):
        lineas.append(f"Descuento por cantidad: {politicas['descuento_cantidad'].strip()}")
    fuera = (
        "Fuera de horario respondé: \"Gracias por escribirnos. Nuestro horario es "
        f"{politicas.get('horario', '')}. Te respondemos apenas estemos disponibles.\""
    )
    lineas.append(fuera)
    return "\n".join(f"- {l}" for l in lineas)


def construir_bloque_tienda(tienda_id: str) -> str:
    """El trozo del system prompt propio de la tienda: identidad + politicas + catalogo."""
    datos = _cargar()
    ficha = datos["tiendas"].get(tienda_id)
    if not ficha:
        return bloque_sin_tienda()

    nombre = ficha.get("nombre", tienda_id)
    presentacion = (
        datos["paraguas"].get("agente", {}).get("presentacion", "Hola, soy Sofi de {tienda}.")
        .replace("{tienda}", nombre)
    )
    identidad = (ficha.get("identidad") or "").strip()
    tono = (ficha.get("tono") or "").strip()
    politicas = _bloque_politicas(ficha.get("_politicas_efectivas") or {})
    catalogo = ficha.get("_catalogo_texto") or "(catálogo vacío)"

    return (
        f"## Tienda que representás en esta conversación: {nombre}\n"
        f"Presentate así al inicio (una sola vez): \"{presentacion}\"\n"
        f"Sobre la tienda: {identidad}\n"
        + (f"Tono de esta tienda: {tono}\n" if tono else "")
        + f"\n## Políticas de {nombre}\n{politicas}\n"
        f"\n## Catálogo de la tienda (tu ÚNICA fuente de precios y especificaciones)\n{catalogo}"
    )


def bloque_sin_tienda() -> str:
    """Bloque a usar cuando no se pudo identificar la tienda."""
    datos = _cargar()
    sin = (
        datos["paraguas"].get("agente", {}).get("sin_tienda", "")
        or "Presentate solo como Sofi y preguntá por cuál producto escribe el cliente."
    ).strip()
    politicas = _bloque_politicas(datos["paraguas"].get("defaults", {}) or {})
    return (
        "## Todavía no sabés de qué tienda de Oriental Group viene este cliente\n"
        f"{sin}\n"
        "No des precios ni especificaciones de ningún producto hasta identificar "
        "la tienda y el producto.\n"
        f"\n## Políticas generales de Oriental Group (mientras tanto)\n{politicas}"
    )
