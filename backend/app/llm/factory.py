"""Construcción de la lista de proveedores LLM según la configuración (T2.5).

Gemini se importa de forma perezosa: con `GEMINI_ENABLED=false` (por defecto),
`google.genai` no se carga en el proceso.
"""

from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.ollama import OllamaProvider


def build_providers(settings: Settings) -> list[LLMProvider]:
    providers: dict[str, LLMProvider] = {}

    if settings.llm_tower_url and settings.llm_tower_model:
        providers["tower"] = OllamaProvider(
            settings.llm_tower_url,
            settings.llm_tower_model,
            name="tower",
            connect_timeout_s=settings.llm_connect_timeout_s,
        )

    if settings.llm_dell_url and settings.llm_dell_model:
        providers["dell"] = OllamaProvider(
            settings.llm_dell_url,
            settings.llm_dell_model,
            name="dell",
            connect_timeout_s=settings.llm_connect_timeout_s,
        )

    if settings.gemini_enabled and settings.google_api_key:
        from app.llm.gemini import GeminiProvider

        providers["gemini"] = GeminiProvider(
            settings.google_api_key,
            model=settings.gemini_model,
        )

    order = [name.strip() for name in settings.llm_providers_order.split(",") if name.strip()]
    ordered = [providers[name] for name in order if name in providers]
    remaining = [provider for name, provider in providers.items() if name not in order]
    return ordered + remaining
