# Chat Cuenta Corriente SPA Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate frontend from Streamlit to vanilla HTML5/CSS3/JavaScript SPA with LARIO brand dark mode, responsive dashboard+chat layout, and modern chat bubbles.

**Architecture:** Single-page application (`web/index.html`) with inline CSS and JavaScript. No frameworks, no build tools. Communicates with existing FastAPI backend via Fetch API. Mobile-first responsive design with collapsible dashboard menu.

**Tech Stack:** HTML5, CSS3 (Grid/Flexbox), JavaScript ES6+, Fetch API. Backend (FastAPI) unchanged.

## Global Constraints

- **Single HTML file:** All CSS and JavaScript inline in `web/index.html`
- **No external dependencies:** Zero npm packages, CDNs, or frameworks
- **LARIO brand colors:** Primary red `#E31C23`, background black `#0a0a0a`, accent gold `#D4A574`, text white `#ffffff`
- **Responsive breakpoint:** Desktop ≥768px, Mobile <768px
- **API endpoints unchanged:** `/chat`, `/health`, `/tools/{usuario}`
- **Browser support:** Chrome, Firefox, Safari (ES6 compatible)
- **Frequent commits:** One commit per task minimum

---

## File Structure

**Files to create:**
- `web/index.html` — Single SPA entry point (all CSS + JS inline)

**Files to modify:**
- `main_api.py` — Potentially add static file serving (if not already done)

**Files unchanged:**
- All backend code, tests, API logic

---

## Phase 1: Scaffold & Dashboard Layout

### Task 1: Create index.html with HTML structure and dark mode CSS

**Files:**
- Create: `web/index.html`

**Produces:**
- HTML structure with semantic tags (`<header>`, `<nav>`, `<main>`, `<aside>`)
- CSS dark mode variables (colors)
- Grid layout: sidebar (20%) + main (80%)
- Basic styling for dashboard panel

**Steps:**

