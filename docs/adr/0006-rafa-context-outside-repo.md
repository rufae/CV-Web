# ADR-0006 — Ubicación y acceso al contexto personal hasta la Fase 3

- **Estado:** aceptada (2026-09-30, T1.1)
- **Contexto:** `rafa_context.txt` contiene datos personales y salió del repositorio en
  T1.1. Hasta que la Fase 3 sustituya la inyección de contexto por RAG, el backend lo
  sigue necesitando para el endpoint `/ask`.
- **Decisión:**
  1. El fichero vive fuera del repo, en `/home/rafael/PROYECTOS/CVWEB.private/rafa_context.txt`.
  2. La aplicación lo leerá desde la ruta indicada por la variable de entorno
     `RAFA_CONTEXT_PATH` (sin ruta por defecto dentro del repo). T1.3 la implementa en
     `core/config.py`.
  3. Para desarrollo local se permite una copia en `backend/rafa_context.txt`, ignorada
     por git (patrón añadido a `backend/.gitignore`).
  4. En la Fase 3 (T3.4/T3.5) el fichero se retira por completo del flujo: el contexto
     pasa a ser la colección `cvweb_public`.
- **Consecuencias:**
  - El arranque sin `RAFA_CONTEXT_PATH` (o sin el fichero) debe fallar con un mensaje
    claro solo si el chat está habilitado, sin romper el resto de la app.
  - El despliegue del HP debe provisionar el fichero a mano (scp/gestor de secretos),
    nunca vía git.
