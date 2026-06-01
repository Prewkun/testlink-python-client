"""
PFS Procedure Implementations.

This module contains all PFS/TestLink procedures organized by category:
- transaction.py: Core routing procedures (PfsVerifyUserInput, PfsQuery, PfsSendResults, etc.)
- retrieval.py: Information retrieval procedures (PfsGetDefectCodes, PfsGetSerialNumbers, etc.)
- utility.py: Utility procedures (PfsFindSerialNumber, PfsPanelize, etc.)
"""

from .transaction import (
    PfsVerifyUserInput,
    PfsSendResults,
    PfsSendSignoff,
    PfsPanelize,
    PfsLinkCompData,
    PfsFindSerialNumber,
    PfsGenerateSerialNumbers,
    PfsSetHalt,
    PfsClearHalt,
)

from .retrieval import (
    PfsGetDefectCodes,
    PfsGetOperationCodes,
    PfsGetWorkCenters,
    PfsGetRepairCodes,
    PfsGetBomItems,
    PfsGetSerialNumbers,
    PfsGetSnDefects,
    PfsGetSnHistory,
    PfsGetSnLinkedData,
    PfsGetSnMacAddresses,
    PfsGetSnPanelNumber,
    PfsGetSnParentItemInfo,
    PfsGetSnStatus,
    PfsGetSnSwitchInfo,
    PfsGetPnlSerialNumbers,
    PfsGetProductionOrderInfo,
    PfsGetItemInfo,
    PfsGetUsageItems,
    PfsGetCurrentUserInfo,
    PfsGetFeederInfo,
    PfsGetMachineShares,
    PfsGetMacAddrSerialNumber,
    PfsGetWorkInstructions,
    PfsGetWorkInstructionOperations,
    PfsGetWorkInstructionMachines,
)

from .utility import (
    PfsQuery,
    PfsExecuteProcedure,
    PfsGenerateReport,
    PfsExportData,
    PfsImportData,
    PfsGetSystemInfo,
    PfsBackupDatabase,
    PfsRestoreDatabase,
    PfsGetAuditLog,
    PfsGetUsers,
    PfsGetUserRoles,
)

from .templates import (
    parse_delimited_response,
    build_delimited_list,
    validate_serial_numbers,
)

__all__ = [
    # Transaction procedures
    'PfsVerifyUserInput',
    'PfsSendResults',
    'PfsSendSignoff',
    'PfsPanelize',
    'PfsLinkCompData',
    'PfsFindSerialNumber',
    'PfsGenerateSerialNumbers',
    'PfsSetHalt',
    'PfsClearHalt',
    # Retrieval procedures
    'PfsGetDefectCodes',
    'PfsGetOperationCodes',
    'PfsGetWorkCenters',
    'PfsGetRepairCodes',
    'PfsGetBomItems',
    'PfsGetSerialNumbers',
    'PfsGetSnDefects',
    'PfsGetSnHistory',
    'PfsGetSnLinkedData',
    'PfsGetSnMacAddresses',
    'PfsGetSnPanelNumber',
    'PfsGetSnParentItemInfo',
    'PfsGetSnStatus',
    'PfsGetSnSwitchInfo',
    'PfsGetPnlSerialNumbers',
    'PfsGetProductionOrderInfo',
    'PfsGetItemInfo',
    'PfsGetUsageItems',
    'PfsGetCurrentUserInfo',
    'PfsGetFeederInfo',
    'PfsGetMachineShares',
    'PfsGetMacAddrSerialNumber',
    'PfsGetWorkInstructions',
    'PfsGetWorkInstructionOperations',
    'PfsGetWorkInstructionMachines',
    # Utility procedures
    'PfsQuery',
    'PfsExecuteProcedure',
    'PfsGenerateReport',
    'PfsExportData',
    'PfsImportData',
    'PfsGetSystemInfo',
    'PfsBackupDatabase',
    'PfsRestoreDatabase',
    'PfsGetAuditLog',
    'PfsGetUsers',
    'PfsGetUserRoles',
    # Utility functions
    'parse_delimited_response',
    'build_delimited_list',
    'validate_serial_numbers',
]
