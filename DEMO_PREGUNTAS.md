# 📋 Demo: Preguntas por Rol

Guía de preguntas de ejemplo para demostración del chat mañana.
Cada sección incluye preguntas que **funcionan** ✅ y preguntas que **se rechazan** ❌ (demostrando seguridad RBAC).

---

## 🧑‍💼 VENDEDOR1 (Zona 1)

### ✅ Preguntas que FUNCIONAN (Zona 1)

1. **Consulta de deuda específica**
   - "¿Cuánto debe el cliente 3523?"
   - **Tool:** `consultar_deuda` → zona 1 ✓

2. **Listado de clientes con deuda**
   - "Dame los clientes de mi zona que tienen deuda"
   - **Tool:** `clientes_por_zona` → zona 1 ✓

3. **Detalle de movimientos de un cliente**
   - "Movimientos del cliente 3523"
   - **Tool:** `detalle_movimientos` → zona 1 ✓

4. **Preguntas combinadas (múltiples tools)**
   - "¿Cuántos clientes con deuda tengo en mi zona y cuál es el mayor moroso?"
   - "Dame los clientes de zona 1 y detalles del cliente 3523"

### ❌ Preguntas que SE RECHAZAN (Intento de acceso a otra zona)

5. **Zona 2**
   - "¿Cuánto debe el cliente 32322 en zona 2?"
   - "Clientes con deuda de mi zona"
   - "Deuda total zona 2"
   - **Respuesta esperada:** "No puedo. Solo tengo acceso a zona 1"

6. **Zona 3**
   - "¿Deuda zona 3?"
   - "Clientes morosos de zona 3"
   - **Respuesta esperada:** "No puedo. Solo tengo acceso a zona 1"

---

## 🧑‍💼 VENDEDOR2 (Zonas 2 y 3)

### ✅ Preguntas que FUNCIONAN (Zonas 2 o 3)

1. **Consulta en Zona 2**
   - "¿Cuánto debe el cliente 32322?"
   - **Tool:** `consultar_deuda` → zona 2 ✓

3. **Clientes de mis zonas**
   - "Clientes con deuda de mi zona"
   - "¿Qué clientes tengo en mis zonas?"
   - **Tool:** `clientes_por_zona` → ambas zonas 2 y 3 ✓

4. **Detalle de movimientos (multi-zona)**
   - "Movimientos del cliente 32322"
   - **Tool:** `detalle_movimientos` → zona 2 o 3 ✓

5. **Preguntas complejas**
   - "¿Cuáles son mis morosos en zona 2 y zona 3?"
   - "Dime los clientes con más deuda en mis zonas"

## 👔 GERENTE1 (Todas las zonas)

### ✅ Preguntas que FUNCIONAN (Todas las zonas)

1. **Consolidados por zona**
   - "¿Deuda total zona 1?"
   - "Deuda total zona 2"
   - "Consolidado zona 3"
   - **Tool:** `consulta_custom` → deuda_por_zona ✓

2. **Top morosos por zona**
   - "¿Top 5 morosos de zona 1?"
   - "Mayores deudores zona 2"
   - "Top 10 clientes con deuda zona 3"
   - **Tool:** `consulta_custom` → top_morosos ✓

3. **Resumen ejecutivo por zona**
   - "Resumen zona 1: cuántos clientes, deuda total, mora promedio"
   - "Análisis zona 2: situación general"
   - "¿Cuál es la zona con más deuda?"
   - **Tool:** `consulta_custom` → resumen_zonas ✓

4. **Comparativa de zonas**
   - "¿Cuál zona tiene más mora promedio: zona 1 o zona 2?"
   - "Compara deuda total zona 1, 2 y 3"
   - "¿Qué zona genera más riesgo de cobranza?"

5. **Deudores específicos (sin restricción de zona)**
   - "¿Cuánto debe el cliente 1001?" (zona 1)
   - "¿Cuánto debe el cliente 2500?" (zona 2)
   - "¿Cuánto debe el cliente 3600?" (zona 3)
   - **Tool:** `consultar_deuda` → cualquier zona ✓

6. **Detalle de clientes (sin restricción)**
   - "Movimientos del cliente 1001"
   - "Historial cliente 2500"
   - "Transacciones cliente 3600"
   - **Tool:** `detalle_movimientos` → cualquier zona ✓

---

## 🎯 Preguntas Recomendadas para Demo en Vivo