- [ ] **Step 1: Create basic index.html scaffold**

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Chat Cuenta Corriente</title>
    <style>
        /* CSS Variables - LARIO Brand Colors */
        :root {
            --color-bg-primary: #0a0a0a;
            --color-bg-secondary: #1a1a1a;
            --color-accent-primary: #E31C23;
            --color-accent-secondary: #D4A574;
            --color-text-primary: #ffffff;
            --color-text-secondary: #b0b0b0;
            --color-border: #2a2a2a;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--color-bg-primary);
            color: var(--color-text-primary);
            line-height: 1.5;
        }

        /* Layout Grid */
        #app {
            display: grid;
            grid-template-columns: 250px 1fr;
            grid-template-rows: auto 1fr;
            height: 100vh;
            gap: 0;
        }

        /* Header */
        header {
            grid-column: 1 / -1;
            background-color: var(--color-bg-secondary);
            padding: 1rem;
            border-bottom: 1px solid var(--color-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .header-title {
            font-size: 1.5rem;
            font-weight: bold;
        }

        /* Sidebar Dashboard */
        aside {
            background-color: var(--color-bg-secondary);
            padding: 1.5rem;
            border-right: 1px solid var(--color-border);
            overflow-y: auto;
        }

        /* Main Chat Area */
        main {
            display: flex;
            flex-direction: column;
            background-color: var(--color-bg-primary);
        }

        /* Responsive: Mobile */
        @media (max-width: 767px) {
            #app {
                grid-template-columns: 1fr;
            }

            aside {
                display: none;
            }

            aside.mobile-open {
                display: block;
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100vh;
                z-index: 1000;
            }
        }
    </style>
</head>
<body>
    <div id="app">
        <header>
            <h1 class="header-title">💰 Chat Cuenta Corriente</h1>
            <button id="hamburger-btn" style="display: none; background: none; border: none; color: #fff; font-size: 1.5rem; cursor: pointer;">☰</button>
        </header>
        
        <aside id="dashboard">
            <h2>⚙️ Configuración</h2>
        </aside>

        <main id="chat-area">
            <div id="messages-container"></div>
            <form id="chat-form"></form>
        </main>
    </div>

    <script>
        // Placeholder for JavaScript
        console.log('App initialized');
    </script>
</body>
</html>
```

- [ ] **Step 2: Verify HTML loads in browser**

Run: `cd web && python -m http.server 8000`
Navigate to: `http://localhost:8000/index.html`
Expected: Black page with "💰 Chat Cuenta Corriente" title visible

- [ ] **Step 3: Commit**

```bash
git add web/index.html
git commit -m "feat: create SPA scaffold with dark mode CSS variables and grid layout

- Single HTML file with inline CSS
- LARIO brand colors as CSS variables
- Header + sidebar + main layout grid
- Mobile-first responsive structure (hidden sidebar on mobile)

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 2: Style dashboard panel with user selector, LLM provider, and status

**Files:**
- Modify: `web/index.html` (add dashboard HTML + CSS)

**Consumes:**
- HTML structure from Task 1

**Produces:**
- Dashboard HTML with user radio buttons, LLM dropdown, health status, tools list
- CSS styling for all dashboard components

**Steps:**

- [ ] **Step 1: Add dashboard HTML elements**

Replace the dashboard `<aside>` section with:

```html
<aside id="dashboard">
    <h2 style="font-size: 1.3rem; margin-bottom: 1.5rem; color: var(--color-accent-primary);">⚙️ Configuración</h2>
    
    <!-- User Selector -->
    <div style="margin-bottom: 1.5rem;">
        <label style="display: block; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--color-text-secondary);">Usuario</label>
        <div id="user-selector" style="display: flex; flex-direction: column; gap: 0.5rem;">
            <!-- Radio buttons will be inserted here by JS -->
        </div>
    </div>

    <!-- LLM Provider Selector -->
    <div style="margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--color-border);">
        <label for="provider-select" style="display: block; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--color-text-secondary);">Modelo LLM</label>
        <select id="provider-select" style="width: 100%; padding: 0.6rem; background-color: var(--color-bg-primary); color: var(--color-text-primary); border: 1px solid var(--color-border); border-radius: 4px; cursor: pointer;">
            <option value="ollama">Ollama (local, Qwen2.5)</option>
            <option value="claude_haiku">Claude Haiku (cloud)</option>
        </select>
    </div>

    <!-- System Status -->
    <div style="margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--color-border);">
        <p style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--color-text-secondary);">Estado del sistema</p>
        <p id="health-status" style="font-size: 0.9rem; color: var(--color-text-secondary);">🔄 Verificando...</p>
    </div>

    <!-- Tools Available -->
    <div style="margin-bottom: 1.5rem;">
        <p style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--color-text-secondary);">📋 Tools disponibles</p>
        <div id="tools-list" style="font-size: 0.85rem; color: var(--color-text-secondary);">Cargando tools...</div>
    </div>

    <!-- Example Questions -->
    <div style="background-color: var(--color-bg-primary); padding: 1rem; border-radius: 4px; border-left: 3px solid var(--color-accent-primary);">
        <p style="font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--color-text-secondary);">💡 Ejemplos:</p>
        <div id="examples-list" style="display: flex; flex-direction: column; gap: 0.5rem;"></div>
    </div>
</aside>
```

- [ ] **Step 2: Add CSS for dashboard components**

Add to `<style>` section:

```css
/* Dashboard Styling */
aside h2 {
    font-size: 1.3rem;
    margin-bottom: 1.5rem;
}

aside label {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--color-text-secondary);
    margin-bottom: 0.5rem;
}

aside input[type="radio"],
aside select,
aside button {
    background-color: var(--color-bg-primary);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 0.6rem;
    cursor: pointer;
}

aside input[type="radio"]:checked {
    accent-color: var(--color-accent-primary);
}

aside button {
    width: 100%;
    background-color: var(--color-accent-primary);
    color: white;
    font-weight: 600;
    transition: opacity 0.2s;
}

aside button:hover {
    opacity: 0.9;
}

.example-btn {
    background-color: var(--color-bg-primary);
    color: var(--color-text-primary);
    border: 1px solid var(--color-accent-primary);
    padding: 0.5rem 0.8rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
}

.example-btn:hover {
    background-color: var(--color-accent-primary);
}
```

- [ ] **Step 3: Add basic JavaScript to populate user selector and examples**

Add to `<script>` section:

```javascript
const USERS = ["vendedor1", "vendedor2", "gerente1"];
const EXAMPLES = [
    "¿Cuánto debe cliente 3523?",
    "Top 3 morosos de mi zona",
    "Deuda total zona 1"
];
const PROVIDERS = {
    "Ollama (local, Qwen2.5)": "ollama",
    "Claude Haiku (cloud)": "claude_haiku"
};

