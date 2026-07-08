# Chat Cuenta Corriente — Redesign SPA Dark Mode

**Date:** 2026-07-08  
**Status:** Design Approved  
**Scope:** Frontend visual redesign from Streamlit to HTML5 SPA with dark mode

---

## 1. Overview

Migrate the Chat Cuenta Corriente frontend from Streamlit to a modern, responsive Single Page Application (SPA) built with vanilla HTML5, CSS3, and JavaScript. The new interface features a dark mode theme, a fixed dashboard panel (desktop) / collapsible menu (mobile), and modern chat bubbles for conversation rendering.

**Key Goals:**
- Eliminate Streamlit dependency for frontend
- Achieve native app-like experience on mobile
- Maintain all existing functionality (RBAC, tool selection, LLM provider switching)
- Zero external dependencies (no frameworks, libraries, or build tools)

---

## 2. Architecture

### 2.1 Tech Stack
- **Frontend:** HTML5 + CSS3 (Grid, Flexbox) + JavaScript ES6+
- **Backend:** Existing FastAPI (unchanged)
- **Communication:** Fetch API for async requests
- **Deployment:** Static files served from FastAPI or separate static server

### 2.2 Project Structure
```
web/
├── index.html          # Single HTML file with inline CSS + JS
├── styles/
│   └── main.css        # (Optional: external CSS if needed)
└── assets/
    └── (favicons, logos if any)

# Keep existing backend untouched
main_api.py            # FastAPI unchanged
```

### 2.3 Communication Flow
```
User Input
    ↓
JavaScript event listener
    ↓
Fetch POST /chat {usuario, mensaje, provider, max_iterations}
    ↓
FastAPI processes
    ↓
JSON response {respuesta, ...}
    ↓
Render message bubble in chat
    ↓
Append to message history (session storage or in-memory)
```

---

## 3. Layout & Responsive Design

### 3.1 Desktop (≥768px)
```
┌─────────────────────────────────────────┐
│  ☰ Menu (hidden)  | Chat Title          │
├──────────┬────────────────────────────────┤
│          │                                │
│ Dashboard│          Chat Messages         │
│ (20%)    │          (80%)                 │
│          │                                │
│ • User   │  User msg (right, bubble)     │
│ • LLM    │  Bot msg (left, bubble)       │
│ • Status │  User msg (right, bubble)     │
│ • Tools  │                                │
│ • Tips   │  ┌──────────────────────────┐ │
│          │  │ Type message... [Send]    │ │
│          │  └──────────────────────────┘ │
└──────────┴────────────────────────────────┘
```

### 3.2 Mobile (<768px)
- Dashboard hidden by default
- Hamburger menu (☰) toggles overlay panel
- Chat occupies full width
- Input at bottom (sticky)

```
┌─────────────────┐
│ ☰ | Chat Title  │
├─────────────────┤
│ Chat Messages   │
│ (full width)    │
│                 │
│ User msg bubble │
│ Bot msg bubble  │
│                 │
├─────────────────┤
│ Type... [Send]  │
└─────────────────┘
```

---

## 4. Components & UI Elements

### 4.1 Dashboard Panel (Left)

**Logo & Title**
- "💰 Chat Cuenta Corriente"
- Subtitle: "Consulta deudas con IA"

**User Selector**
- Radio buttons or select dropdown
- Options: Vendedor1, Vendedor2, Gerente1
- Shows user permissions/zones inline

**LLM Provider Selector**
- Dropdown or radio buttons
- Options: "Ollama (local, Qwen2.5)", "Claude Haiku (cloud)"

**System Status**
- Health check indicator: "✅ API Operativa" or "❌ API Caída"
- Auto-refreshes every 30 seconds
- Shows last check timestamp

**Tools Available**
- Accordion/expandable list of tools accessible to the current user
- Each tool shows: name, description, status

**Example Questions**
- 4-6 clickable suggestion buttons
- Examples: "¿Cuánto debe cliente 3523?", "Top 3 morosos", etc.
- Clicking fills the input and sends automatically

### 4.2 Chat Panel (Right)

**Message History**
- Scrollable container with all messages
- Bubbles are rendered with:
  - **User messages:** right-aligned, teal/cyan background
  - **Bot messages:** left-aligned, dark gray background
  - Timestamp below each message (HH:MM:SS)
  - Avatar emoji (👤 for user, 🤖 for bot)

