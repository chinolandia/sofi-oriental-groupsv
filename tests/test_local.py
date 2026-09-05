# tests/test_local.py — Simulador de chat en terminal
# Generado por AgentKit

"""
Prueba tu agente sin necesitar WhatsApp.
Simula una conversacion en la terminal.

Como en WhatsApp llega un solo numero compartido para todo el paraguas, aca se
usa la tienda por defecto (config/business.yaml -> agente.tienda_por_defecto).
Podes cambiarla en vivo con:  tienda <id>
"""

import asyncio
import os
import sys

# Agregar el directorio raiz al path para poder importar "agent"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.brain import generar_respuesta  # noqa: E402
from agent.memory import (  # noqa: E402
    guardar_mensaje,
    inicializar_db,
    limpiar_historial,
    obtener_historial,
)
from agent import tiendas  # noqa: E402

TELEFONO_TEST = "test-local-001"


async def main():
    """Loop principal del chat de prueba."""
    await inicializar_db()

    tienda_id = tiendas.tienda_por_defecto()

    print()
    print("=" * 55)
    print("   AgentKit — Test Local")
    print("=" * 55)
    print()
    print(f"  Tienda activa: {tienda_id or '(sin identificar)'}")
    print("  Escribe mensajes como si fueras un cliente.")
    print("  Comandos especiales:")
    print("    'tienda <id>' — cambia de tienda")
    print("    'limpiar'     — borra el historial")
    print("    'salir'       — termina el test")
    print()
    print("-" * 55)
    print()

    while True:
        try:
            mensaje = input("Tu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nTest finalizado.")
            break

        if not mensaje:
            continue

        if mensaje.lower() == "salir":
            print("\nTest finalizado.")
            break

        if mensaje.lower() == "limpiar":
            await limpiar_historial(TELEFONO_TEST)
            print("[Historial borrado]\n")
            continue

        if mensaje.lower().startswith("tienda "):
            nuevo = mensaje.split(" ", 1)[1].strip()
            if tiendas.existe(nuevo):
                tienda_id = nuevo
                print(f"[Tienda activa: {tienda_id}]\n")
            else:
                print(f"[No existe la tienda '{nuevo}']\n")
            continue

        # El historial se lee ANTES de guardar (brain.py agrega el mensaje actual)
        historial = await obtener_historial(TELEFONO_TEST)

        print("\nAgente: ", end="", flush=True)
        respuesta, es_respuesta_real = await generar_respuesta(mensaje, historial, tienda_id)
        print(respuesta)
        print()

        # Igual que en produccion: los avisos tecnicos no entran al historial
        if es_respuesta_real:
            await guardar_mensaje(TELEFONO_TEST, "user", mensaje)
            await guardar_mensaje(TELEFONO_TEST, "assistant", respuesta)


if __name__ == "__main__":
    asyncio.run(main())
