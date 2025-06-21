# backend/tests/conftest.py
import os
import logging
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/test_log.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info("Starting test session...")