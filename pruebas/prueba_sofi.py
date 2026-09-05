# Prueba automatica de Sofi — simula una conversacion de cliente.
# Correr desde la raiz del proyecto:
#   python pruebas/prueba_sofi.py
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.brain import generar_respuesta
from agent.memory import (
    guardar_mensaje,
    inicializar_db,
    limpiar_historial,
    obtener_historial,
)
from agent import tiendas

TEL = "prueba-auto-oriental"

GUION = [
    "Hola, vi el anuncio del lápiz de acupuntura. Es para mi mamá que sufre de dolor de rodillas",
    "Con qué funciona? hay que comprar pilas?",
    "Está bien. Quiero llevar 3, para ella y mis dos hermanas",
    "Carlos Menjivar. 7788-1234. Colonia Escalón, calle 5 casa 12, San Salvador. Referencia frente a la tienda La Bendición. Pago contra entrega",
    "Sí, todo correcto",
]


async def main():
    await inicializar_db()
    await limpiar_historial(TEL)
    tienda_id = tiendas.tienda_por_defecto()
    print("=" * 70)
    print(f"Tienda: {tienda_id or '(sin identificar)'}")
    for i, msg in enumerate(GUION, 1):
        historial = await obtener_historial(TEL)
        respuesta, es_real = await generar_respuesta(msg, historial, tienda_id, "Carlos Menjivar")
        print(f"\n[{i}] CLIENTE: {msg}")
        print(f"    SOFI: {respuesta}")
        if es_real:
            await guardar_mensaje(TEL, "user", msg)
            await guardar_mensaje(TEL, "assistant", respuesta)
    print("\n" + "=" * 70)
    await limpiar_historial(TEL)


if __name__ == "__main__":
    asyncio.run(main())
