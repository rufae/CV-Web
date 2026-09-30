# Política de seguridad

## Reporte de vulnerabilidades

Escribe a **rafaelcastanoblanca1805@gmail.com** con el asunto
`[SECURITY] CV-Web`. No abras issues públicos para vulnerabilidades. Se
responderá en un máximo de 7 días.

## Alcance

- API pública: `/api/chat`, `/api/contact`, `/api/feedback`, `/api/status`.
- No se aceptan pruebas que envíen spam real por el formulario, consuman cuota
  de LLM deliberadamente o ataquen la infraestructura doméstica.

## Medidas vigentes

- Rate limiting por IP, tope de cuerpo (16 KB) y presupuesto diario de chat.
- Sanitización de entrada, bloqueo de extracción de prompt/datos, detección de
  inyección; prompt con canario y contexto delimitado/escaper; output guard de
  fuga de prompt/PII/URLs.
- Contacto con honeypot, Turnstile opcional, escape HTML, sin inyección de
  cabeceras y outbox con reintentos.
- CSP/HSTS y cabeceras vía app y Caddy; `/docs` desactivado en producción.
- Secretos solo en `.env` (600) o `EnvironmentFile` de systemd; historial de git
  purgado de datos personales.
- `gitleaks`, `pip-audit` y `npm audit` en CI; cobertura ≥85% y suite red-team.

Detalle completo en [`docs/security.md`](docs/security.md) y
[`docs/privacy.md`](docs/privacy.md).
