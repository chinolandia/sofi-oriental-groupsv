# Sofi — Estado del proyecto y pendientes

Fecha: 2026-09-06

## ✅ Lo que está funcionando en producción

- **Servidor**: FastAPI desplegado en Railway
  - Proyecto Railway: **robust-elegance**
  - Servicio: **sofi-oriental-groupsv**
  - URL: `https://sofi-oriental-groupsv-production.up.railway.app`
  - Health check: `GET /` → `{"status":"ok",...}`
  - Política de privacidad: `GET /privacy`
- **Base de datos**: PostgreSQL en Railway (historial de conversaciones + tienda por conversación)
- **IA**: Claude Sonnet 5 (API de Anthropic, con saldo prepago)
- **WhatsApp**: Meta Cloud API
  - Número actual: **+1 555 657 8622** (número de PRUEBA de Meta)
  - Phone Number ID: `1240950779110061`
  - WABA (cuenta de WhatsApp): `1455294849671713` ("Test WhatsApp Business Account", portafolio Chinolandia SV)
  - App de Meta: **Sofi-agente**, App ID `1572397533759270` — **publicada / Live**
  - App suscrita a la WABA `1455294849671713` (webhook funcionando)
  - Webhook: `https://sofi-oriental-groupsv-production.up.railway.app/webhook`, verify token `oriental-group-sofi-2026`, campo `messages` suscrito
- **Código**: `github.com/chinolandia/sofi-oriental-groupsv` (rama `main`).
  Push a `main` → Railway redespliega solo.
- **Catálogo**: 23 productos de Chinolandia SV en `knowledge/chinolandia-sv/catalogo.md`
- **Detección de tienda**: por anuncio de Facebook (objeto `referral`), con `chinolandia-sv` como tienda por defecto

## Variables de entorno en Railway (servicio sofi-oriental-groupsv)

```
ANTHROPIC_API_KEY      (key de workspace de Anthropic)
ANTHROPIC_MODEL        claude-sonnet-5
ANTHROPIC_EFFORT       low
WHATSAPP_PROVIDER      meta
META_ACCESS_TOKEN      (token permanente de System User, no expira)
META_PHONE_NUMBER_ID   1240950779110061   ← se cambia al migrar al número +503
META_VERIFY_TOKEN      oriental-group-sofi-2026
META_APP_SECRET        (App Secret de la app Sofi-agente)
ENVIRONMENT            production
DATABASE_URL           ${{Postgres.DATABASE_URL}}
```

Los valores reales están en el archivo local `.env` (NO se sube a GitHub).

---

## ⏳ Pendiente 1 — Número local +503 (bloqueado por Meta)

**Objetivo**: que Sofi use un número +503 en vez del +1 de prueba (credibilidad local).

**Estado del enredo actual** (a 2026-09-06):
- La **verificación del negocio** de Chinolandia SV está **"en curso"** (no aprobada).
- Hay 3 números +503 en distintas cuentas, todos "Fuera de internet":
  - `+503 7381 8504` — app de WhatsApp Business del celular (se usa como "cliente" en pruebas)
  - `+503 7082 7281` — WABA "Lo Veo Lo Quiero | Pedidos" (**otro portafolio comercial**). Phone Number ID `1125801510623915`
  - `+503 6042 9873` — WABA "Multitiendas Oriental / atención pedidos" (portafolio Chinolandia SV, tipo "Aplicación de WhatsApp Business")
- El botón "Añadir número" está bloqueado en varias cuentas por la verificación incompleta y el tipo de cuenta.

**Requisito bloqueante**: completar y que Meta **apruebe la verificación del negocio**
(Business Settings → Información del negocio → Iniciar/continuar verificación).

**Pasos para retomar (cuando la verificación esté APROBADA):**
1. Elegir UN número +503 y liberarlo de donde esté (borrarlo de esa WABA).
2. Agregarlo a una cuenta **Cloud API** bajo el portafolio Chinolandia SV:
   Administrador de WhatsApp → esa cuenta → Números de teléfono → Añadir número →
   verificar con código (SMS/llamada) → poner PIN de 2 pasos → registrar.
3. Anotar el **Phone Number ID nuevo** y el **WABA ID** de esa cuenta.
4. En Railway → variable `META_PHONE_NUMBER_ID` = el ID nuevo → redeploy.
5. Si la WABA es distinta a `1455294849671713`, suscribir la app Sofi-agente a la
   WABA nueva (llamada a la API `POST /{WABA_ID}/subscribed_apps` con el token, o
   desde el panel). El webhook (callback URL + verify token) no cambia.
6. Probar: mandar un WhatsApp al número +503 → Sofi responde.

---

## ⏳ Pendiente 2 — Registro de pedidos en Google Sheets

**Objetivo**: que cada pedido que Sofi confirma quede como fila en una hoja de cálculo.

**Lo que prepara el usuario:**
1. Crear hoja de Google "Pedidos Sofi — Chinolandia SV".
2. Fila 1: `Fecha | Tienda | Cliente | Teléfono | Dirección | Referencia | Productos | Total | Forma de pago | Estado`
3. Extensiones → Apps Script → pegar el script `doPost` (ver mensaje del chat).
4. Implementar → Aplicación web → acceso "Cualquier usuario" → copiar la URL `/exec`.

**Lo que falta programar (próxima sesión):**
- Conectar el registro de pedidos a Sofi vía tool use de Claude (que al confirmar,
  llame a una función que arme el pedido estructurado).
- `agent/tools.py` ya tiene `crear_pedido` / `confirmar_pedido` como base.
- Nuevo módulo que haga `POST` de la URL de la hoja al confirmar.
- Variable en Railway con la URL de la hoja.
- Probar un pedido de punta a punta.

---

## Cómo mantener el agente

- **Producto nuevo / cambio de precio** → editar `knowledge/chinolandia-sv/catalogo.md` → `git add`, `git commit`, `git push`
- **Tienda nueva** → crear `config/tiendas/<id>.yaml` + carpeta `knowledge/<id>/` con `catalogo.md` + agregar el `<id>` a la lista `tiendas:` de `config/business.yaml` → push
- **Cambiar tono / reglas de Sofi** → `config/prompts.yaml` → push
- **Ver logs** → Railway → sofi-oriental-groupsv → Deployments → deployment activo → Logs
- **Probar sin WhatsApp** (consume API): `python pruebas/prueba_sofi.py` o `python tests/test_local.py`

## Costos recurrentes

- Railway: ~US$5/mes (Hobby)
- API de Anthropic: ~US$0.02–0.07 por conversación de cliente
