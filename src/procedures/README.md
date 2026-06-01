# PFS Procedures Module

This module contains all PFS/TestLink procedures implemented in Phase 2 of the Python client development.

## Quick Start

```python
from procedures import (
    PfsVerifyUserInput,      # Transaction procedures
    PfsGetSerialNumbers,     # Retrieval procedures
    PfsGetSystemInfo,        # Utility procedures
)

# Build a request
request = PfsVerifyUserInput.build_request(
    database='DELPHI_HUNTS',
    user_id='OPERATOR1',
    password='password123'
)

# Parse a response
response_text = "OK\n\n"
result = PfsVerifyUserInput.parse_response(response_text)
# Returns: {'status': 'OK', 'data': '', 'raw': 'OK\n\n'}
```

## Module Structure

### transaction.py - 9 Procedures
Core routing and result submission procedures used in production flows:
- `PfsVerifyUserInput` - Authenticate operator
- `PfsSendResults` - Submit test results
- `PfsSendSignoff` - Record signoff
- `PfsPanelize` - Panel assembly tracking
- `PfsLinkCompData` - Component data linking
- `PfsFindSerialNumber` - Serial number lookup
- `PfsGenerateSerialNumbers` - Generate serial numbers
- `PfsSetHalt` - Set production hold
- `PfsClearHalt` - Clear production hold

### retrieval.py - 25 Procedures
Information retrieval procedures for querying system data:

**Reference Data:**
- `PfsGetDefectCodes`, `PfsGetOperationCodes`, `PfsGetWorkCenters`, `PfsGetRepairCodes`, `PfsGetBomItems`

**Serial Number Queries:**
- `PfsGetSerialNumbers`, `PfsGetSnDefects`, `PfsGetSnHistory`, `PfsGetSnLinkedData`, `PfsGetSnMacAddresses`, `PfsGetSnPanelNumber`, `PfsGetSnParentItemInfo`, `PfsGetSnStatus`, `PfsGetSnSwitchInfo`, `PfsGetPnlSerialNumbers`

**Production Data:**
- `PfsGetProductionOrderInfo`, `PfsGetItemInfo`, `PfsGetUsageItems`, `PfsGetCurrentUserInfo`

**Equipment:**
- `PfsGetFeederInfo`, `PfsGetMachineShares`, `PfsGetMacAddrSerialNumber`

**Work Instructions:**
- `PfsGetWorkInstructions`, `PfsGetWorkInstructionOperations`, `PfsGetWorkInstructionMachines`

### utility.py - 11 Procedures
Advanced system procedures:
- `PfsQuery` - Execute custom queries
- `PfsExecuteProcedure` - Execute stored procedures
- `PfsGenerateReport` - Generate reports
- `PfsExportData` - Export data
- `PfsImportData` - Import data
- `PfsGetSystemInfo` - Get system information
- `PfsBackupDatabase` - Backup database
- `PfsRestoreDatabase` - Restore from backup
- `PfsGetAuditLog` - Retrieve audit log
- `PfsGetUsers` - Get user list
- `PfsGetUserRoles` - Get user roles

### templates.py - Helper Functions
Utility functions used by all procedures:
- `build_request()` - Format parameters as PFS request
- `parse_response()` - Parse PFS response
- `validate_parameters()` - Validate required/optional parameters
- `build_delimited_list()` - Build delimited lists
- `parse_delimited_response()` - Parse delimited response data
- `validate_serial_numbers()` - Validate serial number formats
- `escape_newlines()` - Escape newlines in parameters
- `format_defect_structure()` - Format defect data

## Procedure Interface

Every procedure follows the same interface:

```python
class PfsGetSerialNumbers:
    # Class constants
    PROCEDURE_NAME = "PfsGetSerialNumbers"      # Procedure name string
    REQUIRED_PARAMS = {}                        # Required parameters
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}
    
    @staticmethod
    def build_request(**kwargs) -> str:
        """Build a formatted PFS request string."""
        # Returns: "REQUEST_TYPE=PfsGetSerialNumbers\nFILTER=...\n\n"
        pass
    
    @staticmethod
    def parse_response(response: str) -> dict:
        """Parse a PFS response string."""
        # Returns: {'status': 'OK', 'data': '...', 'raw': '...'}
        pass
```

## Usage Examples

### Transaction Procedure
```python
from procedures import PfsVerifyUserInput

# Build request
req = PfsVerifyUserInput.build_request(
    database='DELPHI_HUNTS',
    user_id='TESTOP',
    password='testpass',
    production_order='PO-123'
)
# Result: "REQUEST_TYPE=PfsVerifyUserInput\nDATABASE=DELPHI_HUNTS\n..."

# Parse response
resp = PfsVerifyUserInput.parse_response("OK\n\n")
# Result: {'status': 'OK', 'data': '', 'raw': 'OK\n\n'}
```

### Retrieval Procedure with Filter
```python
from procedures import PfsGetSerialNumbers

# Build request with filter
req = PfsGetSerialNumbers.build_request(
    filter='PART123*',
    return_values='SERIAL_NUMBER;STATUS'
)

# Parse response with delimited data
resp = PfsGetSerialNumbers.parse_response("OK\nSN001;PASS\nSN002;FAIL\n\n")
# Result: {'status': 'OK', 'data': 'SN001;PASS\nSN002;FAIL', ...}
```

### Utility Procedure
```python
from procedures import PfsGetSystemInfo

# Build request
req = PfsGetSystemInfo.build_request(
    info_type='VERSION',
    return_values='VERSION;BUILD_DATE'
)

# Parse response
resp = PfsGetSystemInfo.parse_response("OK\n1.0;2024-01-01\n\n")
```

## PFS Protocol Details

All procedures follow the PFS protocol specification:

### Request Format
```
REQUEST_TYPE=<procedure_name>
PARAM1=<value1>
PARAM2=<value2>
<blank line>
```

### Response Format
```
<status_code>
<optional_data>
<blank line>
```

Status codes:
- `OK` - Successful execution
- `<Procedure> Warning` - Non-fatal warning
- `<Procedure> Failure` - Procedure execution failed
- `<Procedure> Error` - System error

### Parameter Rules
- CRLF line endings (automatic)
- Newlines in values escaped as `&nl;`
- Delimiter auto-detection from first non-alphanumeric character in RETURN_VALUES
- Required parameters must be provided
- Optional parameters can be omitted

## Testing

Run the comprehensive test suite:

```bash
python test/test_phase2_procedures.py
```

Tests verify:
- All 47 procedures import correctly
- Request building with various parameters
- Response parsing functionality
- Procedure attribute validation

## Integration with Client

Use procedures with the main testlink_client:

```python
from testlink_client import TestLinkClient
from procedures import PfsVerifyUserInput, PfsSendResults

# Create client
client = TestLinkClient(host='pfs.example.com', port=5432)

# Build request
req = PfsVerifyUserInput.build_request(
    database='DELPHI_HUNTS',
    user_id='OPERATOR1',
    password='pass123'
)

# Send and receive
response = client.send_request(req)

# Parse response
result = PfsVerifyUserInput.parse_response(response)
```

## API Reference

See PHASE2_COMPLETION_SUMMARY.md for complete API documentation.

## Error Handling

Parse responses to check for errors:

```python
result = PfsGetSerialNumbers.parse_response(response_text)

if result['status'] == 'OK':
    print(f"Data: {result['data']}")
elif 'Warning' in result['status']:
    print(f"Warning: {result['status']}")
else:
    print(f"Error: {result['status']}")
```

## Version
- Phase: 2 (Procedure Implementation)
- Procedures: 47
- Status: Complete
- Last Updated: 2024
