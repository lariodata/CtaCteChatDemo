"""
Chat Cuenta Corriente - Streamlit Demo (Diseño distintivo)

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

# Paleta de colores distintiva
COLORS = {
    "navy": "#0F3B66",           # Confianza, autoridad
    "orange": "#FF8C42",         # Urgencia, acción
    "sky_light": "#E8F4F8",      # Fondo chat, aire
    "slate": "#2C3E50",          # Texto principal
    "canvas": "#F5F7FA",         # Fondo limpio
    "teal": "#1ABC9C",           # Éxito, confirmación
}

# ============================================================================
# CONFIG PAGE + CUSTOM CSS
# ============================================================================

st.set_page_config(
    page_title="Chat Cuenta Corriente",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS distintivo
st.markdown(f"""
<style>
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Main background */
    .main {{
        background-color: {COLORS['canvas']};
    }}

    /* Header distintivo */
    .header-container {{
        background: linear-gradient(135deg, {COLORS['navy']} 0%, {COLORS['navy']}dd 100%);
        padding: 2rem;
        border-radius: 0;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(15, 59, 102, 0.15);
    }}

    .header-container h1 {{
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }}

    .header-container p {{
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }}

    /* Chat messages */
    .stChatMessage {{
        background-color: transparent;
    }}

    .stChatMessage[data-testid="ChatMessage"] {{
        padding: 1rem 0;
    }}

    /* User message */
    .stChatMessage[data-testid="ChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
        justify-content: flex-end;
    }}

    /* Assistant message */
    .stChatMessage[data-testid="ChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
        justify-content: flex-start;
    }}

    /* Tarjeta de comprobante (signature element) */
    .comprobante {{
        background-color: white;
        border-left: 4px solid {COLORS['orange']};
        border-radius: 4px;
        padding: 1.2rem;
        margin: 1rem 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(15, 59, 102, 0.08);
        border: 1px solid {COLORS['canvas']};
    }}

    .comprobante-header {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid {COLORS['canvas']};
        font-weight: 600;
        color: {COLORS['slate']};
    }}

    .comprobante-field {{
        display: flex;
        justify-content: space-between;
        margin: 0.6rem 0;
        color: {COLORS['slate']};
    }}

    .comprobante-label {{
        font-weight: 500;
        min-width: 120px;
    }}

    .comprobante-value {{
        text-align: right;
        font-weight: 600;
        color: {COLORS['navy']};
    }}

    .comprobante-value.alert {{
        color: {COLORS['orange']};
    }}

    /* Buttons */
    .stButton > button {{
        background-color: {COLORS['navy']};
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s;
    }}

    .stButton > button:hover {{
        background-color: {COLORS['orange']};
        box-shadow: 0 4px 12px rgba(255, 140, 66, 0.3);
    }}

    /* Input fields */
    .stTextInput > div > div > input {{
        background-color: white;
        border: 1px solid {COLORS['canvas']};
        border-radius: 4px;
        padding: 0.8rem;
        font-size: 0.95rem;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: {COLORS['navy']};
        box-shadow: 0 0 0 3px rgba(15, 59, 102, 0.1);
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid {COLORS['canvas']};
    }}

    /* Success/Error badges */
    .badge-success {{
        color: {COLORS['teal']};
        font-weight: 600;
    }}

    .badge-error {{
        color: {COLORS['orange']};
        font-weight: 600;
    }}

    /* Timestamps */
    .timestamp {{
        color: {COLORS['slate']};
        opacity: 0.6;
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }}
</style>
""", unsafe_allow_html=True)

# Header distintivo
st.markdown(f"""
<div class="header-container">
    <h1>💰 Chat Cuenta Corriente</h1>
    <p>Consulta deudas de clientes con IA | On-premise • Seguro</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR: Configuración (Collapsible)
# ============================================================================

