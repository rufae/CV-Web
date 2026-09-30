"""Extracción y filtrado del vault público (T3.2).

Aplica la política de `docs/adr/0001-public-vault-allowlist.md`:
doble puerta (`Public/` + `cv_public: true`), limpieza de sintaxis Obsidian y
redacción de patrones sensibles como red de seguridad. El vault es de solo
lectura: jamás se escribe en él.
"""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import frontmatter

PUBLIC_DIR_DEFAULT = "Public"
CV_PUBLIC_FIELD = "cv_public"
MARKDOWN_SUFFIXES = {".md", ".markdown"}

DENY_DIRS = {
    "Privado",
    "Diario",
    "Contactos",
    "Finanzas",
    "Salud",
    "Salud-mental",
    ".obsidian",
    "_templates",
    ".trash",
}

_REDACTIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email redactado]"),
    (
        re.compile(
            r"\b(?:\+34[\s.-]?)?(?:6\d{2}|7\d{2}|9\d{2})[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b"
        ),
        "[teléfono redactado]",
    ),
    (re.compile(r"\b[XYZ]?\d{7,8}[A-Z]\b"), "[DNI/NIE redactado]"),
    (re.compile(r"\bES\d{2}[ ]?(?:\d{4}[ ]?){5}\b"), "[IBAN redactado]"),
    (
        re.compile(
            r"(?i)\b(?:nacimiento|nacido|nacid[ao]|born)\b[^\n]{0,40}?\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
        ),
        "[fecha de nacimiento redactada]",
    ),
)

_OBSIDIAN_COMMENT = re.compile(r"%%[\s\S]*?%%")
_HTML_COMMENT = re.compile(r"<!--[\s\S]*?-->")
_WIKILINK = re.compile(r"(!)?\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")
_CALLOUT_MARKER = re.compile(r"^>\s*\[![^\]]+\][-+]?\s*", re.MULTILINE)


@dataclass(frozen=True)
class PublicNote:
    relative_path: str
    title: str
    tags: tuple[str, ...]
    lang: str
    updated: str | None
    content: str
    redactions: int

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class IngestResult:
    notes: tuple[PublicNote, ...]
    manifest: dict[str, str]
    redactions: int


def clean_obsidian(content: str) -> str:
    content = _OBSIDIAN_COMMENT.sub("", content)
    content = _HTML_COMMENT.sub("", content)

    def _replace_link(match: re.Match[str]) -> str:
        is_embed = match.group(1) == "!"
        target = match.group(2).strip()
        section = match.group(3)
        alias = match.group(4)
        if is_embed:
            return ""
        label = (alias or target.rsplit("/", 1)[-1]).strip()
        if section:
            label = f"{label} › {section.strip()}"  # noqa: RUF001
        return label

    content = _WIKILINK.sub(_replace_link, content)
    content = _CALLOUT_MARKER.sub("", content)
    return content.strip()


def redact_sensitive(content: str) -> tuple[str, int]:
    redactions = 0
    for pattern, replacement in _REDACTIONS:
        content, count = pattern.subn(replacement, content)
        redactions += count
    return content, redactions


def _is_denied(relative_path: str) -> bool:
    return any(part in DENY_DIRS for part in Path(relative_path).parts)


def _stringify_updated(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return str(value.isoformat())
    return str(value)


def _load_metadata(path: Path) -> tuple[dict[str, Any], str]:
    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    metadata: dict[str, Any] = dict(post.metadata)
    return metadata, post.content


def extract_public_notes(vault_path: Path, *, public_dir: str = PUBLIC_DIR_DEFAULT) -> IngestResult:
    public_root = vault_path / public_dir
    if not public_root.is_dir():
        return IngestResult((), {}, 0)

    notes: list[PublicNote] = []
    manifest: dict[str, str] = {}
    total_redactions = 0

    for path in sorted(public_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in MARKDOWN_SUFFIXES:
            continue
        relative = path.relative_to(vault_path).as_posix()
        if _is_denied(relative):
            continue

        metadata, raw_content = _load_metadata(path)
        if metadata.get(CV_PUBLIC_FIELD) is not True:
            continue

        cleaned = clean_obsidian(raw_content)
        redacted, redactions = redact_sensitive(cleaned)
        total_redactions += redactions

        note = PublicNote(
            relative_path=relative,
            title=str(metadata.get("title") or path.stem),
            tags=tuple(str(tag) for tag in (metadata.get("tags") or [])),
            lang=str(metadata.get("lang") or "es"),
            updated=_stringify_updated(metadata.get("updated")),
            content=redacted,
            redactions=redactions,
        )
        notes.append(note)
        manifest[relative] = note.content_hash

    return IngestResult(tuple(notes), manifest, total_redactions)
