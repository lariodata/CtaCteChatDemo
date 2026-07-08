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
