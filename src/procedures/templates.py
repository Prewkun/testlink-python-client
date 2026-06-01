"""
PFS Procedure Templates - Helper functions for building and parsing requests.

This module provides utilities for:
- Building standardized request strings
- Parsing standardized response strings
- Validating parameters
- Handling delimiters and escaping
"""

from typing import Dict, List, Optional, Any, Tuple
import re


def build_request(params: Dict[str, str]) -> str:
    """
    Build a PFS request string from parameters.
    
    Implements PFS protocol rules:
    - name=value format
    - CRLF line endings
    - Blank line terminator
    - Newline escaping (&nl;)
    
    Args:
        params: Dictionary of parameter names and values
        
    Returns:
        Formatted request string with CRLF and blank line
        
    Example:
        >>> request = build_request({
        ...     'REQUEST_TYPE': 'PfsVerifyUserInput',
        ...     'DATABASE': 'DELPHI_HUNTS',
        ...     'USER_ID': 'OP1',
        ...     'PASSWORD': 'pass123'
        ... })
    """
    lines = []
    for key, value in params.items():
        if value is None:
            continue
        # Ensure strings don't have raw newlines
        value_str = str(value)
        if '\n' in value_str and '&nl;' not in value_str:
            value_str = value_str.replace('\n', '&nl;')
        lines.append(f"{key}={value_str}")
    
    # Add blank line terminator
    lines.append("")
    return "\r\n".join(lines)


