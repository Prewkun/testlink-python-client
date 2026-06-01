"""
Transaction Procedures - Core routing and result submission procedures.

This module implements the primary PFS procedures used in production flows:
- PfsVerifyUserInput: Authenticate operator and validate context
- PfsQuery: Verify unit should be processed at current operation
- PfsSendResults: Submit pass/fail results with optional defects
- PfsSendSignoff: Record signoff completion
- PfsPanelize: Handle panel/kit assembly tracking
- PfsLinkCompData: Link component data to units
- PfsFindSerialNumber: Resolve alternate/parsed serial numbers
- PfsGenerateSerialNumbers: Generate new serial numbers
- PfsSetHalt/PfsClearHalt: Production hold management
"""

from typing import Dict, List, Optional, Any, Tuple
from .templates import (
    build_request,
    parse_response,
    validate_parameters,
)


class PfsVerifyUserInput:
    """Validate operator credentials and optional context."""
    
    PROCEDURE_NAME = 'PfsVerifyUserInput'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD']
    OPTIONAL_PARAMS = ['PRODUCTION_ORDER', 'OPERATION_CODE', 'WORK_CENTER']
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        production_order: Optional[str] = None,
        operation_code: Optional[str] = None,
        work_center: Optional[str] = None,
    ) -> str:
        """
        Build PfsVerifyUserInput request.
        
        Args:
            database: Database alias (e.g., 'DELPHI_HUNTS')
            user_id: Operator ID/login
            password: Operator password
            production_order: Optional production order number
            operation_code: Optional operation code
            work_center: Optional work center identifier
            
        Returns:
            Formatted request string ready to send to PFS server
            
        Example:
            >>> request = PfsVerifyUserInput.build_request(
            ...     database='DELPHI_HUNTS',
            ...     user_id='OPERATOR1',
            ...     password='password123'
            ... )
        """
        params = {
            'REQUEST_TYPE': PfsVerifyUserInput.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
        }
        
        if production_order:
            params['PRODUCTION_ORDER'] = production_order
        if operation_code:
            params['OPERATION_CODE'] = operation_code
        if work_center:
            params['WORK_CENTER'] = work_center
            
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str) -> Dict[str, Any]:
        """
        Parse PfsVerifyUserInput response.
        
        Args:
            response: Raw response from PFS server
            
        Returns:
            Dictionary with keys:
            - status: 'OK', 'Warning', 'Failure', or 'Error'
            - message: Status message (if not OK)
            - operator_id: Verified operator ID (if OK)
            
        Example:
            >>> result = PfsVerifyUserInput.parse_response('OK')
            >>> result['status']
            'OK'
        """
        return parse_response(response, PfsVerifyUserInput.PROCEDURE_NAME)


