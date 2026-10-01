# Baúl (Obsidian) y permisos para CVWEB

CVWEB **solo** puede leer la carpeta pública del baúl. El resto del segundo
cerebro (privado) no se monta, no se lee y no se indexa.

## Estructura propuesta del baúl

```
mi_boveda_obsidian/
├── Public/                     # ÚNICA carpeta que CVWEB puede ver (solo lectura)
│   ├── portfolio/
│   │   └── facts.md            # nota canónica del portfolio (cv_public: true)
│   ├── proyectos/              # fichas públicas de proyectos (cv_public: true)
│   └── notas/                  # material público adicional (cv_public: true)
├── Privado/                    # diario, finanzas, contactos… CVWEB JAMÁS la ve
├── 00-Inbox/ 01-Proyectos/ 02-Areas/ 03-Recursos/ …
└── Reuniones/  Briefings/  Google/  CRM/  Radar/
```

Reglas de indexación (implementadas en `backend/app/rag/ingest.py`):

1. Solo se recorren ficheros `.md` dentro de `Public/`.
2. Cada nota debe llevar en el frontmatter `cv_public: true`.
3. Se redactan datos sensibles antes de indexar.
4. Se ignoran symlinks y cualquier ruta que resuelva fuera del baúl.
5. El índice (Chroma) vive fuera del baúl y se monta como volumen de datos.

## Aislamiento por sistema de ficheros (lo importante)

El contenedor **no monta el baúl entero**: se monta únicamente la carpeta
pública en modo lectura.

```yaml
# compose.yaml
volumes:
  - ./data:/data
  - <baul>/Public:/vault/Public:ro    # SOLO Public, read-only
```

```dotenv
# .env
VAULT_PATH=/vault
PUBLIC_VAULT_DIR=Public
```

Así, aunque hubiera un fallo de software, CVWEB no puede leer `Privado/`,
`Reuniones/` ni el resto: no están dentro del contenedor.

## Fase actual (mock) y paso a producción

- **Ahora**: `vault_mock/` (datos sintéticos) valida el flujo completo en
  desarrollo/tests. En el HP, `<baul>` apunta a la carpeta pública provisional
  (`~/proyectos/rafita/mi_boveda_obsidian/Public`), que solo contiene la nota
  pública del portfolio.
- **Producción**: cuando el baúl oficial esté listo, basta cambiar el montaje a
  `<baul-oficial>/Public:/vault/Public:ro` y reindexar
  (`docker compose exec cvweb python scripts/ingest_public_vault.py`).
  No hay que tocar código ni configuración de la app.

## Rafita vs CVWEB

- **Rafita** (uso personal) lee el baúl completo: es su segundo cerebro.
- **CVWEB** lee solo `Public/` + `cv_public: true`: el mismo motor, con
  aislamiento estricto para visitantes.