// Populate user selector
const userSelector = document.getElementById('user-selector');
USERS.forEach(user => {
    const label = document.createElement('label');
    label.style.display = 'flex';
    label.style.alignItems = 'center';
    label.style.gap = '0.5rem';
    label.style.cursor = 'pointer';
    
    const input = document.createElement('input');
    input.type = 'radio';
    input.name = 'user';
    input.value = user;
    if (user === USERS[0]) input.checked = true;
    
    const text = document.createElement('span');
    text.textContent = user === "gerente1" ? "👔 Gerente" : `👤 ${user}`;
    
    label.appendChild(input);
    label.appendChild(text);
    userSelector.appendChild(label);
});

// Populate examples
const examplesList = document.getElementById('examples-list');
EXAMPLES.forEach(example => {
    const btn = document.createElement('button');
    btn.className = 'example-btn';
    btn.textContent = example;
    btn.type = 'button';
    examplesList.appendChild(btn);
});

// Store current user and provider
let currentUser = USERS[0];
let currentProvider = 'ollama';

document.getElementById('user-selector').addEventListener('change', (e) => {
    if (e.target.type === 'radio') {
        currentUser = e.target.value;
    }
});

document.getElementById('provider-select').addEventListener('change', (e) => {
    currentProvider = e.target.value;
});

console.log('Dashboard initialized');
```

- [ ] **Step 4: Test in browser**

Reload page at `http://localhost:8000/index.html`
Expected: 
- User radio buttons visible and selectable
- LLM provider dropdown visible
- Example buttons visible
- "Estado del sistema" showing "🔄 Verificando..."
- All styling matches dark mode (black background, LARIO red accents)

- [ ] **Step 5: Commit**

```bash
git add web/index.html
git commit -m "feat: implement dashboard panel with user selector and LLM provider

- User selector with radio buttons (vendedor1, vendedor2, gerente)
- LLM provider dropdown (Ollama, Claude Haiku)
- Health status placeholder
- Tools list placeholder
- Example questions (clickable buttons)
- LARIO brand styling (red accents, dark background)

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 3: Implement hamburger menu for mobile dashboard toggle

**Files:**
- Modify: `web/index.html` (add hamburger menu CSS + JS)

**Consumes:**
- Dashboard from Task 2
- Header from Task 1

**Produces:**
- Hamburger menu button visible on mobile (<768px)
- Mobile menu opens/closes dashboard overlay
- Closes when clicking outside or on a selection

**Steps:**

- [ ] **Step 1: Add hamburger button visibility for mobile**

Update the CSS `@media (max-width: 767px)` section:

```css
@media (max-width: 767px) {
    #app {
        grid-template-columns: 1fr;
    }

    #hamburger-btn {
        display: block !important;
    }

    aside {
        display: none;
        position: fixed;
        top: 3rem;
        left: 0;
        width: 80%;
        max-width: 300px;
        height: calc(100vh - 3rem);
        background-color: var(--color-bg-secondary);
        border-right: 1px solid var(--color-border);
        z-index: 999;
        overflow-y: auto;
    }

    aside.mobile-open {
        display: block;
    }
}
```

- [ ] **Step 2: Add hamburger toggle JavaScript**

Add to `<script>` section:

```javascript
const hamburgerBtn = document.getElementById('hamburger-btn');
const dashboard = document.getElementById('dashboard');

hamburgerBtn.addEventListener('click', () => {
    dashboard.classList.toggle('mobile-open');
});

// Close dashboard when clicking outside
document.addEventListener('click', (e) => {
    if (!dashboard.contains(e.target) && !hamburgerBtn.contains(e.target)) {
        dashboard.classList.remove('mobile-open');
    }
});

// Close when user selects an option
document.getElementById('user-selector').addEventListener('change', () => {
    dashboard.classList.remove('mobile-open');
});

document.getElementById('provider-select').addEventListener('change', () => {
    dashboard.classList.remove('mobile-open');
});
```

- [ ] **Step 3: Test mobile view**

In browser dev tools, toggle device toolbar to mobile (320px width)
Expected:
- Hamburger menu (☰) visible in header
- Dashboard hidden by default
- Clicking ☰ shows dashboard as overlay
- Clicking outside dashboard closes it

- [ ] **Step 4: Test desktop view**

Set viewport back to desktop (1920px)
Expected:
- Hamburger menu hidden
- Dashboard visible as fixed sidebar

- [ ] **Step 5: Commit**

```bash
git add web/index.html
git commit -m "feat: add mobile hamburger menu for dashboard toggle

- Hamburger button visible on mobile (<768px)
- Dashboard slides in as fixed overlay on mobile
- Closes when clicking outside or selecting options
- Desktop sidebar remains fixed and visible

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Phase 2: Chat Interface Components

