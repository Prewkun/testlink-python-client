"""
Unit tests for procedures/templates.py — helper functions.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from procedures.templates import (
    build_request,
    parse_response,
    validate_parameters,
    parse_delimited_response,
    build_delimited_list,
    validate_serial_numbers,
    escape_newlines,
    unescape_newlines,
    extract_delimiter,
    format_list_response,
)


class TestBuildRequest:

    def test_build_request_contains_request_type(self):
        result = build_request({"REQUEST_TYPE": "PfsVerifyUserInput"})
        assert "REQUEST_TYPE=PfsVerifyUserInput" in result

    def test_build_request_crlf_line_endings(self):
        result = build_request({"REQUEST_TYPE": "PfsVerifyUserInput"})
        assert "\r\n" in result

    def test_build_request_ends_with_blank_line(self):
        result = build_request({"REQUEST_TYPE": "PfsVerifyUserInput"})
        assert result.endswith("\r\n")

    def test_build_request_includes_all_params(self):
        result = build_request({
            "REQUEST_TYPE": "PfsVerifyUserInput",
            "DATABASE": "TESTDB",
            "USER_ID": "op1",
        })
        assert "DATABASE=TESTDB" in result
        assert "USER_ID=op1" in result

    def test_build_request_skips_none_values(self):
        result = build_request({
            "REQUEST_TYPE": "PfsVerifyUserInput",
            "OPTIONAL": None,
        })
        assert "OPTIONAL" not in result

    def test_build_request_newline_escaping_in_value(self):
        result = build_request({
            "REQUEST_TYPE": "PfsVerifyUserInput",
            "COMMENT": "line1\nline2",
        })
        assert "&nl;" in result
        assert "\n" not in result.replace("\r\n", "")

    def test_build_request_multiple_params(self):
        params = {
            "REQUEST_TYPE": "PfsSendResults",
            "DATABASE": "TESTDB",
            "USER_ID": "op1",
            "PASSWORD": "pass",
            "SERIAL_NUMBER": "SN001",
            "PASS_FAIL": "P",
        }
        result = build_request(params)
        for key in params:
            assert f"{key}=" in result


class TestParseResponse:

    def test_parse_response_ok(self):
        result = parse_response("OK", "PfsVerifyUserInput")
        assert result["status"] == "OK"

    def test_parse_response_ok_with_data(self):
        result = parse_response("OK\nSN123\n", "PfsVerifyUserInput")
        assert result["status"] == "OK"
        assert "SN123" in result["data"]

    def test_parse_response_failure(self):
        result = parse_response("PfsVerifyUserInput Failure: Invalid credentials", "PfsVerifyUserInput")
        assert result["status"] == "Failure"

    def test_parse_response_failure_message(self):
        result = parse_response("PfsVerifyUserInput Failure: Invalid credentials", "PfsVerifyUserInput")
        assert "Invalid credentials" in result["message"]

    def test_parse_response_warning(self):
        result = parse_response("PfsQuery Warning: Override required", "PfsQuery")
        assert result["status"] == "Warning"

    def test_parse_response_error(self):
        result = parse_response("PfsVerifyUserInput Error: Server error", "PfsVerifyUserInput")
        assert result["status"] == "Error"

    def test_parse_response_empty(self):
        result = parse_response("", "PfsVerifyUserInput")
        assert result["status"] == "Error"

    def test_parse_response_with_return_values(self):
        result = parse_response("OK\nCODE1;Desc1\n", "PfsQuery", return_values="CODE;DESC")
        assert "fields" in result
        assert "CODE" in result["fields"]

    def test_parse_response_unknown_format(self):
        result = parse_response("GARBAGE_RESPONSE", "PfsVerifyUserInput")
        assert result["status"] == "Error"


class TestValidateParameters:

    def test_all_required_present(self):
        valid, errors = validate_parameters(
            {"DATABASE": "TESTDB", "USER_ID": "op1"},
            ["DATABASE", "USER_ID"],
            [],
        )
        assert valid is True
        assert errors == []

    def test_missing_required_param(self):
        valid, errors = validate_parameters(
            {"DATABASE": "TESTDB"},
            ["DATABASE", "USER_ID"],
            [],
        )
        assert valid is False
        assert any("USER_ID" in e for e in errors)

    def test_unknown_param_flagged(self):
        valid, errors = validate_parameters(
            {"DATABASE": "TESTDB", "UNKNOWN": "value"},
            ["DATABASE"],
            [],
        )
        assert valid is False
        assert any("UNKNOWN" in e for e in errors)

    def test_optional_param_allowed(self):
        valid, errors = validate_parameters(
            {"DATABASE": "TESTDB", "OPTIONAL_FIELD": "val"},
            ["DATABASE"],
            ["OPTIONAL_FIELD"],
        )
        assert valid is True

    def test_empty_required_value_flagged(self):
        valid, errors = validate_parameters(
            {"DATABASE": ""},
            ["DATABASE"],
            [],
        )
        assert valid is False


class TestParseDelimitedResponse:

    def test_basic_delimited_parsing(self):
        result = parse_delimited_response(["CODE1;Desc1", "CODE2;Desc2"], ["CODE", "DESC"])
        assert result[0]["CODE"] == "CODE1"
        assert result[0]["DESC"] == "Desc1"

    def test_without_field_names(self):
        result = parse_delimited_response(["CODE1;Desc1"])
        assert result[0]["value"] == "CODE1;Desc1"

    def test_custom_delimiter(self):
        result = parse_delimited_response(["A|B|C"], ["X", "Y", "Z"], delimiter="|")
        assert result[0]["X"] == "A"

    def test_empty_lines_skipped(self):
        result = parse_delimited_response(["", "CODE1;Desc1", ""], ["CODE", "DESC"])
        assert len(result) == 1


class TestBuildDelimitedList:

    def test_basic_list(self):
        items = [{"REF_DES": "U1", "DEFECT_CODE": "PCAC08"}]
        result = build_delimited_list(items, ["REF_DES", "DEFECT_CODE"])
        assert "U1" in result
        assert "PCAC08" in result

    def test_multiple_items(self):
        items = [
            {"REF_DES": "U1", "DEFECT_CODE": "PCAC08"},
            {"REF_DES": "U2", "DEFECT_CODE": "PCAC08"},
        ]
        result = build_delimited_list(items, ["REF_DES", "DEFECT_CODE"])
        assert "U1" in result
        assert "U2" in result

    def test_result_has_brackets(self):
        items = [{"REF_DES": "U1", "DEFECT_CODE": "PCAC08"}]
        result = build_delimited_list(items, ["REF_DES", "DEFECT_CODE"])
        assert result.startswith("[")
        assert result.endswith("]")


class TestValidateSerialNumbers:

    def test_single_serial_number(self):
        valid, sns = validate_serial_numbers("SN123")
        assert valid is True
        assert sns == ["SN123"]

    def test_multiple_serial_numbers(self):
        valid, sns = validate_serial_numbers("SN1;SN2;SN3")
        assert valid is True
        assert len(sns) == 3

    def test_empty_string(self):
        valid, sns = validate_serial_numbers("")
        assert valid is False
        assert sns == []

    def test_none_input(self):
        valid, sns = validate_serial_numbers(None)
        assert valid is False


class TestEscapeUnescape:

    def test_escape_newlines(self):
        assert escape_newlines("line1\nline2") == "line1&nl;line2"

    def test_escape_none(self):
        assert escape_newlines(None) is None

    def test_escape_carriage_return(self):
        result = escape_newlines("line1\r\nline2")
        assert "\r" not in result

    def test_unescape_newlines(self):
        assert unescape_newlines("line1&nl;line2") == "line1\nline2"

    def test_unescape_none(self):
        assert unescape_newlines(None) is None

    def test_roundtrip(self):
        original = "line1\nline2\nline3"
        assert unescape_newlines(escape_newlines(original)) == original


class TestExtractDelimiter:

    def test_semicolon_delimiter(self):
        assert extract_delimiter("CODE;DESC") == ";"

    def test_pipe_delimiter(self):
        assert extract_delimiter("CODE|DESC|TYPE") == "|"

    def test_default_delimiter_when_none(self):
        assert extract_delimiter(None) == ";"

    def test_default_delimiter_when_only_alphanum(self):
        assert extract_delimiter("CODEDESC") == ";"


class TestFormatListResponse:

    def test_basic_format(self):
        result = format_list_response(["CODE1;Desc1", "CODE2;Desc2"], "CODE;DESC")
        assert result[0]["CODE"] == "CODE1"

    def test_empty_data_lines(self):
        result = format_list_response([], "CODE;DESC")
        assert result == []

    def test_no_return_values(self):
        result = format_list_response(["CODE1;Desc1"])
        assert result[0]["value"] == "CODE1;Desc1"
