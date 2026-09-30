"""Tests de CORS, hosts y cabeceras de seguridad (T4.8)."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_security_headers_and_request_id_on_api() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "geolocation=()" in response.headers["permissions-policy"]
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"
    assert len(response.headers["x-request-id"]) == 16


def test_cors_allows_configured_origin_only() -> None:
    with TestClient(create_app()) as client:
        allowed = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
        denied = client.get("/api/health", headers={"Origin": "http://evil.example"})

    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-origin" not in denied.headers


def test_cors_preflight_for_chat() -> None:
    with TestClient(create_app()) as client:
        response = client.options(
            "/api/chat",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

    assert response.status_code in {200, 204}
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_not_found_returns_generic_json() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/ruta-que-no-existe")

    assert response.status_code == 404
    assert response.json() == {"code": "not_found"}


def test_unhandled_exception_returns_generic_500_without_trace() -> None:
    app = create_app()

    with TestClient(app, raise_server_exceptions=False) as client:
        del app.state.health_monitor
        response = client.get("/api/status")

    assert response.status_code == 500
    assert response.json() == {"code": "internal"}
    assert "Traceback" not in response.text
