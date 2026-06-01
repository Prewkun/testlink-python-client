"""
Unit tests for testlink_client.py — TestLinkClient.
"""

import sys
import os
import socket
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from testlink_client import TestLinkClient
from protocol import ResponseStatus
from exceptions import (
    PfsErrorException,
    PfsFailureException,
    PfsWarningException,
    ConnectionException,
    TimeoutException,
)


@pytest.fixture
def client():
    return TestLinkClient(
        host="pfs.example.com",
        database="TESTDB",
        port=50000,
        timeout=30,
        max_retries=3,
    )


class TestTestLinkClientInit:

    def test_host_attribute(self, client):
        assert client.host == "pfs.example.com"

    def test_database_attribute(self, client):
        assert client.database == "TESTDB"

    def test_port_attribute(self, client):
        assert client.port == 50000

    def test_timeout_attribute(self, client):
        assert client.timeout == 30

    def test_max_retries_attribute(self, client):
        assert client.max_retries == 3

    def test_default_port(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB")
        assert c.port == 50000

    def test_default_timeout(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB")
        assert c.timeout == 30

    def test_default_validate_cert(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB")
        assert c.validate_cert is True

    def test_work_center_none_by_default(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB")
        assert c.work_center is None

    def test_work_center_stored(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB", work_center="WC01")
        assert c.work_center == "WC01"

    def test_last_request_empty(self, client):
        assert client.last_request == ""

    def test_last_response_empty(self, client):
        assert client.last_response == ""

    def test_last_status_none(self, client):
        assert client.last_status is None


class TestSendCommand:

    def test_send_command_ok_returns_ok_status(self, client):
        with patch.object(client, '_send_request', return_value='OK'):
            status, msg, data = client.send_command('PfsVerifyUserInput', {})
        assert status == ResponseStatus.OK

    def test_send_command_ok_returns_ok_message(self, client):
        with patch.object(client, '_send_request', return_value='OK'):
            status, msg, data = client.send_command('PfsVerifyUserInput', {})
        assert msg == "OK"

    def test_send_command_ok_data_lines(self, client):
        with patch.object(client, '_send_request', return_value='OK\nline1\nline2\n'):
            status, msg, data = client.send_command('PfsVerifyUserInput', {})
        assert "line1" in data
        assert "line2" in data

    def test_send_command_includes_database(self, client):
        with patch.object(client, '_send_request', return_value='OK') as mock_send:
            client.send_command('PfsVerifyUserInput', {})
        sent_request = mock_send.call_args[0][0]
        assert "DATABASE=TESTDB" in sent_request

    def test_send_command_includes_request_type(self, client):
        with patch.object(client, '_send_request', return_value='OK') as mock_send:
            client.send_command('PfsVerifyUserInput', {})
        sent_request = mock_send.call_args[0][0]
        assert "REQUEST_TYPE=PfsVerifyUserInput" in sent_request

    def test_send_command_includes_user_id_when_provided(self, client):
        with patch.object(client, '_send_request', return_value='OK') as mock_send:
            client.send_command('PfsVerifyUserInput', {}, user_id='op1')
        sent_request = mock_send.call_args[0][0]
        assert "USER_ID=op1" in sent_request

    def test_send_command_includes_password_when_provided(self, client):
        with patch.object(client, '_send_request', return_value='OK') as mock_send:
            client.send_command('PfsVerifyUserInput', {}, password='pass123')
        sent_request = mock_send.call_args[0][0]
        assert "PASSWORD=pass123" in sent_request

    def test_send_command_includes_work_center_from_client(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB", work_center="WC01")
        with patch.object(c, '_send_request', return_value='OK') as mock_send:
            c.send_command('PfsVerifyUserInput', {})
        sent_request = mock_send.call_args[0][0]
        assert "WORK_CENTER=WC01" in sent_request

    def test_send_command_raises_pfs_error_exception(self, client):
        with patch.object(client, '_send_request', return_value='PfsVerifyUserInput Error: bad'):
            with pytest.raises(PfsErrorException):
                client.send_command('PfsVerifyUserInput', {})

    def test_send_command_raises_pfs_failure_exception(self, client):
        with patch.object(client, '_send_request', return_value='PfsVerifyUserInput Failure: bad'):
            with pytest.raises(PfsFailureException):
                client.send_command('PfsVerifyUserInput', {})

    def test_send_command_raises_pfs_warning_exception(self, client):
        with patch.object(client, '_send_request', return_value='PfsVerifyUserInput Warning: caution'):
            with pytest.raises(PfsWarningException):
                client.send_command('PfsVerifyUserInput', {})

    def test_send_command_stores_last_request(self, client):
        with patch.object(client, '_send_request', return_value='OK'):
            client.send_command('PfsVerifyUserInput', {})
        assert "REQUEST_TYPE=PfsVerifyUserInput" in client.last_request

    def test_send_command_stores_last_response(self, client):
        with patch.object(client, '_send_request', return_value='OK'):
            client.send_command('PfsVerifyUserInput', {})
        assert client.last_response == 'OK'

    def test_send_command_stores_last_status(self, client):
        with patch.object(client, '_send_request', return_value='OK'):
            client.send_command('PfsVerifyUserInput', {})
        assert client.last_status == ResponseStatus.OK

    def test_get_last_request(self, client):
        with patch.object(client, '_send_request', return_value='OK'):
            client.send_command('PfsVerifyUserInput', {})
        assert client.get_last_request() == client.last_request

    def test_get_last_response(self, client):
        with patch.object(client, '_send_request', return_value='OK'):
            client.send_command('PfsVerifyUserInput', {})
        assert client.get_last_response() == client.last_response

    def test_get_last_status(self, client):
        with patch.object(client, '_send_request', return_value='OK'):
            client.send_command('PfsVerifyUserInput', {})
        assert client.get_last_status() == ResponseStatus.OK


class TestSendRequestWithRetry:

    def test_raises_connection_exception_after_all_retries(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB", max_retries=2)
        with patch.object(c, '_send_request', side_effect=socket.error("connection refused")):
            with patch('time.sleep'):
                with pytest.raises(ConnectionException):
                    c._send_request_with_retry("REQUEST_TYPE=test\r\n\r\n")

    def test_raises_timeout_exception_on_socket_timeout(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB", max_retries=2)
        with patch.object(c, '_send_request', side_effect=socket.timeout("timed out")):
            with patch('time.sleep'):
                with pytest.raises(TimeoutException):
                    c._send_request_with_retry("REQUEST_TYPE=test\r\n\r\n")

    def test_retries_on_socket_error(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB", max_retries=3)
        call_count = [0]

        def side_effect(req):
            call_count[0] += 1
            if call_count[0] < 3:
                raise socket.error("temporary error")
            return 'OK'

        with patch.object(c, '_send_request', side_effect=side_effect):
            with patch('time.sleep'):
                result = c._send_request_with_retry("REQUEST_TYPE=test\r\n\r\n")
        assert result == 'OK'
        assert call_count[0] == 3

    def test_returns_immediately_on_success(self, client):
        with patch.object(client, '_send_request', return_value='OK') as mock_send:
            result = client._send_request_with_retry("REQUEST_TYPE=test\r\n\r\n")
        assert result == 'OK'
        assert mock_send.call_count == 1

    def test_retries_correct_number_of_times_on_failure(self):
        c = TestLinkClient(host="pfs.example.com", database="TESTDB", max_retries=3)
        with patch.object(c, '_send_request', side_effect=socket.error("err")) as mock_send:
            with patch('time.sleep'):
                with pytest.raises(ConnectionException):
                    c._send_request_with_retry("REQUEST_TYPE=test\r\n\r\n")
        assert mock_send.call_count == 3
