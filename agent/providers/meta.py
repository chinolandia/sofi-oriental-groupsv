# agent/providers/meta.py — Adaptador para Meta WhatsApp Cloud API
# Generado por AgentKit

"""
Conexion directa contra la API oficial de Meta.
Documentacion: https://developers.facebook.com/docs/whatsapp/cloud-api
"""

import hashlib
import hmac
import logging
import os

import httpx
from fastapi import Request

from agent.providers.base import MensajeEntrante, ProveedorWhatsApp

logger = logging.getLogger("agentkit")


class ProveedorMeta(ProveedorWhatsApp):
    """Proveedor de WhatsApp usando la API oficial de Meta (Cloud API)."""

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN", "")
        self.phone_number_id = os.getenv("META_PHONE_NUMBER_ID", "")
        # Mismo cuidado que en zernio.py: una variable declarada pero vacia en el .env
        # devuelve "" y no el default, asi que se usa "or".
        self.verify_token = os.getenv("META_VERIFY_TOKEN") or "agentkit-verify"
        self.app_secret = os.getenv("META_APP_SECRET", "")
        self.api_version = os.getenv("META_API_VERSION") or "v25.0"

        if not self.access_token or not self.phone_number_id:
            logger.warning(
                "Faltan META_ACCESS_TOKEN o META_PHONE_NUMBER_ID: el agente no va a poder responder"
            )
        if not self.app_secret:
            logger.warning(
                "META_APP_SECRET no esta configurado: los webhooks NO se verifican. "
                "Sirve para probar, pero no lo dejes asi en produccion."
            )

    # ── Recibir ──────────────────────────────────────────────────────────

    async def validar_webhook(self, request: Request) -> str | None:
        """
        Meta hace un GET con hub.challenge la primera vez, para comprobar que la URL es tuya.
        Hay que devolver el challenge tal cual, como texto plano.
        """
        params = request.query_params
        if (
            params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == self.verify_token
        ):
            return params.get("hub.challenge") or ""
        return None

    async def verificar_firma(self, request: Request) -> bool:
        """Compara el header X-Hub-Signature-256 contra el HMAC-SHA256 del cuerpo crudo."""
        if not self.app_secret:
            return True  # modo pruebas, ya se advirtio al arrancar

        cabecera = request.headers.get("X-Hub-Signature-256", "")
        if not cabecera.startswith("sha256="):
            logger.warning("Llego un webhook sin firma X-Hub-Signature-256: rechazado")
            return False

        cuerpo = await request.body()
        firma_esperada = hmac.new(
            self.app_secret.encode("utf-8"), cuerpo, hashlib.sha256
        ).hexdigest()

        # Igual que en zernio.py: compare_digest sobre str exige ASCII puro y un header
        # con bytes raros tiraria TypeError, devolviendo 500 en vez de 401.
        try:
            iguales = hmac.compare_digest(firma_esperada, cabecera.removeprefix("sha256="))
        except TypeError:
            logger.warning("La firma del webhook trae caracteres invalidos: rechazado")
            return False

        if not iguales:
            logger.warning("Firma de webhook invalida: rechazado")
            return False
        return True

    async def parsear_webhook(self, request: Request) -> list[MensajeEntrante]:
        """Recorre el payload anidado de Meta Cloud API."""
        body = await request.json()
        mensajes: list[MensajeEntrante] = []

        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value") or {}

                # El numero de WhatsApp del negocio al que llego el mensaje.
                phone_number_id = (value.get("metadata") or {}).get("phone_number_id", "")

                # Nombre del cliente segun su perfil de WhatsApp (si viene).
                nombre_cliente = ""
                contactos = value.get("contacts") or []
                if contactos:
                    nombre_cliente = (contactos[0].get("profile") or {}).get("name", "")

                for msg in value.get("messages", []):
                    if msg.get("type") != "text":
                        continue  # por ahora solo texto

                    contexto = {
                        "evento_id": msg.get("id", ""),
                        "phone_number_id": phone_number_id,
                    }
                    if nombre_cliente:
                        contexto["nombre_cliente"] = nombre_cliente
                    # "referral" solo viene en el PRIMER mensaje de una conversacion
                    # iniciada desde un anuncio de Facebook/Instagram. Sirve para saber
                    # de que tienda del paraguas viene el cliente.
                    referral = msg.get("referral")
                    if referral:
                        contexto["referral"] = referral

                    mensajes.append(
                        MensajeEntrante(
                            telefono=msg.get("from", ""),
                            texto=(msg.get("text") or {}).get("body", ""),
                            mensaje_id=msg.get("id", ""),
                            # Meta solo entrega mensajes entrantes por este canal
                            es_propio=False,
                            contexto=contexto,
                        )
                    )
        return mensajes

    # ── Enviar ───────────────────────────────────────────────────────────

    async def enviar_mensaje(
        self, telefono: str, mensaje: str, contexto: dict | None = None
    ) -> bool:
        """
        Envia un mensaje de texto por la Cloud API.

        Responde desde el MISMO numero al que escribio el cliente: si el contexto
        trae phone_number_id (lo pone parsear_webhook), se usa ese; si no, el del .env.
        """
        contexto = contexto or {}
        # Se prioriza el numero configurado en el .env (META_PHONE_NUMBER_ID): con un
        # solo numero de WhatsApp para todo el paraguas, SIEMPRE se responde desde ese.
        # El del contexto queda como respaldo por si algun dia el .env no lo trae.
        # (Ademas, los payloads de prueba de Meta traen un phone_number_id falso.)
        phone_number_id = self.phone_number_id or contexto.get("phone_number_id")

        if not self.access_token or not phone_number_id:
            logger.error("No se puede enviar: faltan META_ACCESS_TOKEN o META_PHONE_NUMBER_ID")
            return False

        url = f"https://graph.facebook.com/{self.api_version}/{phone_number_id}/messages"

        try:
            async with httpx.AsyncClient(timeout=30.0) as cliente:
                r = await cliente.post(
                    url,
                    json={
                        "messaging_product": "whatsapp",
                        "to": telefono,
                        "type": "text",
                        "text": {"body": mensaje},
                    },
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json",
                    },
                )
        except httpx.HTTPError as e:
            logger.error(f"Error de red hablando con Meta: {e}")
            return False

        if r.status_code == 200:
            return True

        logger.error(f"Meta rechazo el envio [{r.status_code}]: {r.text[:500]}")
        return False

    # ── Diagnostico ──────────────────────────────────────────────────────

    async def verificar_conexion(self) -> tuple[bool, str]:
        """Lee el numero desde la Graph API para confirmar que el token sirve."""
        if not self.access_token or not self.phone_number_id:
            return False, "Faltan META_ACCESS_TOKEN o META_PHONE_NUMBER_ID"

        try:
            async with httpx.AsyncClient(timeout=15.0) as cliente:
                r = await cliente.get(
                    f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}",
                    params={"fields": "display_phone_number,verified_name,quality_rating"},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                )
        except httpx.HTTPError as e:
            return False, f"No se pudo contactar a Meta: {e}"

        if r.status_code != 200:
            return False, f"Meta respondio {r.status_code}: {r.text[:200]}"

        datos = r.json()
        return True, (
            f"Numero {datos.get('display_phone_number', '?')} conectado "
            f"(calidad: {datos.get('quality_rating', '?')})"
        )
