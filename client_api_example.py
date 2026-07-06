"""
Cliente Python para consumir la API (Etapa 5).

Ejemplo de uso:

    # 1. Health check
    python client_api_example.py health

    # 2. Listar tools de un usuario
    python client_api_example.py tools vendedor1

    # 3. Enviar un chat
    python client_api_example.py chat vendedor1 "¿Cuánto debe el cliente 3523?"

    # 4. Gerente consulta reportes
    python client_api_example.py chat gerente1 "¿Cuál es la deuda total de la zona 1?"
"""

import sys
import requests
import json

BASE_URL = "http://localhost:8001"


def health_check():
    """GET /health"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def get_tools(usuario: str):
    """GET /tools/{usuario}"""
    response = requests.get(f"{BASE_URL}/tools/{usuario}")
    if response.status_code == 200:
        data = response.json()
        print(f"Usuario: {data['usuario']}")
        print(f"Tools disponibles ({len(data['tools'])}):")
        for tool in data['tools']:
            print(f"  - {tool['name']}")
            print(f"    {tool['description'][:80]}...")
    else:
        print(f"Error {response.status_code}: {response.json()['detail']}")


def chat(usuario: str, mensaje: str, max_iterations: int = 3):
    """POST /chat"""
    payload = {
        "usuario": usuario,
        "mensaje": mensaje,
        "max_iterations": max_iterations
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=180)
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar a {BASE_URL}")
        print("¿El servidor está corriendo? Intenta: python main_api.py")
        return

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n🤖 [{data['usuario']}]")
            print(f"Respuesta:\n{data['respuesta']}\n")
            print(f"(Iteraciones usadas: {data['iterations_used']})")
        except ValueError:
            print(f"Error: Respuesta inválida del servidor: {response.text}")
    else:
        try:
            print(f"Error {response.status_code}: {response.json()['detail']}")
        except ValueError:
            print(f"Error {response.status_code}: {response.text}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "health":
        health_check()

    elif command == "tools":
        if len(sys.argv) < 3:
            print("Uso: python client_api_example.py tools <usuario>")
            print("Ej: python client_api_example.py tools vendedor1")
            return
        get_tools(sys.argv[2])

    elif command == "chat":
        if len(sys.argv) < 4:
            print("Uso: python client_api_example.py chat <usuario> <mensaje>")
            print("Ej: python client_api_example.py chat vendedor1 '¿Cuánto debe el cliente 3523?'")
            return
        usuario = sys.argv[2]
        mensaje = sys.argv[3]
        max_iter = int(sys.argv[4]) if len(sys.argv) > 4 else 3
        chat(usuario, mensaje, max_iter)

    else:
        print(f"Comando desconocido: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