### Task 4: Create chat container and message bubble styling

**Files:**
- Modify: `web/index.html` (add chat HTML structure + bubble CSS)

**Consumes:**
- Main layout from Task 1

**Produces:**
- Chat messages container (scrollable)
- Message bubble HTML structure and CSS
- User bubble (right-aligned, red accent)
- Bot bubble (left-aligned, gray)
- Timestamp styling

**Steps:**

- [ ] **Step 1: Replace chat area HTML**

Replace the `<main>` section:

```html
<main id="chat-area">
    <div id="messages-container" style="flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem;">
        <!-- Messages will be inserted here by JS -->
    </div>
</main>
```

- [ ] **Step 2: Add message bubble CSS**

Add to `<style>` section:

```css
#messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.message {
    display: flex;
    align-items: flex-end;
    gap: 0.5rem;
    animation: fadeIn 0.2s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.message.user {
    justify-content: flex-end;
}

.message.assistant {
    justify-content: flex-start;
}

.message-content {
    max-width: 70%;
    padding: 0.8rem 1.2rem;
    border-radius: 12px;
    word-wrap: break-word;
    white-space: pre-wrap;
}

.message.user .message-content {
    background-color: var(--color-accent-primary);
    color: white;
}

.message.assistant .message-content {
    background-color: var(--color-bg-secondary);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
}

.message-timestamp {
    font-size: 0.75rem;
    color: var(--color-text-secondary);
    margin-top: 0.3rem;
}

.message-avatar {
    font-size: 1.5rem;
    min-width: 2rem;
    text-align: center;
}

/* Mobile: Wider bubbles */
@media (max-width: 767px) {
    .message-content {
        max-width: 85%;
    }
}
```

- [ ] **Step 3: Add function to render a message bubble**

Add to `<script>` section:

```javascript
function renderMessage(content, role) {
    const messagesContainer = document.getElementById('messages-container');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    const now = new Date();
    timestamp.textContent = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    
    if (role === 'user') {
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(avatar);
    } else {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
    }
    
    messageDiv.appendChild(timestamp);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Test render
renderMessage("Hola, ¿cómo estás?", "user");
renderMessage("Estoy bien, ¿cómo puedo ayudarte?", "assistant");
```

- [ ] **Step 4: Test in browser**

Reload page
Expected:
- Two test messages visible (user on right, bot on left)
- LARIO red bubble for user, gray for bot
- Timestamps visible below each message
- Scrollable container

- [ ] **Step 5: Commit**

```bash
git add web/index.html
git commit -m "feat: implement chat message bubbles with timestamps

- Message container with auto-scroll
- User messages: right-aligned, LARIO red background
- Assistant messages: left-aligned, gray background
- Timestamps with HH:MM:SS format
- Responsive max-width for bubbles (70% desktop, 85% mobile)
- Avatar emojis (👤 user, 🤖 assistant)

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 5: Implement chat input form with send button

**Files:**
- Modify: `web/index.html` (add input HTML + CSS + JS)

**Consumes:**
- Chat area from Task 4

**Produces:**
- Input form at bottom of chat
- Text input field with placeholder
- Send button
- Form submission handling (prevent default, capture input)

**Steps:**

- [ ] **Step 1: Add input form HTML**

Add to `<main>` after messages container:

```html
<form id="chat-form" style="padding: 1.5rem; border-top: 1px solid var(--color-border); background-color: var(--color-bg-secondary); display: flex; gap: 0.8rem;">
    <input 
        id="message-input"
        type="text" 
        placeholder="Tu pregunta..." 
        autocomplete="off"
        style="flex: 1; padding: 0.8rem; background-color: var(--color-bg-primary); color: var(--color-text-primary); border: 1px solid var(--color-border); border-radius: 4px; font-size: 0.95rem;"
    />
    <button 
        id="send-btn"
        type="submit" 
        style="padding: 0.8rem 1.5rem; background-color: var(--color-accent-primary); color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; white-space: nowrap;"
    >
        Enviar
    </button>
</form>
```

- [ ] **Step 2: Add input CSS**

Add to `<style>` section:

```css
#chat-form {
    padding: 1.5rem;
    border-top: 1px solid var(--color-border);
    background-color: var(--color-bg-secondary);
    display: flex;
    gap: 0.8rem;
}

#message-input {
    flex: 1;
    padding: 0.8rem;
    background-color: var(--color-bg-primary);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-size: 0.95rem;
    font-family: inherit;
}

