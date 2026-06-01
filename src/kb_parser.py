"""
Parse PFS_MES_Developer_KB knowledge base to extract procedure definitions.

This module reads the knowledge base markdown file and extracts all procedure
definitions including required and optional parameters, storing them in a
structured format for GUI consumption.
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path


def parse_kb_procedures() -> Dict[str, Dict]:
    """
    Parse the KB and return a dict mapping procedure names to their specifications.
    
    Returns:
        Dict with structure:
        {
            'procedure_name': {
                'required': ['PARAM1', 'PARAM2'],
                'optional': ['PARAM3', 'PARAM4'],
                'conditional': [['PARAM_A', 'PARAM_B']],  # One of these required
                'description': 'Brief description',
                'example': 'Example request text',
            }
        }
    """
    kb_path = Path(__file__).parent.parent.parent.parent / "docs" / "knowledge-base" / "PFS_MES_Developer_KB(Full).md"
    
    if not kb_path.exists():
        raise FileNotFoundError(f"Knowledge base not found at {kb_path}")
    
    with open(kb_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    procedures = {}
    
    # Split into procedure blocks by looking for #### (procedure names)
    procedure_pattern = r'#### (\w+)\n\n'
    matches = list(re.finditer(procedure_pattern, content))
    
    for i, match in enumerate(matches):
        proc_name = match.group(1)
        start_pos = match.start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        
        proc_block = content[start_pos:end_pos]
        
        # Parse required parameters
        required = _extract_params(proc_block, 'Required')
        optional = _extract_params(proc_block, 'Optional')
        
        if required or optional:  # Only include if we found param info
            procedures[proc_name] = {
                'required': required,
                'optional': optional,
                'conditional': _extract_conditional(required),
                'description': _extract_description(proc_block),
            }
    
    return procedures


def _extract_params(block: str, param_type: str) -> List[str]:
    """Extract parameter list from Required/Optional line."""
    # Look for pattern: **Required:** or **Optional:**
    pattern = rf'\*\*{param_type}:\*\*\s+([^\n]+)'
    match = re.search(pattern, block, re.IGNORECASE)
    
    if not match:
        return []
    
    param_str = match.group(1)
    params = []
    
    # Handle "or" conditions - split and extract main params
    # Pattern: REQUEST_TYPE, DATABASE, (PARAM1 or PARAM2), PARAM3
    # We want: REQUEST_TYPE, DATABASE, PARAM1, PARAM2, PARAM3
    
    parts = [p.strip() for p in param_str.split(',')]
    
    for part in parts:
        # Remove parentheses if present
        part = part.strip('()')
        
        # Handle "or" alternatives
        if ' or ' in part:
            alternatives = [p.strip() for p in part.split(' or ')]
            params.extend(alternatives)
        else:
            params.append(part)
    
    # Clean up and remove duplicates while preserving order
    cleaned = []
    seen = set()
    for p in params:
        p = p.strip()
        # Skip connector words
        if p.lower() not in ('and', 'or', ''):
            if p not in seen:
                cleaned.append(p)
                seen.add(p)
    
    return cleaned


def _extract_conditional(required: List[str]) -> List[List[str]]:
    """Extract conditional parameter groups (e.g., 'PARAM1 or PARAM2')."""
    # This is a simplified version - in reality we'd parse the original line more carefully
    conditionals = []
    # For now, return empty - could be enhanced to detect OR groups
    return conditionals


def _extract_description(block: str) -> str:
    """Extract description/purpose of procedure."""
    # Get first paragraph after the procedure name
    lines = block.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('**Required:'):
            # Get lines before this
            desc_lines = lines[1:i]
            desc = ' '.join([l.strip() for l in desc_lines if l.strip()])
            return desc[:200] if desc else ''
    return ''


def get_procedure_fields(proc_name: str) -> Dict[str, List[str]]:
    """
    Get required and optional fields for a procedure.
    
    Args:
        proc_name: Name of the procedure
        
    Returns:
        Dict with 'required' and 'optional' keys containing lists of parameter names.
    """
    procedures = parse_kb_procedures()
    
    if proc_name not in procedures:
        return {'required': [], 'optional': []}
    
    proc_spec = procedures[proc_name]
    return {
        'required': proc_spec['required'],
        'optional': proc_spec['optional'],
    }


# Pre-computed KB procedure registry for GUI
# This serves as a fallback and also provides quick access without file I/O
KB_PROCEDURES = {
    # Transaction Procedures
    'PfsVerifyUserInput': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD'],
        'optional': ['PRODUCTION_ORDER', 'OPERATION_CODE', 'WI_OPERATION', 'ITEM_NUMBER', 'WORK_CENTER'],
    },
    'PfsQuery': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'OPERATION_CODE', 'SERIAL_NUMBER'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'RETURN_VALUES', 'OVERRIDE_OK', 'MULTIPLE_PO'],
    },
    'PfsSendResults': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'OPERATION_CODE', 'SERIAL_NUMBER', 'PASS_FAIL'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'WORK_CENTER', 'HISTORY_COMMENT', 'OVERRIDE_OK', 'MULTIPLE_PO', 'FAIL_REQUIRES_DEFECT', 'DEFECT_FIELDS', 'DEFECTS'],
    },
    'PfsSendSignoff': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'OPERATION_CODE', 'SERIAL_NUMBER'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'WORK_CENTER', 'HISTORY_COMMENT', 'OVERRIDE_OK', 'MULTIPLE_PO'],
    },
    'PfsPanelize': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'OPERATION_CODE', 'SERIAL_NUMBER'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'PANEL_NUMBER', 'PANEL_NUMBER_COMMENT', 'WORK_CENTER', 'HISTORY_COMMENT', 'RETURN_VALUES'],
    },
    'PfsLinkCompData': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'OPERATION_CODE', 'SERIAL_NUMBER', 'REF_DES', 'COMP_SERIAL_NUMBER'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'COMP_ITEM_NUMBER', 'COMP_ITEM_REVISION', 'COUNTRY_OF_ORIGIN', 'WORK_CENTER', 'HISTORY_COMMENT'],
    },
    'PfsFindSerialNumber': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'OPERATION_CODE'],
    },
    'PfsGenerateSerialNumbers': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'PRODUCTION_ORDER', 'OPERATION_CODE', 'WORK_CENTER', 'STARTING_SERIAL_NUMBER', 'BASE'],
        'optional': ['ENDING_SERIAL_NUMBER', 'QUANTITY', 'PREFIX_LENGTH', 'SUFFIX_LENGTH', 'INCREMENT', 'GENERATE_NUMBERS', 'RETURN_NUMBERS', 'COMMENT'],
    },
    'PfsSetHalt': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'HALT_COMMENT'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER'],
    },
    'PfsClearHalt': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER'],
    },
    
    # Retrieval Procedures
    'PfsGetBomItems': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER'],
    },
    'PfsGetCurrentUserInfo': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': [],
    },
    'PfsGetDefectCodes': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER', 'OPERATION_CODE'],
    },
    'PfsGetFeederInfo': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER', 'OPERATION_CODE'],
    },
    'PfsGetItemInfo': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['ITEM_NUMBER', 'PRODUCTION_ORDER', 'SERIAL_NUMBER'],
    },
    'PfsGetMacAddrSerialNumber': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'MAC_ADDRESS', 'RETURN_VALUES'],
        'optional': [],
    },
    'PfsGetMachineShares': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': [],
    },
    'PfsGetOperationCodes': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER'],
    },
    'PfsGetPnlSerialNumbers': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PANEL_NUMBER', 'SERIAL_NUMBER'],
    },
    'PfsGetProductionOrderInfo': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER'],
    },
    'PfsGetRepairCodes': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER', 'OPERATION_CODE'],
    },
    'PfsGetSerialNumbers': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'PRODUCTION_ORDER', 'RETURN_VALUES'],
        'optional': [],
    },
    'PfsGetSnDefects': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER'],
    },
    'PfsGetSnHistory': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'TEST_DATA_KEY'],
    },
    'PfsGetSnLinkedData': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'REF_DES'],
    },
    'PfsGetWorkCenters': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': [],
    },
    'PfsGetWorkInstructions': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'FIELD'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER', 'WI_OPERATION', 'OPERATION_CODE', 'KEY'],
    },
    'PfsGetWorkInstructionOperations': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER'],
    },
    'PfsGetWorkInstructionMachines': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER', 'WI_OPERATION', 'OPERATION_CODE'],
    },
    'PfsGetSnMacAddresses': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER'],
    },
    'PfsGetSnPanelNumber': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'RETURN_VALUES'],
        'optional': [],
    },
    'PfsGetSnParentItemInfo': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'RETURN_VALUES'],
        'optional': ['ITEM_NUMBER', 'PRODUCTION_ORDER'],
    },
    'PfsGetSnStatus': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'SERIAL_NUMBER', 'RETURN_VALUES'],
        'optional': ['ITEM_NUMBER', 'PRODUCTION_ORDER'],
    },
    'PfsGetSnSwitchInfo': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'PRODUCTION_ORDER', 'RETURN_VALUES'],
        'optional': [],
    },
    'PfsGetUsageItems': {
        'required': ['REQUEST_TYPE', 'DATABASE', 'USER_ID', 'PASSWORD', 'RETURN_VALUES'],
        'optional': ['PRODUCTION_ORDER', 'ITEM_NUMBER', 'SERIAL_NUMBER', 'WI_OPERATION', 'OPERATION_CODE'],
    },
}


if __name__ == '__main__':
    # Test script
    procs = KB_PROCEDURES
    print(f"Loaded {len(procs)} procedures from KB")
    for name in sorted(procs.keys())[:5]:
        spec = procs[name]
        print(f"\n{name}:")
        print(f"  Required: {spec['required']}")
        print(f"  Optional: {spec['optional']}")
