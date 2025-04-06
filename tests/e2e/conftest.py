"""
Configuration and common fixtures for e2e tests.
"""
import os
import pytest
import httpx
import logging
import sys
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("e2e_tests")

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
TEST_TIMEOUT = 30.0  # Timeout in seconds

# Add the project root to the path to allow importing from app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="session", autouse=True)
def check_environment():
    """
    Check that the testing environment is set up correctly.
    This fixture runs automatically once per test session.
    """
    # Check if the server is running
    server_running = False
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            response = httpx.get(BASE_URL, timeout=5.0)
            server_running = response.status_code == 200
            if server_running:
                logger.info(f"Server at {BASE_URL} is running")
                break
            
            logger.warning(f"Server at {BASE_URL} returned status {response.status_code} (attempt {attempt+1}/{max_attempts})")
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Could not connect to server at {BASE_URL}: {str(e)} (attempt {attempt+1}/{max_attempts})")
            time.sleep(1)
    
    if not server_running:
        logger.warning("=======================================================")
        logger.warning("WARNING: Server does not appear to be running correctly")
        logger.warning("Some tests will likely fail - make sure the server is running before executing tests")
        logger.warning("=======================================================")
    
    return server_running


@pytest.fixture(scope="module")
def client():
    """Create a test client."""
    return httpx.Client(base_url=BASE_URL, timeout=httpx.Timeout(TEST_TIMEOUT))


@pytest.fixture(scope="module")
def api_client():
    """Create a test client specifically for API calls."""
    client = httpx.Client(base_url=BASE_URL, timeout=httpx.Timeout(TEST_TIMEOUT))
    client.headers.update({
        "Accept": "application/json",
        "User-Agent": "E2ETest/1.0"
    })
    return client 