def parse_response(
    response: str,
    procedure_name: str,
    return_values: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Parse a standardized PFS response.
    
    Handles response types:
    - OK: Success response
    - <Procedure> Warning: <message>
    - <Procedure> Failure: <message>
    - <Procedure> Error: <message>
    
    Args:
        response: Raw response from PFS server
        procedure_name: Expected procedure name (for validation)
        return_values: Expected return value specification (for field mapping)
        
    Returns:
        Dictionary with keys:
        - status: 'OK', 'Warning', 'Failure', or 'Error'
        - message: Status message (if not OK)
        - data: Response data lines (if OK with data)
        - fields: Field names from return_values (if provided)
        
    Example:
        >>> result = parse_response('OK', 'PfsVerifyUserInput')
        >>> result['status']
        'OK'
        
        >>> result = parse_response(
        ...     'PfsQuery Failure: Invalid serial number',
        ...     'PfsQuery'
        ... )
        >>> result['status']
        'Failure'
        >>> result['message']
        'Invalid serial number'
    """
    if not response or not response.strip():
        return {
            'status': 'Error',
            'message': 'Empty response from server',
            'data': [],
        }
    
    lines = response.strip().split('\n')
    first_line = lines[0].strip()
    
    # Check for OK response
    if first_line == 'OK':
        result = {
            'status': 'OK',
            'data': [line.strip() for line in lines[1:] if line.strip()],
        }
        if return_values:
            result['fields'] = return_values.split(';')
        return result
    
    # Check for status message (Warning/Failure/Error)
    match = re.match(r'^(\w+)\s+(Warning|Failure|Error):\s*(.*)', first_line)
    if match:
        proc_name, status_type, message = match.groups()
        return {
            'status': status_type,
            'message': message,
            'procedure': proc_name,
            'data': [],
        }
    
    # Check for alternate format (just the status type)
    for status_type in ['Warning', 'Failure', 'Error']:
        if first_line.startswith(status_type + ':'):
            message = first_line[len(status_type) + 1:].strip()
            return {
                'status': status_type,
                'message': message,
                'data': [],
            }
    
    # Unknown format - treat as error
    return {
        'status': 'Error',
        'message': f'Unknown response format: {first_line}',
        'data': lines,
    }


def validate_parameters(
    params: Dict[str, Optional[str]],
    required: List[str],
    optional: List[str],
) -> Tuple[bool, List[str]]:
    """
    Validate that required parameters are present.
    
    Args:
        params: Dictionary of parameters
        required: List of required parameter names
        optional: List of allowed optional parameter names
        
    Returns:
        Tuple of (is_valid, error_messages)
        
    Example:
        >>> valid, errors = validate_parameters(
        ...     {'DATABASE': 'HUNTS', 'USER_ID': 'OP1'},
        ...     ['DATABASE', 'USER_ID', 'PASSWORD'],
        ...     ['PRODUCTION_ORDER']
        ... )
        >>> valid
        False
        >>> errors
        ['Missing required parameter: PASSWORD']
    """
    errors = []
    
    # Check required parameters
    for param in required:
        if param not in params or not params[param]:
            errors.append(f"Missing required parameter: {param}")
    
    # Check for unknown parameters
    allowed = set(required) | set(optional)
    for param in params:
        if param not in allowed and params[param] is not None:
            errors.append(f"Unknown parameter: {param}")
    
    return len(errors) == 0, errors


def parse_delimited_response(
    response_data: List[str],
    fields: Optional[List[str]] = None,
    delimiter: str = ';',
) -> List[Dict[str, str]]:
    """
    Parse delimited response data into dictionaries.
    
    Args:
        response_data: List of data lines from response
        fields: List of field names (in order)
        delimiter: Field delimiter character
        
    Returns:
        List of dictionaries with field:value pairs
        
    Example:
        >>> data = parse_delimited_response(
        ...     ['HUNTS;Huntsville',  'AUSTIN;Austin'],
        ...     ['CODE', 'DESCRIPTION'],
        ...     ';'
        ... )
        >>> data[0]
        {'CODE': 'HUNTS', 'DESCRIPTION': 'Huntsville'}
    """
    result = []
    for line in response_data:
        if not line.strip():
            continue
        
        values = line.split(delimiter)
        if fields:
            item = {}
            for i, field in enumerate(fields):
                item[field] = values[i] if i < len(values) else ''
            result.append(item)
        else:
            result.append({'value': line})
    
    return result


def build_delimited_list(
    items: List[Dict[str, str]],
    fields: List[str],
    delimiter: str = ';',
    item_delimiter: str = '][',
) -> str:
    """
    Build a delimited list for PFS requests.
    
    Used for DEFECTS parameter format: [field1;field2][field1;field2]
    
    Args:
        items: List of dictionaries with field data
        fields: List of field names (in order)
        delimiter: Field delimiter
        item_delimiter: Item delimiter (with brackets)
        
    Returns:
        Formatted delimited list
        
    Example:
        >>> items = [
        ...     {'REF_DES': 'U1', 'DEFECT_CODE': 'PCAC08'},
        ...     {'REF_DES': 'U2', 'DEFECT_CODE': 'PCAC08'},
        ... ]
        >>> result = build_delimited_list(items, ['REF_DES', 'DEFECT_CODE'])
        >>> result
        '[U1;PCAC08][U2;PCAC08]'
    """
    formatted_items = []
    for item in items:
        values = []
        for field in fields:
            values.append(str(item.get(field, '')))
        formatted_items.append(delimiter.join(values))
    
    return '[' + item_delimiter.join(formatted_items) + ']'


def validate_serial_numbers(serial_numbers: str) -> Tuple[bool, List[str]]:
    """
    Validate serial numbers format.
    
    Args:
        serial_numbers: Serial number or semicolon-delimited list
        
    Returns:
        Tuple of (is_valid, list_of_sns)
        
    Example:
        >>> valid, sns = validate_serial_numbers('SN123')
        >>> valid
        True
        >>> sns
        ['SN123']
        
        >>> valid, sns = validate_serial_numbers('SN1;SN2;SN3')
        >>> valid
        True
        >>> sns
        ['SN1', 'SN2', 'SN3']
    """
    if not serial_numbers or not serial_numbers.strip():
        return False, []
    
    sns = [sn.strip() for sn in serial_numbers.split(';') if sn.strip()]
    return len(sns) > 0, sns


def escape_newlines(text: Optional[str]) -> Optional[str]:
    """
    Escape newlines in text for PFS protocol.
    
    Args:
        text: Text that may contain newlines
        
    Returns:
        Text with newlines replaced by &nl;
        
    Example:
        >>> escape_newlines('Line 1\\nLine 2')
        'Line 1&nl;Line 2'
    """
    if text is None:
        return None
    return text.replace('\n', '&nl;').replace('\r', '')


def unescape_newlines(text: Optional[str]) -> Optional[str]:
    """
    Unescape newlines in text from PFS protocol.
    
    Args:
        text: Text with &nl; markers
        
    Returns:
        Text with &nl; replaced by actual newlines
        
    Example:
        >>> unescape_newlines('Line 1&nl;Line 2')
        'Line 1\\nLine 2'
    """
    if text is None:
        return None
    return text.replace('&nl;', '\n')


def extract_delimiter(return_values: Optional[str]) -> str:
    """
    Extract delimiter from RETURN_VALUES specification.
    
    The first special character (not alphanumeric, underscore, or whitespace)
    in RETURN_VALUES is the delimiter.
    
    Args:
        return_values: RETURN_VALUES specification
        
    Returns:
        Detected delimiter (default ';')
        
    Example:
        >>> extract_delimiter('CODE;DESC')
        ';'
        >>> extract_delimiter('CODE|DESC|TYPE')
        '|'
    """
    if not return_values:
        return ';'
    
    for char in return_values:
        if not (char.isalnum() or char == '_' or char.isspace()):
            return char
    
    return ';'


def format_list_response(
    data_lines: List[str],
    return_values: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    Format a list response into structured data.
    
    Args:
        data_lines: List of delimited data lines
        return_values: Field specification (for field names)
        
    Returns:
        List of dictionaries with field:value pairs
        
    Example:
        >>> lines = ['HUNTS;Huntsville', 'AUSTIN;Austin']
        >>> result = format_list_response(lines, 'CODE;DESC')
        >>> result[0]
        {'CODE': 'HUNTS', 'DESC': 'Huntsville'}
    """
    if not data_lines:
        return []
    
    delimiter = extract_delimiter(return_values)
    fields = return_values.split(delimiter) if return_values else []
    
    return parse_delimited_response(data_lines, fields, delimiter)
