"""Test de humo mínimo para validar el andamiaje de calidad (T1.2)."""

import app


def test_app_package_is_importable() -> None:
    assert app.__name__ == "app"