#message-input:focus {
    outline: none;
    border-color: var(--color-accent-primary);
    box-shadow: 0 0 0 3px rgba(227, 28, 35, 0.2);
}

#send-btn {
    padding: 0.8rem 1.5rem;
    background-color: var(--color-accent-primary);
    color: white;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    transition: opacity 0.2s;
}

#send-btn:hover {
    opacity: 0.9;
}

#send-btn:active {
    opacity: 0.8;
}

#send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
```

- [ ] **Step 3: Add input form JavaScript**

Add to `<script>` section:

```javascript
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Render user message
    renderMessage(message, 'user');
    
    // Clear input and focus
    messageInput.value = '';
    messageInput.focus();
    
    // Simulate bot response (to be replaced with API call in Phase 3)
    setTimeout(() => {
        renderMessage('Respuesta pendiente (conectar a API)', 'assistant');
    }, 500);
});

messageInput.focus();
```

- [ ] **Step 4: Test in browser**

Type a message and press Enter or click Send
Expected:
- User message appears in chat
- Input clears
- Simulated bot response appears after 500ms
- Cursor stays in input field

- [ ] **Step 5: Commit**

```bash
git add web/index.html
git commit -m "feat: implement chat input form with send functionality

- Text input field with placeholder and focus styling
- Send button (LARIO red, hover effect)
- Form submission handling
- Input clears after send
- Simulated response (placeholder for API integration)
- Cursor auto-focuses after send

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Phase 3: API Integration

### Task 6: Connect /health endpoint and show system status

**Files:**
- Modify: `web/index.html` (add health check JS)

**Consumes:**
- Dashboard from Task 2

**Produces:**
- Health check function that fetches `/health`
- Updates dashboard status display
- Auto-refresh every 30 seconds

**Steps:**

- [ ] **Step 1: Add health check function**

Add to `<script>` section:

```javascript
const API_URL = "http://localhost:8080"; // Update if backend runs on different port

async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`, { timeout: 2000 });
        const data = await response.json();
        
        const healthStatus = document.getElementById('health-status');
        if (response.ok) {
            healthStatus.innerHTML = '<span style="color: #51cf66;">✅ API Operativa</span>';
        } else {
            healthStatus.innerHTML = '<span style="color: #ff6b6b;">❌ API con error</span>';
        }
    } catch (error) {
        const healthStatus = document.getElementById('health-status');
        healthStatus.innerHTML = '<span style="color: #ff6b6b;">❌ No disponible</span>';
    }
}

// Check health on load
checkHealth();

// Auto-refresh every 30 seconds
setInterval(checkHealth, 30000);
```

- [ ] **Step 2: Test with API running**

Make sure FastAPI backend is running:
```bash
python main_api.py
```

Reload page at `http://localhost:8000/index.html`
Expected:
- Status shows "✅ API Operativa" if backend is running
- Status shows "❌ No disponible" if backend is not running

- [ ] **Step 3: Test with API stopped**

Stop the backend and observe status updates after 30 seconds
Expected:
- Status changes to error after API goes down

- [ ] **Step 4: Commit**

```bash
git add web/index.html
git commit -m "feat: implement health check endpoint integration

- Fetch /health endpoint on page load
- Display status: ✅ Operativa or ❌ No disponible
- Auto-refresh status every 30 seconds
- Graceful error handling

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 7: Connect /tools endpoint and display available tools

**Files:**
- Modify: `web/index.html` (add tools fetch JS)

**Consumes:**
- Dashboard from Task 2
- User selector from Task 2

**Produces:**
- Fetch tools for current user
- Render tools list with name and description
- Refresh when user changes

**Steps:**

- [ ] **Step 1: Add tools fetch function**

Add to `<script>` section:

```javascript
async function loadTools(usuario) {
    try {
        const response = await fetch(`${API_URL}/tools/${usuario}`);
        const data = await response.json();
        
        const toolsList = document.getElementById('tools-list');
        toolsList.innerHTML = '';
        
        if (data.tools && data.tools.length > 0) {
            data.tools.forEach(tool => {
                const toolDiv = document.createElement('div');
                toolDiv.style.marginBottom = '0.8rem';
                toolDiv.style.paddingBottom = '0.8rem';
                toolDiv.style.borderBottom = '1px solid var(--color-border)';
                
                const toolName = document.createElement('p');
                toolName.style.fontWeight = '600';
                toolName.style.color = 'var(--color-accent-primary)';
                toolName.style.marginBottom = '0.3rem';
                toolName.textContent = `🔧 ${tool.name}`;
                
                const toolDesc = document.createElement('p');
                toolDesc.style.fontSize = '0.8rem';
                toolDesc.style.color = 'var(--color-text-secondary)';
                toolDesc.textContent = tool.description;
                
                toolDiv.appendChild(toolName);
                toolDiv.appendChild(toolDesc);
                toolsList.appendChild(toolDiv);
            });
        } else {
            toolsList.textContent = 'Sin tools disponibles';
        }
    } catch (error) {
        const toolsList = document.getElementById('tools-list');
        toolsList.textContent = 'Error cargando tools';
    }
}

