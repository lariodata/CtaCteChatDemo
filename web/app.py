"""
Chat Cuenta Corriente - Streamlit Demo

Uso:
    streamlit run web/app.py

La app se abre automáticamente en http://localhost:8501
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Configuración
API_URL = "http://localhost:8080"
USUARIOS = ["vendedor1", "vendedor2", "gerente1"]
PROVIDERS = {
    "Ollama (local, Qwen2.5)": "ollama",
    "Claude Haiku (cloud)": "claude_haiku",
}

# ============================================================================
# CONFIG PAGE
# ============================================================================

st.set_page_config(
    page_title="Chat Cuenta Corriente",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💬 Chat Cuenta Corriente")
st.markdown("Demo on-premise | Consulta deudas de clientes con IA")

# ============================================================================
# SIDEBAR: Selector Usuario
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuración")

    usuario = st.radio(
        "Seleccionar usuario:",
        USUARIOS,
        format_func=lambda x: f"{x.replace('_', ' ').title()}",
        key="usuario_selector"
    )

    st.divider()

    provider_label = st.selectbox(
        "Modelo LLM:",
        list(PROVIDERS.keys()),
        key="provider_selector"
    )
    provider = PROVIDERS[provider_label]

    st.divider()

    # Health check
    try:
        resp = requests.get(f"{API_URL}/health", timeout=2)
        if resp.status_code == 200:
            st.success("✅ API operativa", icon="✅")
        else:
            st.error("❌ API con error")
    except Exception as e:
        st.error(f"❌ API no disponible: {str(e)[:50]}")

    st.divider()

    # Mostrar tools disponibles
    st.subheader("📋 Tools disponibles")
    try:
        resp = requests.get(f"{API_URL}/tools/{usuario}", timeout=2)
        if resp.status_code == 200:
            tools = resp.json()["tools"]
            for tool in tools:
                with st.expander(f"🔧 {tool['name']}"):
                    st.write(tool['description'])
        else:
            st.warning("No se pudieron cargar los tools")
    except Exception as e:
        st.warning(f"Error al cargar tools: {str(e)[:40]}")

    st.divider()

    # Info
    st.markdown("""
    **Usuarios disponibles:**
    - **vendedor1** → Zona 1
    - **vendedor2** → Zonas 2, 3
    - **gerente1** → Todas las zonas

    **Ejemplos de preguntas:**
    - "¿Cuánto debe el cliente 3523?"
    - "Dame los clientes con deuda de mi zona"
    - (Gerente) "¿Deuda total zona 1?"
    """)

# ============================================================================
# MAIN: Chat
# ============================================================================

# Inicializar session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_user" not in st.session_state:
    st.session_state.current_user = usuario

# Si cambió usuario, limpiar historial
if st.session_state.current_user != usuario:
    st.session_state.messages = []
    st.session_state.current_user = usuario

# ============================================================================
# MOSTRAR HISTORIAL
# ============================================================================

st.subheader(f"Conversación con {usuario}")

# Mostrar todos los mensajes
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")

    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(content)
            if timestamp:
                st.caption(timestamp)
    else:  # assistant
        with st.chat_message("assistant", avatar="🤖"):
            st.write(content)
            if timestamp:
                st.caption(timestamp)

# ============================================================================
# INPUT Y ENVÍO
# ============================================================================

def enviar_mensaje(mensaje: str):
    """Envía mensaje a la API y maneja respuesta."""
    if not mensaje.strip():
        return

    # Agregar mensaje usuario al historial
    st.session_state.messages.append({
        "role": "user",
        "content": mensaje,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # Mostrar en UI
    with st.chat_message("user", avatar="👤"):
        st.write(mensaje)
        st.caption(datetime.now().strftime("%H:%M:%S"))

    # Llamar API
    with st.spinner("Procesando... 🔄"):
        try:
            payload = {
                "usuario": usuario,
                "mensaje": mensaje,
                "provider": provider,
                "max_iterations": 3
            }

            resp = requests.post(
                f"{API_URL}/chat",
                json=payload,
                timeout=120  # 2 minutos para el LLM
            )

            if resp.status_code == 200:
                data = resp.json()
                respuesta = data["respuesta"]

                # Agregar respuesta al historial
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": respuesta,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })

                # Mostrar respuesta
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(respuesta)
                    st.caption(datetime.now().strftime("%H:%M:%S"))

            else:
                # Error de la API
                error_detail = resp.json().get("detail", "Error desconocido")
                st.error(f"❌ Error ({resp.status_code}): {error_detail}")

        except requests.exceptions.Timeout:
            if provider == "ollama":
                st.error("⏱️ Timeout: El LLM tardó más de 2 minutos. Verifica:\n- ¿Ollama está corriendo? (`ollama serve`)\n- ¿Tienes CPU/RAM disponible?\n- Intenta de nuevo.")
            else:
                st.error("⏱️ Timeout: Claude tardó más de 2 minutos. Verifica tu conexión a internet e intenta de nuevo.")
        except requests.exceptions.ConnectionError:
            st.error(f"❌ No se puede conectar a la API. ¿Está corriendo en {API_URL}?")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Input box con form (patrón recomendado Streamlit)
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([0.85, 0.15])

    with col1:
        user_input = st.text_input(
            "Escribe tu pregunta:",
            placeholder="Ej: ¿Cuánto debe el cliente 3523?",
            label_visibility="collapsed"
        )

    with col2:
        submitted = st.form_submit_button("Enviar 📤", use_container_width=True)

    # Procesar envío si form fue submitted
    if submitted and user_input.strip():
        enviar_mensaje(user_input)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**Chat Cuenta Corriente** | Demo Etapa 7 (Streamlit)
Backend: FastAPI + Ollama/Qwen2.5 o Claude Haiku (seleccionable)
""")