**Message Rendering**
- Plain text messages rendered as-is
- Support for Markdown (optional: if response contains MD, render formatted)
- Debt response detection: if message contains "$", "deuda", "mora", flag for potential data highlight

**Input Area (Sticky at Bottom)**
- Text input field: "Tu pregunta..."
- Send button: "Enviar" (teal/cyan)
- On submit: disable input, show spinner "⏳ Procesando..."
- Auto-scroll to latest message

---

## 5. Color Palette (Dark Mode)

| Element | Color | Usage |
|---------|-------|-------|
| Background Primary | `#0a0e27` | Main bg, very dark blue-black |
| Background Secondary | `#1a1f3a` | Panel bg, slightly lighter |
| Accent | `#06d6d0` | Buttons, highlights, user bubbles |
| Text Primary | `#e0e6ed` | Main text, almost white |
| Text Secondary | `#a8b2c1` | Muted text, timestamps |
| Border | `#2a2f4a` | Borders, dividers |
| Bot Bubble | `#252d4a` | Bot message background |
| User Bubble | `#06d6d0` (with opacity 0.2) | User message highlight |
| Error | `#ff6b6b` | Error messages |
| Success | `#51cf66` | Success messages |

---

## 6. Interactions & Behavior

### 6.1 Dashboard Interactions

**User Switch**
- Changing user clears chat history
- Reloads tools for new user
- Updates health status

**Provider Switch**
- Changes provider for next request
- No history clear

**Click Example Question**
- Auto-fills input field
- Sends message immediately
- Equivalent to user typing and clicking Send

### 6.2 Chat Interactions

**Send Message**
- Enter key or click Send button both work
- Input clears on send
- Spinner shows while waiting
- Message appends to history with timestamp
- Auto-scroll to bottom

**Error Handling**
- Network errors: show error banner at top of chat
- API errors (401, 403, 500): display error message as bot response
- Timeout: show helpful message (check Ollama, API status, etc.)

**Session Persistence**
- Store messages in `sessionStorage` (cleared on tab close)
- Or in-memory array (simpler)
- User/Provider selection in `localStorage` (persists across tabs)

---

## 7. Performance & Loading

- **First Load:** Single HTML file (~50-100KB with CSS+JS inline)
- **No build step:** Open `index.html` directly in browser
- **No external CDNs:** All CSS/JS self-contained
- **API Calls:** Fetch API with timeout (120s for LLM, 2s for health check)

---

## 8. Accessibility & Mobile

- Semantic HTML (`<main>`, `<nav>`, `<form>`, etc.)
- ARIA labels where necessary
- Keyboard navigation: Tab through inputs, Enter to send
- Viewport meta tag: responsive design
- Touch-friendly buttons (min 44x44px)
- Dark mode respects `prefers-color-scheme` (optional enhancement)

---

## 9. API Contracts (No Changes)

All existing endpoints remain unchanged:
- `POST /chat` → `{usuario, mensaje, provider, max_iterations}`
- `GET /health` → `{status}`
- `GET /tools/{usuario}` → `{tools: [...]}`

---

## 10. Implementation Phases

### Phase 1: Scaffold & Dashboard
- Create index.html with basic structure
- Implement dashboard panel (static, no API calls yet)
- Implement mobile hamburger menu
- CSS for dark mode, layout, responsiveness

### Phase 2: Chat Interface
- Message bubble rendering (user + bot)
- Input form with Send button
- Message history in-memory storage
- Auto-scroll behavior

### Phase 3: API Integration
- Connect /chat endpoint
- Connect /tools endpoint
- Connect /health endpoint
- Error handling, spinners, timeouts

### Phase 4: Polish & Testing
- Mobile responsiveness testing
- Cross-browser testing (Chrome, Firefox, Safari)
- Performance optimization
- UX refinements

---

## 11. Success Criteria

- ✅ Fully responsive (desktop 1920px, tablet 768px, mobile 320px)
- ✅ Dark mode applied consistently
- ✅ All existing features work (RBAC, tools, provider switching)
- ✅ Chat bubbles render cleanly with timestamps
- ✅ Mobile hamburger menu works smoothly
- ✅ No external dependencies (vanilla JS/CSS)
- ✅ API calls timeout gracefully
- ✅ Zero console errors
- ✅ Loads in <2 seconds on 4G

---

## 12. Post-Launch Enhancements (Out of Scope)

- Markdown rendering in messages
- Copy message to clipboard
- Message export/download
- Dark/Light theme toggle
- Search chat history
- Multiple conversations/tabs
- User avatar customization