// Load tools on start
loadTools(currentUser);

// Reload tools when user changes
document.getElementById('user-selector').addEventListener('change', (e) => {
    if (e.target.type === 'radio') {
        currentUser = e.target.value;
        loadTools(currentUser);
    }
});
```

- [ ] **Step 2: Test with backend running**

Make sure backend is running and user changes are saved in DB
Reload page
Expected:
- Tools list populated with tool names and descriptions
- List changes when switching users (if backend has different tools per user)

- [ ] **Step 3: Commit**

```bash
git add web/index.html
git commit -m "feat: fetch and display available tools per user

- GET /tools/{usuario} integration
- Display tool name and description
- Refresh tools when user changes
- Error handling and empty state

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 8: Connect /chat endpoint and handle message sending

**Files:**
- Modify: `web/index.html` (replace chat form submit with API call)

**Consumes:**
- Chat input form from Task 5
- Current user and provider from Task 2
- renderMessage function from Task 4

**Produces:**
- POST /chat endpoint integration
- Send user message, receive bot response
- Show spinner while waiting
- Error handling with messages

**Steps:**

- [ ] **Step 1: Add chat API function**

Replace the chat form submit handler:

```javascript
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Render user message
    renderMessage(message, 'user');
    messageInput.value = '';
    
    // Disable input while processing
    messageInput.disabled = true;
    sendBtn.disabled = true;
    sendBtn.textContent = '⏳ Enviando...';
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                usuario: currentUser,
                mensaje: message,
                provider: currentProvider,
                max_iterations: 3
            }),
            timeout: 120000 // 2 minutes
        });
        
        if (response.ok) {
            const data = await response.json();
            renderMessage(data.respuesta, 'assistant');
        } else {
            const errorData = await response.json();
            const errorMsg = errorData.detail || `Error ${response.status}`;
            renderMessage(`❌ Error: ${errorMsg}`, 'assistant');
        }
    } catch (error) {
        let errorMsg = '❌ Error inesperado';
        if (error.name === 'AbortError') {
            errorMsg = '⏱️ Timeout: La solicitud tardó demasiado. Verifica la conexión.';
        } else if (error.message.includes('Failed to fetch')) {
            errorMsg = `❌ No se puede conectar a ${API_URL}`;
        }
        renderMessage(errorMsg, 'assistant');
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        sendBtn.disabled = false;
        sendBtn.textContent = 'Enviar';
        messageInput.focus();
    }
});
```

- [ ] **Step 2: Test with backend**

Make sure backend is running at `http://localhost:8080`
Try sending a message in the chat
Expected:
- Button shows "⏳ Enviando..." while processing
- Bot response appears when backend responds
- If backend is down, shows connection error

- [ ] **Step 3: Test error cases**

Stop backend, try sending message
Expected:
- "❌ No se puede conectar a http://localhost:8080" message

Test with invalid user (if backend checks):
Expected:
- Error from backend displayed in chat

- [ ] **Step 4: Commit**

