import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import threading
import time
import uvicorn
import socket

sys.path.append(str(Path(__file__).parent.parent.parent))


def get_free_port():
    """Get a free port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture(scope="session")
def test_server():
    """Start the FastAPI server in a background thread for the entire test session."""
    from backend.main import app

    port = get_free_port()

    config = uvicorn.Config(app=app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()

    # Wait for server to start
    max_attempts = 20
    for _ in range(max_attempts):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                break
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.1)
    else:
        raise RuntimeError(f"Server failed to start on port {port}")

    yield f"http://127.0.0.1:{port}"

    # Server will be killed when the test process ends


@pytest.fixture(scope="session")
def base_url(test_server):
    """Provide the base URL for the test server."""
    return test_server


@pytest.fixture
def client():
    """Create a test client."""
    from backend.main import app

    return TestClient(app)
