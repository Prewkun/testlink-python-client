"""
Unit tests for config.py — Configuration management.
"""

import sys
import os
import json
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from config import ServerConfig, DatabaseConfig, CredentialsConfig, TestLinkConfig, ConfigManager
from exceptions import ConfigurationException


class TestServerConfig:

    def test_server_config_valid(self):
        cfg = ServerConfig(host="pfs.example.com", port=50000, timeout=30)
        assert cfg.host == "pfs.example.com"
        assert cfg.port == 50000
        assert cfg.timeout == 30

    def test_server_config_default_port(self):
        cfg = ServerConfig(host="pfs.example.com")
        assert cfg.port == 50000

    def test_server_config_default_timeout(self):
        cfg = ServerConfig(host="pfs.example.com")
        assert cfg.timeout == 30

    def test_server_config_default_validate_cert(self):
        cfg = ServerConfig(host="pfs.example.com")
        assert cfg.validate_cert is True

    def test_server_config_invalid_port_zero(self):
        with pytest.raises(Exception):
            ServerConfig(host="pfs.example.com", port=0)

    def test_server_config_invalid_port_too_high(self):
        with pytest.raises(Exception):
            ServerConfig(host="pfs.example.com", port=65536)

    def test_server_config_valid_port_min(self):
        cfg = ServerConfig(host="pfs.example.com", port=1)
        assert cfg.port == 1

    def test_server_config_valid_port_max(self):
        cfg = ServerConfig(host="pfs.example.com", port=65535)
        assert cfg.port == 65535

    def test_server_config_invalid_timeout_zero(self):
        with pytest.raises(Exception):
            ServerConfig(host="pfs.example.com", timeout=0)

    def test_server_config_invalid_timeout_negative(self):
        with pytest.raises(Exception):
            ServerConfig(host="pfs.example.com", timeout=-1)

    def test_server_config_valid_timeout(self):
        cfg = ServerConfig(host="pfs.example.com", timeout=60)
        assert cfg.timeout == 60


class TestDatabaseConfig:

    def test_database_name_normalized_to_uppercase(self):
        cfg = DatabaseConfig(name="testdb")
        assert cfg.name == "TESTDB"

    def test_database_name_already_uppercase(self):
        cfg = DatabaseConfig(name="TESTDB")
        assert cfg.name == "TESTDB"

    def test_database_name_mixed_case(self):
        cfg = DatabaseConfig(name="TestDb")
        assert cfg.name == "TESTDB"

    def test_database_name_empty_raises(self):
        with pytest.raises(Exception):
            DatabaseConfig(name="")

    def test_database_name_whitespace_raises(self):
        with pytest.raises(Exception):
            DatabaseConfig(name="   ")


class TestTestLinkConfig:

    def test_load_from_dict_valid(self, basic_config_dict):
        manager = ConfigManager()
        cfg = manager.load_from_dict(basic_config_dict)
        assert cfg.server.host == "pfs-server.example.com"

    def test_load_from_dict_database_uppercase(self):
        manager = ConfigManager()
        cfg = manager.load_from_dict({
            "server": {"host": "localhost"},
            "database": {"name": "mydb"},
        })
        assert cfg.database.name == "MYDB"

    def test_load_from_dict_with_credentials(self, basic_config_dict):
        manager = ConfigManager()
        cfg = manager.load_from_dict(basic_config_dict)
        assert cfg.credentials.user_id == "testuser"
        assert cfg.credentials.password == "testpass"

    def test_load_from_dict_without_credentials(self):
        manager = ConfigManager()
        cfg = manager.load_from_dict({
            "server": {"host": "localhost"},
            "database": {"name": "TESTDB"},
        })
        assert cfg.credentials is None

    def test_load_from_dict_port_validation(self):
        manager = ConfigManager()
        with pytest.raises(ConfigurationException):
            manager.load_from_dict({
                "server": {"host": "localhost", "port": 0},
                "database": {"name": "TESTDB"},
            })

    def test_testlink_config_work_center(self):
        manager = ConfigManager()
        cfg = manager.load_from_dict({
            "server": {"host": "localhost"},
            "database": {"name": "TESTDB"},
            "work_center": "WC01",
        })
        assert cfg.work_center == "WC01"

    def test_testlink_config_operation_code(self):
        manager = ConfigManager()
        cfg = manager.load_from_dict({
            "server": {"host": "localhost"},
            "database": {"name": "TESTDB"},
            "operation_code": "INSPECT",
        })
        assert cfg.operation_code == "INSPECT"


class TestConfigManager:

    def test_load_from_file_missing_raises(self):
        manager = ConfigManager()
        with pytest.raises(ConfigurationException):
            manager.load_from_file("nonexistent_config_file.json")

    def test_load_from_file_valid(self, tmp_path, basic_config_dict):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(basic_config_dict))
        manager = ConfigManager()
        cfg = manager.load_from_file(str(config_file))
        assert cfg.server.host == "pfs-server.example.com"

    def test_load_from_file_invalid_json(self, tmp_path):
        config_file = tmp_path / "bad.json"
        config_file.write_text("not valid json {{{")
        manager = ConfigManager()
        with pytest.raises(ConfigurationException):
            manager.load_from_file(str(config_file))

    def test_get_config_raises_when_not_loaded(self):
        manager = ConfigManager()
        with pytest.raises(ConfigurationException):
            manager.get_config()

    def test_get_config_returns_after_load(self, basic_config_dict):
        manager = ConfigManager()
        manager.load_from_dict(basic_config_dict)
        cfg = manager.get_config()
        assert cfg is not None

    def test_apply_env_overrides_host(self, basic_config_dict):
        manager = ConfigManager()
        with patch.dict(os.environ, {"TESTLINK_HOST": "override-host.example.com"}):
            cfg = manager.load_from_dict(basic_config_dict)
        assert cfg.server.host == "override-host.example.com"

    def test_apply_env_overrides_port(self, basic_config_dict):
        manager = ConfigManager()
        with patch.dict(os.environ, {"TESTLINK_PORT": "12345"}):
            cfg = manager.load_from_dict(basic_config_dict)
        assert cfg.server.port == 12345

    def test_apply_env_overrides_database(self, basic_config_dict):
        manager = ConfigManager()
        with patch.dict(os.environ, {"TESTLINK_DATABASE": "ENVDB"}):
            cfg = manager.load_from_dict(basic_config_dict)
        assert cfg.database.name == "ENVDB"

    def test_apply_env_overrides_timeout(self, basic_config_dict):
        manager = ConfigManager()
        with patch.dict(os.environ, {"TESTLINK_TIMEOUT": "60"}):
            cfg = manager.load_from_dict(basic_config_dict)
        assert cfg.server.timeout == 60

    def test_apply_env_overrides_user_id(self, basic_config_dict):
        manager = ConfigManager()
        with patch.dict(os.environ, {"TESTLINK_USER_ID": "envuser"}):
            cfg = manager.load_from_dict(basic_config_dict)
        assert cfg.credentials.user_id == "envuser"

    def test_apply_env_overrides_password(self, basic_config_dict):
        manager = ConfigManager()
        with patch.dict(os.environ, {"TESTLINK_PASSWORD": "envpass"}):
            cfg = manager.load_from_dict(basic_config_dict)
        assert cfg.credentials.password == "envpass"
