# ADR-0004 — Fuente única de verdad del contenido

- **Estado:** aceptada (2026-09-30, T6.1)
- **Contexto:** R11 (divergencia entre lo que dice la web y lo que responde el
  chat). El vault público ya es la fuente del RAG (Fase 3).

## Decisión

1. **Nota canónica** `Public/portfolio/facts.md` con `cv_public: true` y un
   bloque `facts` en el frontmatter (perfil, experiencia, proyectos,
   habilidades, certificaciones e idiomas). Su **cuerpo** resume lo mismo para
   que el asistente pueda responder.
2. **Exportador** `backend/scripts/build_facts.py` genera
   `frontend/src/content/facts.json`; la web renderiza ese JSON (tipado en
   `src/content/facts.ts`). El JSON se versiona.
3. **Verificación** `eval/check_consistency.py`:
   - falla si `facts.json` no coincide con el frontmatter del vault (dato
     cambiado “solo en un lado”),
   - falla si algún término de `facts` (empresas, proyectos, tecnologías) no
     aparece en el corpus público,
   - falla si hay canarios o términos sensibles.
4. Sin datos personales: teléfono/DNI/IBAN/fecha de nacimiento quedan fuera por
   la propia política (ADR-0001) y por la verificación.

## Consecuencias

- Editar el vault exige ejecutar el exportador (o el check de CI fallará): es el
  precio de que web y chat no divergen.
- El pipeline real (`VAULT_PATH` del nodo) sustituirá al vault fixture cuando el
  usuario cree su `Public/`; basta regenerar y revisar.
- Los textos de UI (botones, títulos) siguen en los componentes; los **datos**
  del portfolio viven solo en el vault.
