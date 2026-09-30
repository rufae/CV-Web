"""Tests de la construcción de proveedores LLM (T2.5)."""

import subprocess
import sys
from pathlib import Path

from app.core.config import Settings
from app.llm.factory import build_providers

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _settings(
    *,
    llm_tower_url: str = "",
    llm_tower_model: str = "",
    llm_dell_url: str = "",
    llm_dell_model: str = "",
    llm_providers_order: str = "tower,dell",
    gemini_enabled: bool = False,
    google_api_key: str = "",
) -> Settings:
    return Settings(
        _env_file=None,  # type: ignore[call-arg]  # pydantic-settings lo soporta en runtime
        llm_tower_url=llm_tower_url,
        llm_tower_model=llm_tower_model,
        llm_dell_url=llm_dell_url,
        llm_dell_model=llm_dell_model,
        llm_providers_order=llm_providers_order,
        gemini_enabled=gemini_enabled,
        google_api_key=google_api_key,
    )


def test_no_config_returns_empty_list() -> None:
    assert build_providers(_settings()) == []


def test_builds_ollama_providers_in_configured_order() -> None:
    settings = _settings(
        llm_tower_url="http://tower:11434",
        llm_tower_model="big",
        llm_dell_url="http://dell:11434",
        llm_dell_model="small",
        llm_providers_order="dell,tower",
    )

    providers = build_providers(settings)

    assert [provider.name for provider in providers] == ["dell", "tower"]


def test_gemini_disabled_is_excluded() -> None:
    settings = _settings(gemini_enabled=False, google_api_key="k")

    assert build_providers(settings) == []


def test_gemini_enabled_without_key_is_excluded() -> None:
    settings = _settings(gemini_enabled=True, google_api_key="")

    assert build_providers(settings) == []


def test_gemini_enabled_with_key_is_included_and_ordered() -> None:
    settings = _settings(
        gemini_enabled=True,
        google_api_key="k",
        llm_tower_url="http://tower:11434",
        llm_tower_model="big",
        llm_providers_order="tower,gemini",
    )

    providers = build_providers(settings)

    assert [provider.name for provider in providers] == ["tower", "gemini"]


def test_disabled_gemini_does_not_import_google_genai() -> None:
    code = (
        "import sys\n"
        "from app.core.config import Settings\n"
        "from app.llm.factory import build_providers\n"
        "providers = build_providers(Settings(_env_file=None))\n"
        "assert providers == []\n"
        "assert 'google.genai' not in sys.modules\n"
        "print('ok')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
