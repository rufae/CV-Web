"""Chunking consciente de Markdown (T3.3).

- Divide por encabezados y conserva la ruta de secciones (`Título › Sección`).
- Bloques ~300-500 tokens con solape corto, sin cortar listas ni bloques de código.
- Ids deterministas (hash de `source_id + contexto + texto`) para reindexado
  idempotente.
"""

import hashlib
import re
from dataclasses import dataclass

from app.rag.ingest import PublicNote

MAX_TOKENS = 450
OVERLAP_TOKENS = 50
CHARS_PER_TOKEN = 4

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_FENCE = ("```", "~~~")
_SECTION_SEPARATOR = " › "


@dataclass(frozen=True)
class Chunk:
    id: str
    source_id: str
    title: str
    section: str
    tags: tuple[str, ...]
    lang: str
    updated: str | None
    context: str
    text: str

    @property
    def embedded_text(self) -> str:
        return f"{self.context}\n\n{self.text}" if self.context else self.text


@dataclass
class _Section:
    headings: tuple[str, ...]
    body: str


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def chunk_note(
    note: PublicNote,
    *,
    max_tokens: int = MAX_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for section in _split_sections(note.content):
        headings = list(section.headings)
        if headings and headings[0].lower() == note.title.lower():
            headings = headings[1:]
        section_label = _SECTION_SEPARATOR.join(headings)
        context = _build_context(note.title, section_label)
        for text in _chunk_text(section.body, max_tokens, overlap_tokens):
            chunks.append(
                Chunk(
                    id=_chunk_id(note.relative_path, context, text),
                    source_id=note.relative_path,
                    title=note.title,
                    section=section_label,
                    tags=note.tags,
                    lang=note.lang,
                    updated=note.updated,
                    context=context,
                    text=text,
                )
            )
    return chunks


def _build_context(title: str, section_label: str) -> str:
    if not section_label or section_label.lower() == title.lower():
        return title
    return f"{title}{_SECTION_SEPARATOR}{section_label}"


def _chunk_id(source_id: str, context: str, text: str) -> str:
    digest = hashlib.sha256(f"{source_id}|{context}|{text}".encode())
    return digest.hexdigest()[:16]


def _split_sections(markdown: str) -> list[_Section]:
    sections: list[_Section] = []
    stack: list[tuple[int, str]] = []
    current: list[str] = []
    current_headings: tuple[str, ...] = ()

    def close() -> None:
        body = "\n".join(current).strip()
        if body:
            sections.append(_Section(current_headings, body))
        current.clear()

    for line in markdown.splitlines():
        match = _HEADING.match(line)
        if match:
            close()
            level = len(match.group(1))
            text = match.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, text))
            current_headings = tuple(heading for _, heading in stack)
            continue
        current.append(line)

    close()
    return sections


def _blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    in_fence = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(_FENCE):
            in_fence = not in_fence
        if not in_fence and not stripped:
            if current:
                blocks.append("\n".join(current).strip("\n"))
                current = []
            continue
        current.append(line)

    if current:
        blocks.append("\n".join(current).strip("\n"))
    return [block for block in blocks if block.strip()]


def _split_large_block(block: str, max_tokens: int) -> list[str]:
    lines = block.splitlines()
    if len(lines) == 1:
        return _split_words(lines[0], max_tokens)

    pieces: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in lines:
        was_in_fence = in_fence
        if line.strip().startswith(_FENCE):
            in_fence = not in_fence
        candidate = "\n".join([*current, line])
        if (
            current
            and not was_in_fence
            and not in_fence
            and estimate_tokens(candidate) > max_tokens
        ):
            pieces.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        pieces.append("\n".join(current))
    return pieces


def _split_words(text: str, max_tokens: int) -> list[str]:
    pieces: list[str] = []
    current: list[str] = []
    current_chars = 0
    for word in text.split():
        if current and (current_chars + len(word) + 1) // CHARS_PER_TOKEN > max_tokens:
            pieces.append(" ".join(current))
            current = []
            current_chars = 0
        current.append(word)
        current_chars += len(word) + 1

    if current:
        pieces.append(" ".join(current))
    return pieces


def _overlap_units(units: list[str], overlap_tokens: int) -> list[str]:
    tail: list[str] = []
    tokens = 0
    for unit in reversed(units):
        unit_tokens = estimate_tokens(unit)
        if tail and tokens + unit_tokens > overlap_tokens:
            break
        tail.insert(0, unit)
        tokens += unit_tokens
        if tokens >= overlap_tokens:
            break
    return tail


def _chunk_text(body: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    units: list[str] = []
    for block in _blocks(body):
        if estimate_tokens(block) <= max_tokens:
            units.append(block)
        else:
            units.extend(_split_large_block(block, max_tokens))

    chunks: list[str] = []
    current: list[str] = []
    for unit in units:
        candidate = "\n\n".join([*current, unit])
        if current and estimate_tokens(candidate) > max_tokens:
            chunks.append("\n\n".join(current))
            tail = _overlap_units(current, overlap_tokens)
            if estimate_tokens("\n\n".join([*tail, unit])) > max_tokens:
                tail = []
            current = tail
        current.append(unit)

    if current:
        chunks.append("\n\n".join(current))
    return [chunk for chunk in chunks if chunk.strip()]