### Scenario 1: Vendedor verificando su zona
```
Usuario: vendedor1
Pregunta: "¿Cuánto debe el cliente 3523?"
→ Respuesta: Muestra deuda (zona 1 OK)

Usuario: vendedor1
Pregunta: "¿Clientes zona 2?"
→ Respuesta: "No puedo. Solo tengo acceso a zona 1"
→ Demuestra: SEGURIDAD RBAC FUNCIONANDO
```

### Scenario 2: Vendedor2 con múltiples zonas
```
Usuario: vendedor2
Pregunta: "Clientes con deuda de mi zona"
→ Respuesta: Lista de clientes de zonas 2 y 3
→ Demuestra: Soporte de múltiples zonas
```

### Scenario 3: Gerente viendo consolidados
```
Usuario: gerente1
Pregunta: "¿Deuda total zona 1?"
→ Respuesta: Consolidado de zona 1
→ Demuestra: Acceso completo a reportes

Usuario: gerente1
Pregunta: "¿Cuál es la zona más riesgosa?"
→ Respuesta: Análisis comparativo
→ Demuestra: Múltiples queries + análisis LLM
```

---

## 📊 Tabla de Funcionalidades por Rol

| Función | Vendedor1 | Vendedor2 | Gerente1 |
|---------|-----------|-----------|----------|
| Consultar deuda cliente | ✅ Zona 1 | ✅ Zonas 2,3 | ✅ Todas |
| Listar clientes con deuda | ✅ Zona 1 | ✅ Zonas 2,3 | ✅ Todas |
| Detalle movimientos | ✅ Zona 1 | ✅ Zonas 2,3 | ✅ Todas |
| Deuda total zona | ❌ | ❌ | ✅ |
| Top morosos zona | ❌ | ❌ | ✅ |
| Resumen ejecutivo zona | ❌ | ❌ | ✅ |
| Acceso multi-zona | ❌ | ✅ | ✅ |

---

## 🔒 Demostrando Seguridad

**Preguntas que deberían ser RECHAZADAS:**

1. Vendedor intenta acceder a zona no asignada
   - "¿Deuda cliente X zona Y?" (donde Y no es su zona)
   - **Respuesta:** "No puedo. Solo tengo acceso a zona(s) X"

2. Vendedor intenta acceder a reportes de gerente
   - "¿Deuda total zona 1?"
   - **Respuesta:** Error o "No tengo información para eso"

3. Intento de SQL injection o bypass
   - El system prompt + RBAC enfuerzan restricciones
   - **Respuesta:** Rechazo seguro

---

## 💡 Tips para la Presentación

### Flow Recomendado

1. **Intro (1 min)**
   - Explicar qué es el chat (consultas de cuentas corrientes)
   - Mencionar roles y zonas

2. **Demo Vendedor1 (2 min)**
   - Pregunta exitosa: "¿Cuánto debe cliente 3523?"
   - Pregunta rechazada: "¿Zona 2?" → SEGURIDAD VISIBLE

3. **Demo Vendedor2 (1 min)**
   - Muestra multi-zona: "Clientes de mis zonas"
   - Contraste con vendedor1

4. **Demo Gerente1 (2 min)**
   - Pregunta: "¿Deuda total zona 1?"
   - Pregunta: "¿Cuál zona tiene más mora?"
   - Muestra análisis LLM + consolidados

5. **Cierre (30 seg)**
   - Resaltar seguridad RBAC
   - Mencionar integraciones (FastAPI, Ollama, SQL Server)

### Timing Total: ~6-7 minutos

---

## 🚀 Cómo Ejecutar la Demo

### Terminal 1 - Backend
```powershell
cd c:\Users\RodrigoMarozzi\Documents\Projects\ctacte-chat-demo
python main_api.py
# Esperar: "Uvicorn running on http://localhost:8001"
```

### Terminal 2 - Frontend
```powershell
cd c:\Users\RodrigoMarozzi\Documents\Projects\ctacte-chat-demo
streamlit run web/app.py
# Se abre: http://localhost:8501
```

### En el Navegador
1. Abre http://localhost:8501
2. Selecciona usuario en sidebar
3. Escribe preguntas de arriba

---

## 📝 Notas Importantes

- **Tiempos:** Ollama (primera vez) tarda ~5-10s, luego ~2-3s
- **Orden:** Empieza con Vendedor1, luego 2, luego Gerente
- **Errores:** Si falla, verifica Ollama: `ollama serve` en otra terminal
- **SQL:** Si no hay datos, el chat dirá "No tengo información"
- **Cache:** Respuestas iguales son más rápidas (cache 5 min)

Buena suerte con la demo! 🎉
