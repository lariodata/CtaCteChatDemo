# Chat Cuenta Corriente — Frontend Streamlit (Etapa 7)

Demo simple con Streamlit que consume la API FastAPI.

## Inicio rápido

### 1. Instalar dependencias

```bash
cd web
pip install -r requirements.txt
```

### 2. Arrancar Backend (FastAPI)

En **otra terminal**:

```bash
python main_api.py
# Debe estar en http://localhost:8001
```

### 3. Arrancar Frontend (Streamlit)

```bash
streamlit run app.py
```

Se abre automáticamente en **http://localhost:8501**

---

## Estructura

```
web/
├── app.py                  # App Streamlit principal (~180 líneas)
├── requirements.txt        # Dependencias (streamlit, requests, dotenv)
└── README.md              # Este archivo
```

---

## Uso

### 1. Selecciona un usuario

En el **sidebar izquierdo**:
- **vendedor1** → Zona 1 (3 tools: deuda, movimientos, clientes)
- **vendedor2** → Zonas 2, 3 (mismos 3 tools)
- **gerente1** → Todas las zonas (4 tools: + consulta_custom)

### 2. Expande "Tools disponibles"

Ves qué puede hacer cada usuario (ayuda a entender qué preguntar).

### 3. Escribe tu pregunta

Ejemplos:
```
Vendedor:
  "¿Cuánto debe el cliente 3523?"
  "Dame los clientes con deuda de mi zona"
  "Movimientos del cliente 100"

Gerente:
  "¿Deuda total zona 1?"
  "Top 3 morosos zona 1"
  "Resumen ejecutivo zona 2"
```

### 4. Lee la respuesta

El LLM procesa con Ollama/Qwen2.5 y devuelve respuesta.

---

## Features

✅ **Selector de usuario** — Cambia usuario sin recargar  
✅ **Historial de chat** — Todos los mensajes guardados en sesión  
✅ **Tools info** — Expandibles, muestran descripción  
✅ **Health check** — Verifica que API está disponible  
✅ **Timestamps** — Cada mensaje muestra hora  
✅ **Error handling** — Muestra errores de API de forma legible  
✅ **Loading state** — Spinner mientras LLM procesa  
✅ **Responsive** — Funciona en mobile también  

---

## Troubleshooting

### ❌ "No se puede conectar a la API"

Verifica que FastAPI está corriendo:
```bash
python main_api.py
# Debe estar en http://localhost:8001
```

### ❌ "¿Cuánto debe el cliente X?" → Error 500

Probablemente falta la BD o no está disponible. Verifica `.env`:
```
DB_HOST=lariosql70
DB_USER=chat_app
DB_PASSWORD=...
```

### ❌ App muy lenta

- Si es el primer mensaje, es normal (LLM carga)
- Si todos son lentos, verifica CPU/RAM disponible
- O reduce `max_iterations` en app.py (línea 108)

---

## Próximos pasos

### Si prospera el proyecto → Migración a React

Cuando quieras versión profesional:
1. Mantén la API FastAPI igual
2. Crea frontend React (ver plan en agent output)
3. Misma funcionalidad, pero UI/UX mejor

### Etapa 8+

- Persistencia: guardar conversaciones en BD
- Logging: registrar cada llamada a /chat
- Auth JWT: reemplazar validación simple

---

## Deploy

### Desarrollo (ahora)
```bash
streamlit run app.py  # http://localhost:8501
```

### Producción (futuro)
```bash
# Servir Streamlit en servidor remoto
streamlit run app.py --server.port 80 --server.address 0.0.0.0
```

O empaquetarlo en Docker:
```dockerfile
FROM python:3.13
WORKDIR /app
COPY web/ .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

---

## Nota técnica

**¿Por qué Streamlit para demo?**
- Rápido de desarrollar (1 archivo, ~180 líneas)
- Todo Python (no necesitas JavaScript)
- Perfecto para demos/prototipos
- Bueno para mostrar al cliente

**¿Cuándo migrar a React?**
- Si el proyecto crece (más usuarios)
- Si necesitas UI/UX más personalizada
- Si quieres controlar cada pixel
- Si integras con más sistemas

**API sigue siendo FastAPI en ambos casos** → No hay cambios en backend.
