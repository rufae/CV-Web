"""Aislamiento FS del vault para CVWEB (2026-10-01).

CVWEB solo debe poder leer la carpeta pública del baúl: ni el resto del
vault, ni symlinks que escapen, ni notas sin el flag `cv_public: true`.
"""

from pathlib import Path

from app.rag.ingest import extract_public_notes


def _escribir(path: Path, texto: str, cv_public: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flag = "true" if cv_public else "false"
    path.write_text(
        f"---\ntitle: {path.stem}\ncv_public: {flag}\n---\n\n{texto}\n",
        encoding="utf-8",
    )


def test_solo_publica_con_flag_y_nada_de_fuera(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    _escribir(vault / "Public" / "portfolio" / "facts.md", "PUBLICO_OK")
    _escribir(vault / "Public" / "borrador.md", "PUBLICO_SIN_FLAG", cv_public=False)
    _escribir(vault / "Privado" / "diario.md", "PRIVADO_NO", cv_public=True)

    result = extract_public_notes(vault)

    assert {nota.relative_path for nota in result.notes} == {"Public/portfolio/facts.md"}
    texto = "\n".join(nota.content for nota in result.notes)
    assert "PUBLICO_OK" in texto
    assert "PUBLICO_SIN_FLAG" not in texto
    assert "PRIVADO_NO" not in texto


def test_ignora_symlinks_que_escapan_del_vault(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    _escribir(vault / "Public" / "ok.md", "PUBLICO_OK")
    secreto = tmp_path / "secreto.md"
    _escribir(secreto, "SECRETO_FUERA")
    (vault / "Public" / "enlace.md").symlink_to(secreto)

    result = extract_public_notes(vault)

    assert {nota.relative_path for nota in result.notes} == {"Public/ok.md"}
    assert "SECRETO_FUERA" not in "\n".join(nota.content for nota in result.notes)
