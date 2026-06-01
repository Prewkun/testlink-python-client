"""
Unit tests for protocol.py — RequestBuilder and ResponseParser.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from protocol import RequestBuilder, ResponseParser, ResponseStatus
from exceptions import ProtocolException


class TestRequestBuilder:

    def test_request_builder_initializes_empty(self):
        builder = RequestBuilder()
        assert builder.parameters == {}
        assert builder.request_type is None

    def test_set_request_type_returns_self(self):
        builder = RequestBuilder()
        result = builder.set_request_type("PfsVerifyUserInput")
        assert result is builder

    def test_set_request_type_stores_value(self):
        builder = RequestBuilder()
        builder.set_request_type("PfsVerifyUserInput")
        assert builder.request_type == "PfsVerifyUserInput"

    def test_set_parameter_returns_self(self):
        builder = RequestBuilder()
        result = builder.set_parameter("DATABASE", "TESTDB")
        assert result is builder

    def test_set_parameter_stores_value(self):
        builder = RequestBuilder()
        builder.set_parameter("DATABASE", "TESTDB")
        assert builder.parameters["DATABASE"] == "TESTDB"

    def test_set_parameter_ignores_none(self):
        builder = RequestBuilder()
        builder.set_parameter("KEY", None)
        assert "KEY" not in builder.parameters

    def test_set_parameter_newline_escaping(self):
        builder = RequestBuilder()
        builder.set_parameter("COMMENT", "line1\nline2")
        assert builder.parameters["COMMENT"] == "line1&nl;line2"

    def test_set_parameter_carriage_return_removed(self):
        builder = RequestBuilder()
        builder.set_parameter("COMMENT", "line1\r\nline2")
        assert "\r" not in builder.parameters["COMMENT"]

    def test_set_parameters_adds_multiple(self):
        builder = RequestBuilder()
        builder.set_parameters({"A": "1", "B": "2"})
        assert builder.parameters["A"] == "1"
        assert builder.parameters["B"] == "2"

    def test_build_raises_without_request_type(self):
        builder = RequestBuilder()
        builder.set_parameter("DATABASE", "TESTDB")
        with pytest.raises(ProtocolException):
            builder.build()

    def test_build_contains_request_type(self):
        builder = RequestBuilder()
        builder.set_request_type("PfsVerifyUserInput")
        result = builder.build()
        assert "REQUEST_TYPE=PfsVerifyUserInput" in result

    def test_request_builder_crlf_line_endings(self):
        builder = RequestBuilder()
        builder.set_request_type("PfsVerifyUserInput")
        result = builder.build()
        assert "\r\n" in result

    def test_build_ends_with_blank_line(self):
        builder = RequestBuilder()
        builder.set_request_type("PfsVerifyUserInput")
        result = builder.build()
        assert result.endswith("\r\n\r\n")

    def test_build_request_type_is_first_line(self):
        builder = RequestBuilder()
        builder.set_request_type("PfsVerifyUserInput")
        builder.set_parameter("DATABASE", "TESTDB")
        result = builder.build()
        first_line = result.split("\r\n")[0]
        assert first_line == "REQUEST_TYPE=PfsVerifyUserInput"

    def test_build_includes_parameters(self):
        builder = RequestBuilder()
        builder.set_request_type("PfsVerifyUserInput")
        builder.set_parameter("DATABASE", "TESTDB")
        result = builder.build()
        assert "DATABASE=TESTDB" in result

    def test_clear_resets_state(self):
        builder = RequestBuilder()
        builder.set_request_type("PfsVerifyUserInput")
        builder.set_parameter("DATABASE", "TESTDB")
        builder.clear()
        assert builder.request_type is None
        assert builder.parameters == {}

    def test_chaining_works(self):
        result = (RequestBuilder()
                  .set_request_type("PfsVerifyUserInput")
                  .set_parameter("DATABASE", "TESTDB")
                  .build())
        assert "REQUEST_TYPE=PfsVerifyUserInput" in result


class TestResponseParser:

    def test_response_parser_initializes(self):
        parser = ResponseParser()
        assert parser.status == ResponseStatus.UNKNOWN

    def test_parse_ok_response(self, sample_ok_response):
        parser = ResponseParser()
        status, message, data_lines = parser.parse(sample_ok_response)
        assert status == ResponseStatus.OK

    def test_parse_ok_response_message(self, sample_ok_response):
        parser = ResponseParser()
        status, message, data_lines = parser.parse(sample_ok_response)
        assert message == "OK"

    def test_parse_ok_response_data_lines(self, sample_ok_response):
        parser = ResponseParser()
        status, message, data_lines = parser.parse(sample_ok_response)
        assert "data_line_1" in data_lines
        assert "data_line_2" in data_lines

    def test_parse_failure_response(self, sample_failure_response):
        parser = ResponseParser()
        status, message, data_lines = parser.parse(sample_failure_response)
        assert status == ResponseStatus.FAILURE

    def test_parse_failure_response_message(self, sample_failure_response):
        parser = ResponseParser()
        status, message, data_lines = parser.parse(sample_failure_response)
        assert "Failure:" in message

    def test_parse_warning_response(self, sample_warning_response):
        parser = ResponseParser()
        status, message, data_lines = parser.parse(sample_warning_response)
        assert status == ResponseStatus.WARNING

    def test_parse_warning_response_message(self, sample_warning_response):
        parser = ResponseParser()
        status, message, data_lines = parser.parse(sample_warning_response)
        assert "Warning:" in message

    def test_parse_error_response(self, sample_error_response):
        parser = ResponseParser()
        status, message, data_lines = parser.parse(sample_error_response)
        assert status == ResponseStatus.ERROR

    def test_parse_error_response_message(self, sample_error_response):
        parser = ResponseParser()
        status, message, data_lines = parser.parse(sample_error_response)
        assert "Error:" in message

    def test_parse_empty_response(self):
        parser = ResponseParser()
        status, message, data_lines = parser.parse("")
        assert status == ResponseStatus.ERROR

    def test_parse_whitespace_response(self):
        parser = ResponseParser()
        status, message, data_lines = parser.parse("   \n  ")
        assert status == ResponseStatus.ERROR

    def test_parse_empty_data_lines(self):
        parser = ResponseParser()
        status, message, data_lines = parser.parse("")
        assert data_lines == []

    def test_parse_unknown_response(self):
        parser = ResponseParser()
        status, message, data_lines = parser.parse("SOMETHING_RANDOM")
        assert status == ResponseStatus.UNKNOWN

    def test_parse_delimited_data(self, sample_delimited_response):
        parser = ResponseParser()
        parser.parse(sample_delimited_response)
        rows = parser.parse_delimited_data(delimiter=';')
        assert len(rows) == 2
        assert rows[0][0] == "CODE1"
        assert rows[0][1] == "Description1"

    def test_parse_delimited_data_custom_delimiter(self):
        parser = ResponseParser()
        parser.parse("OK\nA|B|C\n")
        rows = parser.parse_delimited_data(delimiter='|')
        assert rows[0] == ["A", "B", "C"]

    def test_get_status_name_ok(self, sample_ok_response):
        parser = ResponseParser()
        parser.parse(sample_ok_response)
        assert parser.get_status_name() == "OK"

    def test_get_status_name_failure(self, sample_failure_response):
        parser = ResponseParser()
        parser.parse(sample_failure_response)
        assert parser.get_status_name() == "Failure"

    def test_response_status_enum_values(self):
        assert ResponseStatus.OK.value == "OK"
        assert ResponseStatus.WARNING.value == "Warning"
        assert ResponseStatus.FAILURE.value == "Failure"
        assert ResponseStatus.ERROR.value == "Error"
        assert ResponseStatus.UNKNOWN.value == "Unknown"