with st.sidebar:
    st.markdown(f"<h3 style='color: {COLORS['navy']}; margin-top: 0;'>⚙️ Configuración</h3>", unsafe_allow_html=True)

    # Usuario
    usuario = st.radio(
        "Seleccionar usuario:",
        USUARIOS,
        format_func=lambda x: {
            "vendedor1": "👤 Vendedor 1 (Zona 1)",
            "vendedor2": "👤 Vendedor 2 (Zonas 2, 3)",
            "gerente1": "👔 Gerente (Todas zonas)"
        }.get(x, x),
        key="usuario_selector"
    )

    st.divider()

    # LLM Provider
    provider_label = st.selectbox(
        "Modelo LLM:",
        list(PROVIDERS.keys()),
        key="provider_selector"
    )
    provider = PROVIDERS[provider_label]

    st.divider()

    # Health check
    st.markdown("**Estado del sistema**")
    try:
        resp = requests.get(f"{API_URL}/health", timeout=2)
        if resp.status_code == 200:
            st.markdown(f"<p class='badge-success'>✅ API operativa</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p class='badge-error'>❌ API con error</p>", unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"<p class='badge-error'>❌ No disponible</p>", unsafe_allow_html=True)

    st.divider()

    # Tools disponibles
    st.markdown(f"<h4 style='color: {COLORS['navy']};'>📋 Tools disponibles</h4>", unsafe_allow_html=True)
    try:
        resp = requests.get(f"{API_URL}/tools/{usuario}", timeout=2)
        if resp.status_code == 200:
            tools = resp.json()["tools"]
            for tool in tools:
                with st.expander(f"🔧 {tool['name']}", expanded=False):
                    st.caption(tool['description'])
        else:
            st.info("No se pudieron cargar los tools")
    except Exception as e:
        st.info(f"Error al cargar tools")

    st.divider()

    # Info y ejemplos
    st.markdown(f"""
    <div style='background-color: {COLORS['sky_light']}; padding: 1rem; border-radius: 4px; border-left: 3px solid {COLORS['navy']};'>
    <p><strong>Ejemplos de preguntas:</strong></p>
    <ul style='margin: 0.5rem 0; font-size: 0.9rem;'>
    <li>"¿Cuánto debe cliente 3523?"</li>
    <li>"Top 3 morosos de mi zona"</li>
    <li>"Deuda total zona 1" (gerentes)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def render_comprobante(cliente: str = None, deuda: str = None, mora_dias: str = None, zona: str = None):
    """Renderiza una tarjeta de comprobante distintiva (signature element)."""
    html = '<div class="comprobante">'
    html += '<div class="comprobante-header">'
    html += '<span>COMPROBANTE DE DEUDA</span>'
    html += f'<span style="font-size: 0.85rem;">{datetime.now().strftime("%d/%m/%y %H:%M")}</span>'
    html += '</div>'

    if cliente:
        html += '<div class="comprobante-field">'
        html += '<span class="comprobante-label">CLIENTE</span>'
        html += f'<span class="comprobante-value">{cliente}</span>'
        html += '</div>'

    if deuda:
        html += '<div class="comprobante-field">'
        html += '<span class="comprobante-label">DEUDA</span>'
        html += f'<span class="comprobante-value">${deuda}</span>'
        html += '</div>'

    if mora_dias:
        html += '<div class="comprobante-field">'
        html += '<span class="comprobante-label">MORA</span>'
        html += f'<span class="comprobante-value alert">{mora_dias} días</span>'
        html += '</div>'

    if zona:
        html += '<div class="comprobante-field">'
        html += '<span class="comprobante-label">ZONA</span>'
        html += f'<span class="comprobante-value">{zona}</span>'
        html += '</div>'

    html += '</div>'
    return html

def is_debt_response(text: str) -> bool:
    """Detecta si la respuesta contiene información de deuda."""
    indicators = ["$", "deuda", "debe", "saldo", "mora", "cliente", "zona"]
    return any(ind.lower() in text.lower() for ind in indicators)

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

st.markdown(f"<h3 style='color: {COLORS['slate']}; margin-top: 2rem;'>💬 Conversación</h3>", unsafe_allow_html=True)

# Mostrar todos los mensajes del historial
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")

    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
            if timestamp:
                st.markdown(f"<p class='timestamp'>{timestamp}</p>", unsafe_allow_html=True)
    else:  # assistant
        with st.chat_message("assistant", avatar="🤖"):
            # Mostrar respuesta de deuda como comprobante
            if is_debt_response(content):
                st.markdown(render_comprobante(cliente="Consulta procesada"), unsafe_allow_html=True)
            st.markdown(content)
            if timestamp:
                st.markdown(f"<p class='timestamp'>{timestamp}</p>", unsafe_allow_html=True)

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
        st.markdown(mensaje)
        st.markdown(f"<p class='timestamp'>{datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

    # Llamar API
    with st.spinner("⏳ Procesando tu consulta..."):
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

                # Mostrar respuesta con formato distintivo
                with st.chat_message("assistant", avatar="🤖"):
                    # Si es respuesta de deuda, mostrar como comprobante
                    if is_debt_response(respuesta):
                        st.markdown(render_comprobante(cliente="Consulta procesada"), unsafe_allow_html=True)
                        st.markdown(respuesta)
                    else:
                        st.markdown(respuesta)

                    st.markdown(f"<p class='timestamp'>{datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

            else:
                # Error de la API
                error_detail = resp.json().get("detail", "Error desconocido")
                st.error(f"❌ Error ({resp.status_code}): {error_detail}")

        except requests.exceptions.Timeout:
            if provider == "ollama":
                st.error("⏱️ Timeout: El modelo tardó mucho. Verifica:\n- ¿Ollama está corriendo? (`ollama serve`)\n- ¿Tienes CPU/RAM disponible?\n- Intenta de nuevo.")
            else:
                st.error("⏱️ Timeout: Claude tardó más de 2 minutos. Verifica tu conexión.")
        except requests.exceptions.ConnectionError:
            st.error(f"❌ No se puede conectar a la API en {API_URL}")
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")

# ============================================================================
# INPUT BOX (Distintivo)
# ============================================================================

st.markdown(f"""
<style>
    .input-container {{
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid {COLORS['canvas']};
        margin-top: 2rem;
        box-shadow: 0 2px 8px rgba(15, 59, 102, 0.06);
    }}
</style>
<div class="input-container">
""", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([0.88, 0.12])

    with col1:
        user_input = st.text_input(
            "Tu pregunta:",
            placeholder="Ej: ¿Cuánto debe el cliente 3523?",
            label_visibility="collapsed"
        )

    with col2:
        submitted = st.form_submit_button("Enviar", use_container_width=True)

    # Procesar envío si form fue submitted
    if submitted and user_input.strip():
        enviar_mensaje(user_input)

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# FOOTER MINIMALISTA
# ============================================================================

st.markdown(f"""
<div style='margin-top: 3rem; padding-top: 2rem; border-top: 1px solid {COLORS['canvas']}; text-align: center; color: {COLORS['slate']}; opacity: 0.6; font-size: 0.85rem;'>
    <p><strong>💰 Chat Cuenta Corriente</strong> • Demo Etapa 7 (Streamlit rediseñado)<br>
    Backend: FastAPI + Ollama/Qwen2.5 o Claude Haiku • <span style='color: {COLORS['teal']};'>⚡ On-premise & Seguro</span></p>
</div>
""", unsafe_allow_html=True)
