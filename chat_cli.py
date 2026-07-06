"""
Chat interactivo por consola (demo manual, no automatizado).

Uso:
    python chat_cli.py

Elegís un usuario (vendedor1, vendedor2, gerente1), escribís preguntas,
y ves la respuesta del LLM en vivo. Requiere Ollama corriendo.
"""

from src import orchestrator

USUARIOS_DISPONIBLES = ["vendedor1", "vendedor2", "gerente1"]


def elegir_usuario() -> str:
    print("Usuarios disponibles:", ", ".join(USUARIOS_DISPONIBLES))
    while True:
        usuario = input("¿Con qué usuario querés chatear? ").strip()
        if usuario in USUARIOS_DISPONIBLES:
            return usuario
        print(f"'{usuario}' no es válido. Elegí uno de: {USUARIOS_DISPONIBLES}")


def main():
    usuario = elegir_usuario()
    print(f"\nChateando como '{usuario}'. Escribí 'salir' para terminar.\n")

    while True:
        mensaje = input(f"[{usuario}] > ").strip()
        if mensaje.lower() in ("salir", "exit", "quit"):
            break
        if not mensaje:
            continue

        try:
            respuesta = orchestrator.chat(usuario=usuario, mensaje=mensaje)
            print(f"\n🤖 {respuesta}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