class PfsQuery:
    """Verify unit should be processed at current operation."""
    
    PROCEDURE_NAME = 'PfsQuery'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD', 'OPERATION_CODE', 'SERIAL_NUMBER']
    OPTIONAL_PARAMS = ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'RETURN_VALUES', 'OVERRIDE_OK', 'MULTIPLE_PO']
    DEFAULT_RETURN_VALUES = 'PFS_SERIAL_NUMBER'
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        operation_code: str,
        serial_number: str,
        production_order: Optional[str] = None,
        item_number: Optional[str] = None,
        return_values: Optional[str] = None,
        override_ok: bool = False,
        multiple_po: bool = False,
    ) -> str:
        """
        Build PfsQuery request.
        
        Args:
            database: Database alias
            user_id: Operator ID
            password: Operator password
            operation_code: Operation code to verify
            serial_number: Serial number (or semicolon-delimited list for panels)
            production_order: Production order (optional but recommended)
            item_number: Item number (alternative to production_order)
            return_values: Semicolon-delimited list of return fields
            override_ok: Allow OVERRIDE_OK in response
            multiple_po: Allow multiple production orders
            
        Returns:
            Formatted request string
            
        Example:
            >>> request = PfsQuery.build_request(
            ...     database='DELPHI_HUNTS',
            ...     user_id='OPERATOR1',
            ...     password='password123',
            ...     operation_code='INSPECT',
            ...     serial_number='SN123456'
            ... )
        """
        params = {
            'REQUEST_TYPE': PfsQuery.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
            'OPERATION_CODE': operation_code,
            'SERIAL_NUMBER': serial_number,
        }
        
        if production_order:
            params['PRODUCTION_ORDER'] = production_order
        if item_number:
            params['ITEM_NUMBER'] = item_number
        if return_values:
            params['RETURN_VALUES'] = return_values
        else:
            params['RETURN_VALUES'] = PfsQuery.DEFAULT_RETURN_VALUES
            
        params['OVERRIDE_OK'] = 'TRUE' if override_ok else 'FALSE'
        params['MULTIPLE_PO'] = 'TRUE' if multiple_po else 'FALSE'
        
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str, return_values: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse PfsQuery response.
        
        Args:
            response: Raw response from PFS server
            return_values: Return values specification (for field mapping)
            
        Returns:
            Dictionary with keys:
            - status: 'OK', 'Warning', 'Failure', or 'Error'
            - message: Status message (if not OK)
            - data: Delimited response data (if OK)
            - override_ok: Boolean indicating if override was allowed
            
        Example:
            >>> result = PfsQuery.parse_response('OK\\nSN123456\\n')
            >>> result['status']
            'OK'
        """
        return parse_response(response, PfsQuery.PROCEDURE_NAME, return_values)


class PfsSendResults:
    """Submit pass/fail results with optional defect data."""
    
    PROCEDURE_NAME = 'PfsSendResults'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD', 'OPERATION_CODE', 'SERIAL_NUMBER', 'PASS_FAIL']
    OPTIONAL_PARAMS = [
        'PRODUCTION_ORDER', 'WORK_CENTER', 'HISTORY_COMMENT',
        'DEFECT_FIELDS', 'DEFECTS', 'FAIL_REQUIRES_DEFECT'
    ]
    VALID_PASS_FAIL = ['P', 'F']
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        operation_code: str,
        serial_number: str,
        pass_fail: str,
        production_order: Optional[str] = None,
        work_center: Optional[str] = None,
        history_comment: Optional[str] = None,
        defect_fields: Optional[str] = None,
        defects: Optional[str] = None,
        fail_requires_defect: bool = True,
    ) -> str:
        """
        Build PfsSendResults request.
        
        Args:
            database: Database alias
            user_id: Operator ID
            password: Operator password
            operation_code: Operation code
            serial_number: Serial number (or semicolon-delimited list)
            pass_fail: 'P' for pass, 'F' for fail
            production_order: Production order (optional but recommended)
            work_center: Work center (optional)
            history_comment: Comment for history (optional)
            defect_fields: Semicolon-delimited field names (e.g., 'REF_DES;DEFECT_CODE')
            defects: Defect list (e.g., '[U1;PCAC08][U2;PCAC08]')
            fail_requires_defect: Whether failures require explicit defects
            
        Returns:
            Formatted request string
            
        Raises:
            ValueError: If pass_fail is not 'P' or 'F'
            ValueError: If defect_fields provided without defects
            
        Example:
            >>> # Pass result
            >>> request = PfsSendResults.build_request(
            ...     database='DELPHI_HUNTS',
            ...     user_id='OPERATOR1',
            ...     password='password123',
            ...     operation_code='INSPECT',
            ...     serial_number='SN123456',
            ...     pass_fail='P'
            ... )
            
            >>> # Fail with defects
            >>> request = PfsSendResults.build_request(
            ...     database='DELPHI_HUNTS',
            ...     user_id='OPERATOR1',
            ...     password='password123',
            ...     operation_code='INSPECT',
            ...     serial_number='SN123456',
            ...     pass_fail='F',
            ...     defect_fields='REF_DES;DEFECT_CODE',
            ...     defects='[U1;PCAC08]'
            ... )
        """
        if pass_fail not in PfsSendResults.VALID_PASS_FAIL:
            raise ValueError(f"pass_fail must be 'P' or 'F', got {pass_fail}")
        
        if defect_fields and not defects:
            raise ValueError("defect_fields requires defects parameter")
        
        if defects and not defect_fields:
            raise ValueError("defects requires defect_fields parameter")
        
        params = {
            'REQUEST_TYPE': PfsSendResults.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
            'OPERATION_CODE': operation_code,
            'SERIAL_NUMBER': serial_number,
            'PASS_FAIL': pass_fail,
        }
        
        if production_order:
            params['PRODUCTION_ORDER'] = production_order
        if work_center:
            params['WORK_CENTER'] = work_center
        if history_comment:
            # Escape newlines in comments
            params['HISTORY_COMMENT'] = history_comment.replace('\n', '&nl;')
            
        if defect_fields and defects:
            params['DEFECT_FIELDS'] = defect_fields
            params['DEFECTS'] = defects
            
        if not fail_requires_defect:
            params['FAIL_REQUIRES_DEFECT'] = 'FALSE'
        
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str) -> Dict[str, Any]:
        """
        Parse PfsSendResults response.
        
        Args:
            response: Raw response from PFS server
            
        Returns:
            Dictionary with keys:
            - status: 'OK', 'Warning', 'Failure', or 'Error'
            - message: Status message (if not OK)
            
        Example:
            >>> result = PfsSendResults.parse_response('OK')
            >>> result['status']
            'OK'
        """
        return parse_response(response, PfsSendResults.PROCEDURE_NAME)


class PfsSendSignoff:
    """Record signoff completion at Signoff stations."""
    
    PROCEDURE_NAME = 'PfsSendSignoff'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD', 'OPERATION_CODE', 'SERIAL_NUMBER']
    OPTIONAL_PARAMS = ['PRODUCTION_ORDER', 'WORK_CENTER', 'HISTORY_COMMENT']
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        operation_code: str,
        serial_number: str,
        production_order: Optional[str] = None,
        work_center: Optional[str] = None,
        history_comment: Optional[str] = None,
    ) -> str:
        """
        Build PfsSendSignoff request.
        
        Args:
            database: Database alias
            user_id: Operator ID
            password: Operator password
            operation_code: Operation code (station type must be Signoff)
            serial_number: Serial number (or semicolon-delimited list)
            production_order: Production order (optional but recommended)
            work_center: Work center (optional)
            history_comment: Comment for history (optional)
            
        Returns:
            Formatted request string
        """
        params = {
            'REQUEST_TYPE': PfsSendSignoff.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
            'OPERATION_CODE': operation_code,
            'SERIAL_NUMBER': serial_number,
        }
        
        if production_order:
            params['PRODUCTION_ORDER'] = production_order
        if work_center:
            params['WORK_CENTER'] = work_center
        if history_comment:
            params['HISTORY_COMMENT'] = history_comment.replace('\n', '&nl;')
        
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str) -> Dict[str, Any]:
        """Parse PfsSendSignoff response."""
        return parse_response(response, PfsSendSignoff.PROCEDURE_NAME)


class PfsPanelize:
    """Handle panel/kit assembly tracking."""
    
    PROCEDURE_NAME = 'PfsPanelize'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD', 'PRODUCTION_ORDER', 'OPERATION_CODE']
    OPTIONAL_PARAMS = ['PANEL_NUMBER', 'SERIAL_NUMBERS', 'WORK_CENTER']
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        production_order: str,
        operation_code: str,
        panel_number: Optional[str] = None,
        serial_numbers: Optional[str] = None,
        work_center: Optional[str] = None,
    ) -> str:
        """Build PfsPanelize request."""
        params = {
            'REQUEST_TYPE': PfsPanelize.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
            'PRODUCTION_ORDER': production_order,
            'OPERATION_CODE': operation_code,
        }
        
        if panel_number:
            params['PANEL_NUMBER'] = panel_number
        if serial_numbers:
            params['SERIAL_NUMBERS'] = serial_numbers
        if work_center:
            params['WORK_CENTER'] = work_center
        
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str) -> Dict[str, Any]:
        """Parse PfsPanelize response."""
        return parse_response(response, PfsPanelize.PROCEDURE_NAME)


class PfsLinkCompData:
    """Link component data to units."""
    
    PROCEDURE_NAME = 'PfsLinkCompData'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'COMPONENT_DATA']
    OPTIONAL_PARAMS = ['OPERATION_CODE', 'PRODUCTION_ORDER']
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        serial_number: str,
        component_data: str,
        operation_code: Optional[str] = None,
        production_order: Optional[str] = None,
    ) -> str:
        """Build PfsLinkCompData request."""
        params = {
            'REQUEST_TYPE': PfsLinkCompData.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
            'SERIAL_NUMBER': serial_number,
            'COMPONENT_DATA': component_data,
        }
        
        if operation_code:
            params['OPERATION_CODE'] = operation_code
        if production_order:
            params['PRODUCTION_ORDER'] = production_order
        
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str) -> Dict[str, Any]:
        """Parse PfsLinkCompData response."""
        return parse_response(response, PfsLinkCompData.PROCEDURE_NAME)


class PfsFindSerialNumber:
    """Resolve actual PFS serial number from alternate/parsed form."""
    
    PROCEDURE_NAME = 'PfsFindSerialNumber'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER']
    OPTIONAL_PARAMS = ['RETURN_VALUES', 'PRODUCTION_ORDER', 'OPERATION_CODE']
    DEFAULT_RETURN_VALUES = 'PFS_SERIAL_NUMBER'
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        serial_number: str,
        return_values: Optional[str] = None,
        production_order: Optional[str] = None,
        operation_code: Optional[str] = None,
    ) -> str:
        """Build PfsFindSerialNumber request."""
        params = {
            'REQUEST_TYPE': PfsFindSerialNumber.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
            'SERIAL_NUMBER': serial_number,
            'RETURN_VALUES': return_values or PfsFindSerialNumber.DEFAULT_RETURN_VALUES,
        }
        
        if production_order:
            params['PRODUCTION_ORDER'] = production_order
        if operation_code:
            params['OPERATION_CODE'] = operation_code
        
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str, return_values: Optional[str] = None) -> Dict[str, Any]:
        """Parse PfsFindSerialNumber response."""
        return parse_response(response, PfsFindSerialNumber.PROCEDURE_NAME, return_values)


class PfsGenerateSerialNumbers:
    """Generate new serial numbers."""
    
    PROCEDURE_NAME = 'PfsGenerateSerialNumbers'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD', 'PRODUCTION_ORDER', 'QUANTITY']
    OPTIONAL_PARAMS = ['RETURN_VALUES']
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        production_order: str,
        quantity: int,
        return_values: Optional[str] = None,
    ) -> str:
        """Build PfsGenerateSerialNumbers request."""
        params = {
            'REQUEST_TYPE': PfsGenerateSerialNumbers.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
            'PRODUCTION_ORDER': production_order,
            'QUANTITY': str(quantity),
        }
        
        if return_values:
            params['RETURN_VALUES'] = return_values
        
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str, return_values: Optional[str] = None) -> Dict[str, Any]:
        """Parse PfsGenerateSerialNumbers response."""
        return parse_response(response, PfsGenerateSerialNumbers.PROCEDURE_NAME, return_values)


class PfsSetHalt:
    """Set production hold on a unit or production order."""
    
    PROCEDURE_NAME = 'PfsSetHalt'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD']
    OPTIONAL_PARAMS = ['SERIAL_NUMBER', 'PRODUCTION_ORDER', 'OPERATION_CODE', 'REASON']
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        serial_number: Optional[str] = None,
        production_order: Optional[str] = None,
        operation_code: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> str:
        """Build PfsSetHalt request."""
        params = {
            'REQUEST_TYPE': PfsSetHalt.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
        }
        
        if serial_number:
            params['SERIAL_NUMBER'] = serial_number
        if production_order:
            params['PRODUCTION_ORDER'] = production_order
        if operation_code:
            params['OPERATION_CODE'] = operation_code
        if reason:
            params['REASON'] = reason.replace('\n', '&nl;')
        
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str) -> Dict[str, Any]:
        """Parse PfsSetHalt response."""
        return parse_response(response, PfsSetHalt.PROCEDURE_NAME)


class PfsClearHalt:
    """Clear production hold from a unit or production order."""
    
    PROCEDURE_NAME = 'PfsClearHalt'
    REQUIRED_PARAMS = ['DATABASE', 'USER_ID', 'PASSWORD']
    OPTIONAL_PARAMS = ['SERIAL_NUMBER', 'PRODUCTION_ORDER', 'OPERATION_CODE', 'REASON']
    
    @staticmethod
    def build_request(
        database: str,
        user_id: str,
        password: str,
        serial_number: Optional[str] = None,
        production_order: Optional[str] = None,
        operation_code: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> str:
        """Build PfsClearHalt request."""
        params = {
            'REQUEST_TYPE': PfsClearHalt.PROCEDURE_NAME,
            'DATABASE': database,
            'USER_ID': user_id,
            'PASSWORD': password,
        }
        
        if serial_number:
            params['SERIAL_NUMBER'] = serial_number
        if production_order:
            params['PRODUCTION_ORDER'] = production_order
        if operation_code:
            params['OPERATION_CODE'] = operation_code
        if reason:
            params['REASON'] = reason.replace('\n', '&nl;')
        
        return build_request(params)
    
    @staticmethod
    def parse_response(response: str) -> Dict[str, Any]:
        """Parse PfsClearHalt response."""
        return parse_response(response, PfsClearHalt.PROCEDURE_NAME)
