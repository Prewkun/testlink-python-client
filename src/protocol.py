"""
TestLink protocol message builder and parser.
Handles request formatting and response parsing according to PFS/TestLink specification.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple

try:
    from .exceptions import ProtocolException
except ImportError:
    from exceptions import ProtocolException


class ResponseStatus(Enum):
    """PFS response status types."""
    OK = "OK"
    WARNING = "Warning"
    FAILURE = "Failure"
    ERROR = "Error"
    UNKNOWN = "Unknown"


class RequestBuilder:
    """
    Builds properly formatted PFS request messages.
    
    PFS Protocol Requirements:
    - ASCII text encoding
    - CRLF line endings (\\r\\n)
    - name=value format (no spaces around =)
    - REQUEST_TYPE must be first line
    - Must end with blank line (double newline)
    - Newlines in values encoded as &nl;
    """
    
    def __init__(self):
        self.parameters: Dict[str, str] = {}
        self.request_type: Optional[str] = None
    
    def set_request_type(self, request_type: str) -> 'RequestBuilder':
        """Set the REQUEST_TYPE (must be first parameter)."""
        self.request_type = request_type
        return self
    
    def set_parameter(self, name: str, value: str) -> 'RequestBuilder':
        """
        Add a parameter to the request.
        
        Args:
            name: Parameter name (case-sensitive)
            value: Parameter value
        
        Returns:
            Self for chaining
        """
        if value is not None:
            # Encode newlines in value
            encoded_value = str(value).replace('\n', '&nl;').replace('\r', '')
            self.parameters[name] = encoded_value
        return self
    
    def set_parameters(self, params: Dict[str, str]) -> 'RequestBuilder':
        """
        Add multiple parameters at once.
        
        Args:
            params: Dictionary of parameter name/value pairs
        
        Returns:
            Self for chaining
        """
        for name, value in params.items():
            self.set_parameter(name, value)
        return self
    
    def build(self) -> str:
        """
        Build the formatted request message.
        
        Returns:
            Properly formatted request string with CRLF and blank line
        
        Raises:
            ProtocolException: If REQUEST_TYPE is not set
        """
        if not self.request_type:
            raise ProtocolException("REQUEST_TYPE must be set")
        
        lines = []
        
        # REQUEST_TYPE must be first
        lines.append(f"REQUEST_TYPE={self.request_type}")
        
        # Add all other parameters
        for name, value in self.parameters.items():
            lines.append(f"{name}={value}")
        
        # Join with CRLF and add terminal blank line
        request = '\r\n'.join(lines) + '\r\n\r\n'
        
        return request
    
    def clear(self) -> 'RequestBuilder':
        """Clear all parameters and request type."""
        self.parameters.clear()
        self.request_type = None
        return self


class ResponseParser:
    """
    Parses PFS response messages.
    
    Response Format:
    - First line: Status (OK, <Proc> Warning: <msg>, <Proc> Failure: <msg>, <Proc> Error: <msg>)
    - Subsequent lines: Data (if status is OK)
    - Blank line terminates response
    """
    
    def __init__(self):
        self.status: ResponseStatus = ResponseStatus.UNKNOWN
        self.message: str = ""
        self.data_lines: List[str] = []
        self.raw_response: str = ""
    
    def parse(self, response: str) -> Tuple[ResponseStatus, str, List[str]]:
        """
        Parse a PFS response.
        
        Args:
            response: Raw response string from server
        
        Returns:
            Tuple of (status, message, data_lines)
        """
        self.raw_response = response
        
        if not response or response.strip() == "":
            self.status = ResponseStatus.ERROR
            self.message = "Empty response from server"
            return (self.status, self.message, [])
        
        # Split into lines and remove trailing whitespace
        lines = [line.rstrip('\r\n') for line in response.split('\n')]
        
        # First line determines status
        first_line = lines[0] if lines else ""
        
        if first_line == "OK":
            self.status = ResponseStatus.OK
            self.message = "OK"
            # Remaining lines are data
            self.data_lines = [line for line in lines[1:] if line]
        
        elif "Warning:" in first_line:
            self.status = ResponseStatus.WARNING
            self.message = first_line
            self.data_lines = [line for line in lines[1:] if line]
        
        elif "Failure:" in first_line:
            self.status = ResponseStatus.FAILURE
            self.message = first_line
            self.data_lines = [line for line in lines[1:] if line]
        
        elif "Error:" in first_line:
            self.status = ResponseStatus.ERROR
            self.message = first_line
            self.data_lines = [line for line in lines[1:] if line]
        
        else:
            self.status = ResponseStatus.UNKNOWN
            self.message = f"Unknown response format: {first_line}"
            self.data_lines = []
        
        return (self.status, self.message, self.data_lines)
    
    def parse_delimited_data(self, delimiter: str = ';') -> List[List[str]]:
        """
        Parse delimited data lines into structured format.
        
        Args:
            delimiter: Delimiter character (default: semicolon)
        
        Returns:
            List of lists, where each inner list is one data row
        """
        parsed_data = []
        for line in self.data_lines:
            if line:
                fields = line.split(delimiter)
                parsed_data.append(fields)
        return parsed_data
    
    def get_status_name(self) -> str:
        """Get the status as a string."""
        return self.status.value if self.status else "Unknown"