```bash
git add web/index.html
git commit -m "feat: integrate /chat endpoint for message sending

- POST /chat with usuario, mensaje, provider, max_iterations
- Show spinner ⏳ while waiting for response
- Display bot response in chat
- Error handling: connection errors, API errors, timeouts
- Input disabled during request
- 120s timeout for LLM processing

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Phase 4: Polish & Testing

### Task 9: Test mobile responsiveness on various screen sizes

**Files:**
- Test: `web/index.html` (no code changes, testing only)

**Testing checklist:**

- [ ] **Step 1: Test mobile view (320px, 375px, 425px)**

In browser dev tools, set viewport to:
- 320px (iPhone SE)
- 375px (iPhone 8)
- 425px (iPhone 12)

Expected:
- Dashboard hidden, hamburger menu visible
- Chat bubbles responsive (max-width 85%)
- Input form readable and usable
- No horizontal scrolling
- All text readable

- [ ] **Step 2: Test tablet view (768px, 1024px)**

Set viewport to:
- 768px (iPad)
- 1024px (iPad Pro)

Expected:
- Dashboard visible as sidebar (20% width)
- Chat area uses 80% width
- Everything properly spaced
- No horizontal scrolling

- [ ] **Step 3: Test desktop view (1440px, 1920px)**

Set viewport to:
- 1440px (laptop)
- 1920px (desktop)

Expected:
- Dashboard sidebar fixed
- Chat area wide and readable
- Max-width bubbles at 70%
- No layout issues

- [ ] **Step 4: Test orientation changes**

On actual mobile device or emulator, rotate between portrait/landscape
Expected:
- Layout adapts smoothly
- No content hidden or overlapping
- Hamburger menu works in both orientations

- [ ] **Step 5: Document findings**

If any issues found, note them for Task 10

---

### Task 10: Cross-browser testing and compatibility fixes

**Files:**
- Test: `web/index.html` (optional fixes)

**Testing in:**
- Chrome/Edge (Chromium)
- Firefox
- Safari (macOS)
- Mobile Safari (iOS)

**Testing checklist:**

- [ ] **Step 1: Test in Chrome**

Open `http://localhost:8000/index.html` in Chrome
Expected:
- All features work
- Styling correct
- No console errors

- [ ] **Step 2: Test in Firefox**

Open in Firefox
Expected:
- All features work
- Styling correct
- No console errors

- [ ] **Step 3: Test in Safari (macOS)**

Open in Safari
Expected:
- All features work
- Check for CSS/JS compatibility issues

- [ ] **Step 4: Test on actual iOS device**

If available, test on iPhone/iPad
Expected:
- Touch interactions work
- Mobile menu works
- Chat is usable

- [ ] **Step 5: Fix any compatibility issues**

If found, apply fixes to `web/index.html`
Common issues:
- CSS prefixes for older browsers (if needed)
- Fetch API polyfills (usually not needed for modern browsers)
- Touch event handling

- [ ] **Step 6: Commit if changes made**

```bash
git add web/index.html
git commit -m "fix: cross-browser compatibility adjustments

- [List any specific fixes]
- Tested on Chrome, Firefox, Safari
- Mobile touch interactions verified

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 11: Final polish and UX improvements

**Files:**
- Modify: `web/index.html` (final refinements)

**Polish items:**

- [ ] **Step 1: Add keyboard shortcuts**

Add to `<script>` section:

```javascript
// Focus input with Ctrl+K
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        messageInput.focus();
    }
});
```

- [ ] **Step 2: Add loading state to health check**

Update health check to show last update time:

```javascript
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`, { timeout: 2000 });
        const data = await response.json();
        
        const healthStatus = document.getElementById('health-status');
        const now = new Date();
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
        
        if (response.ok) {
            healthStatus.innerHTML = `<span style="color: #51cf66;">✅ API Operativa</span><br><span style="font-size: 0.8rem; color: var(--color-text-secondary);">${timeStr}</span>`;
        } else {
            healthStatus.innerHTML = `<span style="color: #ff6b6b;">❌ Error ${response.status}</span>`;
        }
    } catch (error) {
        const healthStatus = document.getElementById('health-status');
        healthStatus.innerHTML = '<span style="color: #ff6b6b;">❌ No disponible</span>';
    }
}
```

- [ ] **Step 3: Optimize scrolling**

Ensure auto-scroll only when at bottom:

```javascript
function renderMessage(content, role) {
    const messagesContainer = document.getElementById('messages-container');
    const wasAtBottom = messagesContainer.scrollTop + messagesContainer.clientHeight >= messagesContainer.scrollHeight - 10;
    
    // ... existing code ...
    
    if (wasAtBottom) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}
```

- [ ] **Step 4: Add empty state message**

Add to `<script>` section on load:

```javascript
// Show initial greeting
window.addEventListener('load', () => {
    const messagesContainer = document.getElementById('messages-container');
    if (messagesContainer.children.length === 0) {
        renderMessage('Hola 👋 ¿En qué puedo ayudarte?', 'assistant');
    }
});
```

- [ ] **Step 5: Test all improvements**

Reload page
Expected:
- Greeting message on load
- Cmd+K (or Ctrl+K) focuses input
- Health check shows time
- Auto-scroll works smoothly

