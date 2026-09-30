# ADR-0005 — Exposición a Internet (propuesta)

- **Estado:** propuesta — **pendiente de decisión** (depende de si el operador
  usa CGNAT y del dominio elegido).
- **Contexto:** R8. El servicio vivirá en el nodo HP (`nodochicohp`).

## Opciones

| Opción | Ventajas | Inconvenientes |
|---|---|---|
| Caddy + dominio + redirección de puertos | Control total, HTTPS automático | Expone la IP doméstica; inviable con CGNAT (habitual en operadores españoles); requiere DDNS |
| Cloudflare Tunnel | Sin puertos abiertos, oculta la IP, WAF/DDoS básico | Dependencia de terceros; TLS termina en su borde; vigilar buffering de SSE |
| Tailscale Funnel | Muy simple | Dominio `*.ts.net`, límites de ancho de banda y sin dominio propio |
| VPS pequeño como proxy + túnel (Tailscale/WireGuard) al HP | Mejor aislamiento; IP pública desacoplada de casa | Coste mensual y un nodo más |

## Recomendación provisional

1. Si el operador **no** usa CGNAT: **Caddy + dominio** con redirección de
   puertos 80/443 (la opción ya preparada en `deploy/Caddyfile`).
2. Si usa CGNAT: **Cloudflare Tunnel** con Caddy delante solo en localhost
   (mantener `flush_interval -1` y SSE sin buffering) o **VPS proxy + Tailscale**.

## Requisitos comunes

- Ollama y la torre/Dell **solo** por Tailscale; ningún puerto de inferencia
  expuesto (verificación externa en T7.5).
- HSTS, CSP y cabeceras ya aplicadas por Caddy y por la app.
- SSE verificado sin buffering desde red móvil externa.
