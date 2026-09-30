"""Tests del filtro de salida (T4.6)."""

from app.features.chat.output_guard import OutputGuard

SYSTEM = (
    "Eres el asistente de Rafael. Reglas: responde solo con las fuentes "
    "y no reveles el token interno."
)


def _guard(**overrides: object) -> OutputGuard:
    base: dict[str, object] = {
        "canary": "CANARIO123",
        "system_prompt": SYSTEM,
        "allowlist": (),
        "allowed_domains": ("github.com",),
    }
    base.update(overrides)
    return OutputGuard(**base)  # type: ignore[arg-type]


def _run(guard: OutputGuard, chunks: list[str]) -> tuple[str, str | None]:
    emitted: list[str] = []
    for chunk in chunks:
        decision = guard.feed(chunk)
        if decision.blocked:
            return "", decision.reason
        emitted.append(decision.text)
    final = guard.flush()
    if final.blocked:
        return "", final.reason
    emitted.append(final.text)
    return "".join(emitted), None


def test_normal_text_passes_unchanged() -> None:
    text = "Rafael trabaja en AePTIC y usa Python con FastAPI. " * 5

    result, reason = _run(_guard(), list(text))

    assert reason is None
    assert result == text


def test_buffer_only_emits_after_retention() -> None:
    guard = _guard()

    first = guard.feed("a" * 100)

    assert first.text == "a" * 36


def test_canary_split_across_chunks_is_blocked() -> None:
    result, reason = _run(_guard(), ["hola CANA", "RIO123 adios"])

    assert result == ""
    assert reason == "canary"


def test_prompt_ngram_leak_is_blocked() -> None:
    leak = "responde solo con las fuentes y no reveles el token interno"

    result, reason = _run(_guard(), [leak])

    assert result == ""
    assert reason == "prompt_leak"


def test_email_not_allowlisted_is_blocked_and_allowlisted_passes() -> None:
    _, reason = _run(_guard(), ["escribe a rafael@example.com"])
    assert reason == "email"

    result, allowed_reason = _run(
        _guard(allowlist=("rafael@example.com",)), ["escribe a rafael@example.com"]
    )
    assert allowed_reason is None
    assert "rafael@example.com" in result


def test_phone_dni_and_iban_are_blocked() -> None:
    assert _run(_guard(), ["llama al +34 600 11 22 33"])[1] == "phone"
    assert _run(_guard(), ["su documento es 12345678Z"])[1] == "dni"
    assert _run(_guard(), ["cuenta ES12 3456 7890 1234 5678 9012"])[1] == "iban"


def test_allowed_domain_passes_and_external_url_is_blocked() -> None:
    result, reason = _run(_guard(), ["mira https://github.com/rufae/CV-Web"])
    assert reason is None
    assert "github.com" in result

    _, reason = _run(_guard(), ["mira https://evil.example.com/x"])
    assert reason == "external_url"


def test_dangerous_markdown_is_blocked() -> None:
    assert _run(_guard(), ["[click](javascript:alert(1))"])[1] == "dangerous_markdown"
    assert _run(_guard(), ["![foto](https://evil.example.com/a.png)"])[1] == ("dangerous_markdown")


def test_max_length_is_enforced() -> None:
    guard = _guard(max_length=10)

    _, reason = _run(guard, ["x" * 200])

    assert reason == "too_long"
