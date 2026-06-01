"""
Configuration management for TestLink client.
Supports loading from JSON/YAML files and environment variables.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator

try:
    from .exceptions import ConfigurationException
except ImportError:
    from exceptions import ConfigurationException


class ServerConfig(BaseModel):
    """Server connection configuration."""
    host: str = Field(..., description="PFS server hostname (DNS alias)")
    port: int = Field(50000, description="PFS server port")
    timeout: int = Field(30, description="Connection timeout in seconds")
    validate_cert: bool = Field(True, description="Validate TLS certificate")
    
    @validator('port')
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        return v


class DatabaseConfig(BaseModel):
    """Database configuration."""
    name: str = Field(..., description="PFS database name (e.g., PFSHJP4)")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Database name cannot be empty")
        return v.upper()


class CredentialsConfig(BaseModel):
    """User credentials configuration."""
    user_id: Optional[str] = Field(None, description="PFS user ID")
    password: Optional[str] = Field(None, description="PFS password")
    
    class Config:
        # Don't allow extra fields for security
        extra = 'forbid'


class TestLinkConfig(BaseModel):
    """Complete TestLink client configuration."""
    server: ServerConfig
    database: DatabaseConfig
    credentials: Optional[CredentialsConfig] = None
    work_center: Optional[str] = Field(None, description="Default work center")
    operation_code: Optional[str] = Field(None, description="Default operation code")
    
    class Config:
        extra = 'forbid'


class ConfigManager:
    """
    Manages loading and validation of configuration.
    Supports JSON files and environment variable overrides.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path
        self.config: Optional[TestLinkConfig] = None
    
    def load_from_file(self, file_path: str) -> TestLinkConfig:
        """
        Load configuration from JSON file.
        
        Args:
            file_path: Path to JSON configuration file
        
        Returns:
            Validated TestLinkConfig instance
        
        Raises:
            ConfigurationException: If file not found or invalid
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ConfigurationException(f"Configuration file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Apply environment variable overrides
            data = self._apply_env_overrides(data)
            
            self.config = TestLinkConfig(**data)
            return self.config
        
        except json.JSONDecodeError as e:
            raise ConfigurationException(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigurationException(f"Failed to load configuration: {e}")
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> TestLinkConfig:
        """
        Load configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
        
        Returns:
            Validated TestLinkConfig instance
        """
        try:
            # Apply environment variable overrides
            config_dict = self._apply_env_overrides(config_dict)
            
            self.config = TestLinkConfig(**config_dict)
            return self.config
        except Exception as e:
            raise ConfigurationException(f"Failed to load configuration: {e}")
    
    def load_site_config(self, site_name: str, config_dir: str = "config/sites") -> TestLinkConfig:
        """
        Load pre-configured site configuration.
        
        Args:
            site_name: Site name (e.g., 'huntsville', 'austin')
            config_dir: Directory containing site configurations
        
        Returns:
            Validated TestLinkConfig instance
        """
        file_path = Path(config_dir) / f"{site_name.lower()}.json"
        return self.load_from_file(str(file_path))
    
    def _apply_env_overrides(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration.
        
        Environment variables:
        - TESTLINK_HOST: Server host
        - TESTLINK_PORT: Server port
        - TESTLINK_DATABASE: Database name
        - TESTLINK_USER_ID: User ID
        - TESTLINK_PASSWORD: Password
        - TESTLINK_TIMEOUT: Connection timeout
        
        Args:
            config_dict: Configuration dictionary
        
        Returns:
            Configuration dictionary with overrides applied
        """
        # Server overrides
        if 'server' in config_dict:
            if os.getenv('TESTLINK_HOST'):
                config_dict['server']['host'] = os.getenv('TESTLINK_HOST')
            if os.getenv('TESTLINK_PORT'):
                config_dict['server']['port'] = int(os.getenv('TESTLINK_PORT'))
            if os.getenv('TESTLINK_TIMEOUT'):
                config_dict['server']['timeout'] = int(os.getenv('TESTLINK_TIMEOUT'))
        
        # Database overrides
        if 'database' in config_dict:
            if os.getenv('TESTLINK_DATABASE'):
                config_dict['database']['name'] = os.getenv('TESTLINK_DATABASE')
        
        # Credentials overrides
        if os.getenv('TESTLINK_USER_ID') or os.getenv('TESTLINK_PASSWORD'):
            if 'credentials' not in config_dict:
                config_dict['credentials'] = {}
            if os.getenv('TESTLINK_USER_ID'):
                config_dict['credentials']['user_id'] = os.getenv('TESTLINK_USER_ID')
            if os.getenv('TESTLINK_PASSWORD'):
                config_dict['credentials']['password'] = os.getenv('TESTLINK_PASSWORD')
        
        return config_dict
    
    def save_to_file(self, file_path: str):
        """
        Save current configuration to file (excludes credentials for security).
        
        Args:
            file_path: Path to save configuration
        """
        if not self.config:
            raise ConfigurationException("No configuration loaded")
        
        # Create safe config dict (no passwords)
        safe_dict = self.config.dict(exclude={'credentials'})
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(safe_dict, f, indent=2)
    
    def get_config(self) -> TestLinkConfig:
        """
        Get the current configuration.
        
        Returns:
            Current TestLinkConfig instance
        
        Raises:
            ConfigurationException: If no configuration loaded
        """
        if not self.config:
            raise ConfigurationException("No configuration loaded. Call load_from_file() or load_from_dict() first.")
        return self.config
