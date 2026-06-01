"""
Unit tests for exceptions.py — Exception hierarchy.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from exceptions import (
    TestLinkException,
    PfsErrorException,
    PfsFailureException,
    PfsWarningException,
    ConnectionException,
    TimeoutException,
    ConfigurationException,
    ValidationException,
    ProtocolException,
)


class TestExceptionInstantiation:

    def test_testlink_exception_with_message_only(self):
        exc = TestLinkException("something went wrong")
        assert exc.message == "something went wrong"

    def test_testlink_exception_with_details(self):
        exc = TestLinkException("error", details="extra info")
        assert exc.details == "extra info"

    def test_testlink_exception_details_none_by_default(self):
        exc = TestLinkException("error")
        assert exc.details is None

    def test_pfs_error_exception_instantiates(self):
        exc = PfsErrorException("pfs error")
        assert exc.message == "pfs error"

    def test_pfs_failure_exception_instantiates(self):
        exc = PfsFailureException("pfs failure")
        assert exc.message == "pfs failure"

    def test_pfs_warning_exception_instantiates(self):
        exc = PfsWarningException("pfs warning")
        assert exc.message == "pfs warning"

    def test_connection_exception_instantiates(self):
        exc = ConnectionException("connection failed")
        assert exc.message == "connection failed"

    def test_timeout_exception_instantiates(self):
        exc = TimeoutException("timed out")
        assert exc.message == "timed out"

    def test_configuration_exception_instantiates(self):
        exc = ConfigurationException("bad config")
        assert exc.message == "bad config"

    def test_validation_exception_instantiates(self):
        exc = ValidationException("invalid param")
        assert exc.message == "invalid param"

    def test_protocol_exception_instantiates(self):
        exc = ProtocolException("bad protocol")
        assert exc.message == "bad protocol"

    def test_all_exceptions_with_details(self):
        for ExcClass in [
            PfsErrorException, PfsFailureException, PfsWarningException,
            ConnectionException, TimeoutException, ConfigurationException,
            ValidationException, ProtocolException,
        ]:
            exc = ExcClass("msg", details="detail info")
            assert exc.details == "detail info"


class TestExceptionHierarchy:

    def test_testlink_exception_inherits_exception(self):
        assert issubclass(TestLinkException, Exception)

    @pytest.mark.parametrize("exc_class", [
        PfsErrorException,
        PfsFailureException,
        PfsWarningException,
        ConnectionException,
        TimeoutException,
        ConfigurationException,
        ValidationException,
        ProtocolException,
    ])
    def test_all_inherit_from_testlink_exception(self, exc_class):
        assert issubclass(exc_class, TestLinkException)

    @pytest.mark.parametrize("exc_class", [
        PfsErrorException,
        PfsFailureException,
        PfsWarningException,
        ConnectionException,
        TimeoutException,
        ConfigurationException,
        ValidationException,
        ProtocolException,
    ])
    def test_all_inherit_from_exception(self, exc_class):
        assert issubclass(exc_class, Exception)

    def test_can_catch_as_testlink_exception(self):
        with pytest.raises(TestLinkException):
            raise PfsErrorException("error")

    def test_can_catch_as_exception(self):
        with pytest.raises(Exception):
            raise ConnectionException("conn error")


class TestExceptionStrOutput:

    def test_str_without_details(self):
        exc = TestLinkException("simple message")
        assert str(exc) == "simple message"

    def test_str_with_details(self):
        exc = TestLinkException("error occurred", details="more info")
        result = str(exc)
        assert "error occurred" in result
        assert "more info" in result

    def test_str_with_details_contains_details_label(self):
        exc = TestLinkException("error", details="info")
        assert "Details:" in str(exc)

    def test_subclass_str_without_details(self):
        exc = PfsErrorException("pfs error msg")
        assert str(exc) == "pfs error msg"

    def test_subclass_str_with_details(self):
        exc = PfsFailureException("fail msg", details="detail here")
        assert "fail msg" in str(exc)
        assert "detail here" in str(exc)
