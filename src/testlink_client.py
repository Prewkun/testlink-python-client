"""
TestLink Client - Enhanced PFS client with full procedure support.
Based on the original pfs.py example but with comprehensive features.
"""

import socket
import ssl
import time
from typing import Dict, List, Optional, Tuple

try:
    from .protocol import RequestBuilder, ResponseParser, ResponseStatus
    from .exceptions import (
        PfsErrorException,
        PfsFailureException,
        PfsWarningException,
        ConnectionException,
        TimeoutException
    )
    from .logger import logger, mask_sensitive_data
except ImportError:
    from protocol import RequestBuilder, ResponseParser, ResponseStatus
    from exceptions import (
        PfsErrorException,
        PfsFailureException,
        PfsWarningException,
        ConnectionException,
        TimeoutException
    )
    from logger import logger, mask_sensitive_data


class TestLinkClient:
    """
    Comprehensive TestLink/PFS client implementation.
    
    Supports all 40+ PFS procedures with proper protocol handling,
    TLS 1.2 encryption, retry logic, and comprehensive error handling.
    """
    
    def __init__(
        self,
        host: str,
        database: str,
        port: int = 50000,
        timeout: int = 30,
        work_center: Optional[str] = None,
        validate_cert: bool = True,
        max_retries: int = 3
    ):
        """
        Initialize TestLink client.
        
        Args:
            host: PFS server hostname (DNS alias)
            database: PFS database name (e.g., PFSHJP4)
            port: Server port (default: 50000)
            timeout: Connection timeout in seconds (default: 30)
            work_center: Default work center (optional)
            validate_cert: Validate TLS certificate (default: True)
            max_retries: Maximum connection retry attempts (default: 3)
        """
        self.host = host
        self.database = database
        self.port = port
        self.timeout = timeout
        self.work_center = work_center
        self.validate_cert = validate_cert
        self.max_retries = max_retries
        
        # Session state
        self.last_request = ""
        self.last_response = ""
        self.last_status: Optional[ResponseStatus] = None
        
        logger.info(f"TestLink client initialized: {host}:{port} (Database: {database})")
    
    def send_command(
        self,
        request_type: str,
        parameters: Dict[str, str],
        user_id: Optional[str] = None,
        password: Optional[str] = None
    ) -> Tuple[ResponseStatus, str, List[str]]:
        """
        Send a command to PFS server.
        
        Args:
            request_type: PFS procedure name (e.g., 'PfsVerifyUserInput')
            parameters: Dictionary of parameters
            user_id: User ID (optional if in parameters)
            password: Password (optional if in parameters)
        
        Returns:
            Tuple of (status, message, data_lines)
        
        Raises:
            PfsErrorException: On error response
            PfsFailureException: On failure response
            PfsWarningException: On warning response
            ConnectionException: On connection failure
            TimeoutException: On timeout
        """
        # Build request
        builder = RequestBuilder()
        builder.set_request_type(request_type)
        builder.set_parameter('DATABASE', self.database)
        
        # Add credentials if provided
        if user_id:
            builder.set_parameter('USER_ID', user_id)
        if password:
            builder.set_parameter('PASSWORD', password)
        
        # Add work center if set
        if self.work_center and 'WORK_CENTER' not in parameters:
            builder.set_parameter('WORK_CENTER', self.work_center)
        
        # Add all other parameters
        builder.set_parameters(parameters)
        
        # Build formatted request
        request = builder.build()
        self.last_request = request
        
        # Log request (mask sensitive data)
        log_params = mask_sensitive_data(parameters.copy())
        logger.debug(f"Sending {request_type}: {log_params}")
        
        # Send request and get response
        response = self._send_request_with_retry(request)
        self.last_response = response
        
        # Parse response
        parser = ResponseParser()
        status, message, data_lines = parser.parse(response)
        self.last_status = status
        
        logger.debug(f"Response status: {status.value}, Message: {message}")
        
        # Raise exceptions based on status
        if status == ResponseStatus.ERROR:
            raise PfsErrorException(message)
        elif status == ResponseStatus.FAILURE:
            raise PfsFailureException(message)
        elif status == ResponseStatus.WARNING:
            raise PfsWarningException(message)
        elif status == ResponseStatus.UNKNOWN:
            raise PfsErrorException(f"Unknown response format: {message}")
        
        return (status, message, data_lines)
    
    def _send_request_with_retry(self, request: str) -> str:
        """
        Send request with retry logic.
        
        Args:
            request: Formatted request string
        
        Returns:
            Response string from server
        
        Raises:
            ConnectionException: If all retries fail
            TimeoutException: If request times out
        """
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._send_request(request)
            except socket.timeout as e:
                last_exception = e
                logger.warning(f"Request timeout (attempt {attempt}/{self.max_retries})")
                if attempt < self.max_retries:
                    time.sleep(2)
            except socket.error as e:
                last_exception = e
                logger.warning(f"Connection error (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    time.sleep(2)
        
        # All retries failed
        if isinstance(last_exception, socket.timeout):
            raise TimeoutException(f"Request timed out after {self.max_retries} attempts")
        else:
            raise ConnectionException(f"Connection failed after {self.max_retries} attempts: {last_exception}")
    
    def _send_request(self, request: str) -> str:
        """
        Send single request to PFS server.
        
        Args:
            request: Formatted request string
        
        Returns:
            Response string from server
        """
        pfs_socket = None
        pfs_socket_file = None
        
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Wrap with TLS 1.2
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            if not self.validate_cert:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            pfs_socket = context.wrap_socket(sock, server_hostname=self.host)
            
            # Connect to server
            pfs_socket.connect((self.host, self.port))
            
            # Create file object for easier I/O
            pfs_socket_file = pfs_socket.makefile('rwb', 0)
            
            # Send request
            pfs_socket_file.write(request.encode('ascii'))
            pfs_socket_file.flush()
            
            # Read response
            response = ''
            line = 'initial'
            while line != '':
                line = pfs_socket_file.readline().decode('utf-8').rstrip('\r\n')
                if line != '':
                    response += line + '\n'
            
            return response.rstrip('\n')
        
        finally:
            # Clean up
            if pfs_socket_file:
                try:
                    pfs_socket_file.close()
                except:
                    pass
            if pfs_socket:
                try:
                    pfs_socket.close()
                except:
                    pass
    
    def get_last_request(self) -> str:
        """Get the last request sent."""
        return self.last_request
    
    def get_last_response(self) -> str:
        """Get the last response received."""
        return self.last_response
    
    def get_last_status(self) -> Optional[ResponseStatus]:
        """Get the status of the last response."""
        return self.last_status
