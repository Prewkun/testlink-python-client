"""
Shared pytest fixtures for TestLink client unit tests.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))


@pytest.fixture
def sample_ok_response():
    return "OK\ndata_line_1\ndata_line_2\n"


@pytest.fixture
def sample_failure_response():
    return "PfsVerifyUserInput Failure: Invalid credentials\n"


@pytest.fixture
def sample_warning_response():
    return "PfsQuery Warning: Override required\n"


@pytest.fixture
def sample_error_response():
    return "PfsVerifyUserInput Error: Server error\n"


@pytest.fixture
def sample_delimited_response():
    return "OK\nCODE1;Description1\nCODE2;Description2\n"


@pytest.fixture
def mock_socket():
    sock = MagicMock()
    sock_file = MagicMock()
    sock.makefile.return_value = sock_file
    return sock


@pytest.fixture
def basic_config_dict():
    return {
        "server": {
            "host": "pfs-server.example.com",
            "port": 50000,
            "timeout": 30,
            "validate_cert": True,
        },
        "database": {
            "name": "TESTDB"
        },
        "credentials": {
            "user_id": "testuser",
            "password": "testpass",
        },
    }
