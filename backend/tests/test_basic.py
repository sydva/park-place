"""Basic tests to verify the test setup works."""

import requests


def test_server_is_running(base_url):
    """Test that the server starts and responds."""
    response = requests.get(f"{base_url}/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Park Place API"


def test_openapi_available(base_url):
    """Test that OpenAPI schema is available."""
    response = requests.get(f"{base_url}/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "Park Place API"


def test_docs_available(base_url):
    """Test that API docs are available."""
    response = requests.get(f"{base_url}/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
