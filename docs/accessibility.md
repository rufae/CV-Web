# Accesibilidad — informe (T6.7)

> Última actualización: 2026-09-30. La auditoría manual se completa tras el
> despliegue (T7.9).

## Automatizado (verde)

- `axe-core` en jsdom sin violaciones **serias/críticas**:
  - lanzador y panel del chat (`features/chat/__tests__/a11y.test.tsx`),
  - app completa en tema claro y oscuro (`app/__tests__/a11y-app.test.tsx`).
- Contraste AA verificado en tokens (texto principal 21:1 / 18,76:1; muted
  5,62:1 / 7,68:1, T1.6) y mensajes del chat con `--card-foreground`.
- Foco: `focus-visible` global, anillo en tarjetas/acciones del chat, trampa de
  foco en el diálogo y retorno al lanzador.
- Anuncios: la respuesta se anuncia **al completarse** vía `aria-live="polite"`
  (sin anunciar token a token).
- `prefers-reduced-motion`: desactiva animaciones CSS (typing, glow, transiciones).
- Objetivos táctiles ≥44 px en acciones del chat y starters (compactos en ≥sm).
- Formularios con `label` asociada; progreso de skills con nombre accesible.

## Checklist manual (pendiente de ejecutar en el navegador)

- [ ] Recorrido completo con teclado (Tab/Shift+Tab/Enter/Esc) sin trampas.
- [ ] Lector de pantalla (NVDA o VoiceOver): navegación por landmarks y lectura
      del chat al completarse la respuesta.
- [ ] Chrome, Firefox, Safari (iOS) y Android real.
- [ ] Zoom al 200 % sin pérdida de contenido ni scroll horizontal.
- [ ] Modo “reducir movimiento” del sistema operativo.
- [ ] Contraste real en pantalla de los estados (offline/degraded/rate-limit).