- [ ] **Step 6: Commit**

```bash
git add web/index.html
git commit -m "feat: final polish and UX improvements

- Keyboard shortcut: Ctrl+K (Cmd+K on Mac) to focus input
- Health check displays last update time
- Smart auto-scroll (only when at bottom)
- Initial greeting message on load
- Improved scrolling UX

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 12: Create README and documentation

**Files:**
- Create: `web/README.md`

**Steps:**

- [ ] **Step 1: Write README for web app**

```markdown
# Chat Cuenta Corriente — SPA Frontend

Single-page application (SPA) built with vanilla HTML5, CSS3, and JavaScript.

## Running Locally

```bash
# Terminal 1: Start backend API
python main_api.py

# Terminal 2: Serve frontend (from project root)
cd web && python -m http.server 8000
```

Then open: `http://localhost:8000/index.html`

## Architecture

- **Single file:** `index.html` contains all HTML, CSS, and JavaScript
- **No dependencies:** Pure vanilla JavaScript, no frameworks
- **LARIO brand:** Dark mode with red accents (#E31C23)
- **Responsive:** Desktop (sidebar visible) and mobile (hamburger menu)

## Features

- ✅ User selector (vendedor1, vendedor2, gerente1) with RBAC
- ✅ LLM provider selector (Ollama, Claude Haiku)
- ✅ System health check (auto-refresh every 30s)
- ✅ Tools display (per user)
- ✅ Example questions (clickable)
- ✅ Chat interface with message bubbles
- ✅ Auto-scrolling chat history
- ✅ Real-time API integration

## Keyboard Shortcuts

- **Ctrl+K** (Cmd+K on Mac): Focus message input

## Testing

### Mobile Responsiveness
- Open dev tools → Device Toolbar
- Test on 320px (mobile), 768px (tablet), 1920px (desktop)

### API Integration
- Ensure backend runs at `http://localhost:8080`
- Check browser console for errors
- Test with backend stopped to see error messages

## Browser Support

- Chrome/Edge ✅
- Firefox ✅
- Safari ✅
- Mobile browsers ✅

## Customization

All styling uses CSS variables in `:root`. To change colors, edit:

```css
--color-bg-primary: #0a0a0a;        /* Main background */
--color-accent-primary: #E31C23;    /* LARIO red */
--color-accent-secondary: #D4A574;  /* Gold accent */
--color-text-primary: #ffffff;      /* Main text */
```

## Performance

- **First load:** Single HTML file (~20KB)
- **No build step:** Just open in browser
- **Network:** Calls to `/chat`, `/health`, `/tools/{usuario}` via Fetch API
- **Timeout:** 120s for LLM responses, 2s for health checks

## Troubleshooting

**API connection error:**
- Check backend is running at `http://localhost:8080`
- Check CORS if cross-origin issues

**Styling issues:**
- Clear browser cache (Ctrl+Shift+Del or Cmd+Shift+Del)
- Check browser console for errors

**Mobile menu not working:**
- Test in actual mobile or device emulator
- Check viewport meta tag is present

---

**Built with:** HTML5, CSS3, JavaScript ES6+  
**Backend:** FastAPI (unchanged)  
**Tested:** Chrome, Firefox, Safari, Mobile
```

- [ ] **Step 2: Commit README**

```bash
git add web/README.md
git commit -m "docs: add README for SPA frontend

- Setup instructions for local development
- Architecture overview
- Features list
- Keyboard shortcuts
- Testing guidelines
- Browser support
- Customization guide
- Troubleshooting section

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Summary

**Total Tasks:** 12  
**Estimated Time:** 4-6 hours (depending on execution pace)

**Deliverables:**
- ✅ Single-page application in `web/index.html`
- ✅ LARIO brand dark mode styling
- ✅ Responsive dashboard + chat layout
- ✅ Mobile hamburger menu
- ✅ API integration (all endpoints)
- ✅ Error handling and user feedback
- ✅ Cross-browser tested
- ✅ Documentation and README

**Success Criteria (from spec):**
- ✅ Fully responsive (320px to 1920px)
- ✅ Dark mode with LARIO colors
- ✅ All existing features work (RBAC, tools, provider switching)
- ✅ Chat bubbles with timestamps
- ✅ Mobile hamburger menu
- ✅ Zero external dependencies
- ✅ Graceful error handling
- ✅ Auto-scrolling chat history

---

**Next Step:** Choose execution approach:

**1. Subagent-Driven (Recommended)**  
I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution**  
Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
