# ADR-0001 — Allow-list de publicación del Segundo Cerebro

- **Estado:** aceptada (2026-09-30, T3.1)
- **Contexto:** R2 exige que el chat público no pueda leer el vault privado. La
  ingesta debe decidir qué sale del Segundo Cerebro **antes** de escribir código.

## Decisión

1. **Carpeta publicable única:** `Public/` en la raíz del vault, con subcarpetas
   según necesidad: `sobre-mi/`, `experiencia/`, `proyectos/`, `stack/`,
   `certificaciones/`. No se crean de más.
2. **Doble puerta:** una nota se indexa **solo** si cumple las dos condiciones:
   - (a) está dentro de `Public/`;
   - (b) su frontmatter contiene `cv_public: true`.
3. **Deny-list explícita** (nunca se lee, ni siquiera para listar):
   `Privado/`, `Diario/`, `Contactos/`, `Finanzas/`, `Salud/`, `Salud-mental/`,
   `.obsidian/`, `_templates/`, adjuntos binarios. Cualquier ruta fuera de
   `Public/` está excluida por defecto.
4. **Redacción como red de seguridad:** aunque estén en una nota pública, se
   eliminan emails, teléfonos, DNI/NIE, IBAN y fechas de nacimiento detectadas.
5. **Limpieza de sintaxis Obsidian:** los `[[wikilinks]]` se degradan a texto plano
   (alias si existe; si no, solo el **nombre** de la nota, sin carpeta, para no
   revelar rutas privadas); se eliminan embeds (`![[...]]`), bloques de comentario
   `%%...%%` y callouts se convierten a texto.
6. La ingesta es **de solo lectura** sobre el vault original.

## Consecuencias

- Toda nota publicable necesita el frontmatter válido
  (`title`, `cv_public: true`, `tags`, `updated`, `lang`); plantilla en
  `docs/templates/public-note.md`.
- Al quitar `cv_public: true` (o mover la nota fuera de `Public/`), sus chunks se
  borran en la siguiente ingesta (T3.5).
- El chat recibe solo `título + sección`, nunca rutas de fichero.
- El contenido binario (PDF, imágenes) no se indexa.
