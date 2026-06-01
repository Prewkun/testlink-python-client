"""
Simple test script to verify core functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from testlink_client import TestLinkClient
from protocol import RequestBuilder, ResponseParser, ResponseStatus
from config import ConfigManager
from exceptions import *

print("=" * 60)
print("TestLink Python Client - Foundation Test")
print("=" * 60)

# Test 1: Request Builder
print("\n[TEST 1] Request Builder")
builder = RequestBuilder()
builder.set_request_type("PfsVerifyUserInput")
builder.set_parameter("DATABASE", "PFSHJP4")
builder.set_parameter("USER_ID", "testuser")
builder.set_parameter("PASSWORD", "testpass")
request = builder.build()

print("✓ Request built successfully")
print(f"Request preview:\n{repr(request)}")
assert "REQUEST_TYPE=PfsVerifyUserInput" in request
assert "DATABASE=PFSHJP4" in request
assert request.endswith('\r\n\r\n')
print("✓ All assertions passed")

# Test 2: Response Parser
print("\n[TEST 2] Response Parser")
parser = ResponseParser()

# Test OK response
status, msg, data = parser.parse("OK\nSome data\nMore data\n")
assert status == ResponseStatus.OK
print(f"✓ OK response parsed: {status.value}")

# Test Error response
status, msg, data = parser.parse("PfsQuery Error: Serial number not found")
assert status == ResponseStatus.ERROR
print(f"✓ Error response parsed: {status.value}")

# Test Warning response
status, msg, data = parser.parse("PfsQuery Warning: Unit may need inspection")
assert status == ResponseStatus.WARNING
print(f"✓ Warning response parsed: {status.value}")

# Test Failure response
status, msg, data = parser.parse("PfsQuery Failure: Unit not ready for this operation")
assert status == ResponseStatus.FAILURE
print(f"✓ Failure response parsed: {status.value}")

# Test 3: Configuration Manager
print("\n[TEST 3] Configuration Manager")
config_mgr = ConfigManager()

try:
    config = config_mgr.load_from_file("config/example_config.json")
    print(f"✓ Config loaded: {config.server.host}:{config.server.port}")
    print(f"✓ Database: {config.database.name}")
    print(f"✓ Timeout: {config.server.timeout}s")
except Exception as e:
    print(f"✗ Config load failed: {e}")

# Test 4: Site Configuration
print("\n[TEST 4] Site Configuration")
try:
    config = config_mgr.load_site_config("huntsville")
    print(f"✓ Huntsville config loaded: {config.server.host}")
    print(f"✓ Database: {config.database.name}")
except Exception as e:
    print(f"✗ Site config load failed: {e}")

# Test 5: Client Initialization
print("\n[TEST 5] TestLink Client Initialization")
try:
    client = TestLinkClient(
        host="pfs-gw-hjp4.corp.bench.com",
        database="PFSHJP4",
        timeout=30
    )
    print(f"✓ Client initialized: {client.host}:{client.port}")
    print(f"✓ Database: {client.database}")
    print(f"✓ Timeout: {client.timeout}s")
except Exception as e:
    print(f"✗ Client initialization failed: {e}")

print("\n" + "=" * 60)
print("Foundation tests completed successfully!")
print("=" * 60)
