"""Taxonomía de errores del subsistema LLM (T2.1)."""


class LLMError(Exception):
    """Error base del subsistema LLM."""


class ProviderUnavailable(LLMError):
    """El proveedor no es accesible (conexión rechazada, DNS, timeout de conexión)."""


class FirstTokenTimeout(LLMError):
    """El proveedor no emitió el primer token dentro del tiempo máximo."""


class ProviderError(LLMError):
    """Error genérico devuelto por el proveedor (HTTP 5xx, JSON corrupto, etc.)."""
