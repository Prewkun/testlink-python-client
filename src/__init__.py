"""
TestLink Python Client - Core library.

A comprehensive Python client for TestLink/PFS MES integration
with full support for 40+ PFS procedures.
"""

__version__ = "1.0.0"
__author__ = "Benchmark Electronics MES Integration Team"

from .testlink_client import TestLinkClient
from .protocol import RequestBuilder, ResponseParser, ResponseStatus
from .config import ConfigManager, TestLinkConfig
from .exceptions import (
    TestLinkException,
    PfsErrorException,
    PfsFailureException,
    PfsWarningException,
    ConnectionException,
    TimeoutException,
    ConfigurationException,
    ValidationException,
    ProtocolException
)
from .logger import setup_logger, logger

__all__ = [
    'TestLinkClient',
    'RequestBuilder',
    'ResponseParser',
    'ResponseStatus',
    'ConfigManager',
    'TestLinkConfig',
    'TestLinkException',
    'PfsErrorException',
    'PfsFailureException',
    'PfsWarningException',
    'ConnectionException',
    'TimeoutException',
    'ConfigurationException',
    'ValidationException',
    'ProtocolException',
    'setup_logger',
    'logger',
]
