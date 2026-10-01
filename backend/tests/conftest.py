"""Configuración hermética de la suite.

Los tests no deben tocar nodos reales (torre/Dell), la bóveda ni el `.env`
local: se neutraliza cualquier valor externo antes de crear la app.
"""

import os

_NEUTRAL_ENV = {
    # APP_ENV se deja en su valor por defecto (development): el modo "test"
    # activa el FakeProvider y el TestRetriever, que algunos tests no esperan.
    "LLM_TOWER_URL": "",
    "LLM_TOWER_MODEL": "",
    "LLM_DELL_URL": "",
    "LLM_DELL_MODEL": "",
    "EMBED_URL": "",
    "EMBED_MODEL": "bge-m3",
    "VAULT_PATH": "",
    "CHROMA_PATH": "",
    "DATA_PATH": "",
    "GEMINI_ENABLED": "false",
    "GOOGLE_API_KEY": "",
    "EMAIL": "",
    "PASSWORD_APPLICATION": "",
    "METRICS_TOKEN": "",
    "ALLOWED_HOSTS": "*",
    "RATE_LIMIT_CHAT": "10/minute;60/hour",
    "RATE_LIMIT_CONTACT": "3/hour",
    "RATE_LIMIT_FEEDBACK": "20/hour",
    "DAILY_CHAT_BUDGET": "500",
}

for _key, _value in _NEUTRAL_ENV.items():
    os.environ[_key] = _value
