# Política de privacidad y datos — CV Web

> Documento vivo. Última actualización: 2026-09-30 (T1.1 de `plan.md`).
> La política pública de cara al visitante se redactará en T6.6.

## 1. Principios

1. El repositorio `rufae/CV-Web` es **público** y no debe contener datos personales
   innecesarios ni secretos (decisión D7 de `plan.md`).
2. El asistente público **solo** podrá consultar información publicable del portfolio
   (política de allow-list de la Fase 3, T3.1). El vault privado de Obsidian nunca se
   expone ni se indexa completo.
3. Los secretos viven únicamente en:
   - `.env` local (fuera de git, `chmod 600` en servidor),
   - variables de entorno del servicio (systemd `EnvironmentFile`),
   - gestores de las plataformas externas mientras sigan activas.

## 2. Qué NO se versiona

| Dato | Ubicación |
|---|---|
| Contexto personal con fecha de nacimiento y contacto (`rafa_context.txt`) | `/home/rafael/PROYECTOS/CVWEB.private/` (fuera del repo) |
| Teléfono personal | Eliminado del código en T1.1; contacto solo por email/formulario |
| Claves `GOOGLE_API_KEY`, `PASSWORD_APPLICATION`, `EMAIL` | `.env` ignorado por git |
| Futuras bases de datos (`feedback.db`, outbox de contacto) | `DATA_PATH` del servidor, nunca en git |

## 3. Rotación de credenciales

- La `GOOGLE_API_KEY` y la contraseña de aplicación de Gmail usadas en Render/Vercel se
  **revocaron y rotaron** al ejecutar T1.1.
- El historial del monorepo se purgó con `git filter-repo` para eliminar
  `backend/rafa_context.txt` de todos los commits.
- Los repositorios antiguos (`CVWeb-Back`, `CVWeb-Front`) deben borrarse o limpiarse al
  cerrar el despliegue (M1/T7.11) porque conservan el mismo historial.

## 4. Retención y tratamiento (a completar en T6.6)

- Mensajes de contacto: definir retención (propuesta: 12 meses) y base legal RGPD.
- Feedback del chat: anónimo, sin pregunta ni IP (T4.9).
- Conversaciones del chat: no se almacenan en servidor.
- Sin cookies de seguimiento; analítica autoalojada opcional (T6.6).

## 5. Verificación

- `gitleaks git .` limpio sobre todo el historial.
- `git log --all -- backend/rafa_context.txt` vacío tras la purga.
- `git grep` de teléfono/fecha de nacimiento sin resultados.
