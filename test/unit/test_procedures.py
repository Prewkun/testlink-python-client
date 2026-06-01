"""
Unit tests for all 46 PFS procedures across transaction, retrieval, and utility modules.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

# --- Transaction procedures ---
from procedures.transaction import (
    PfsVerifyUserInput,
    PfsQuery,
    PfsSendResults,
    PfsSendSignoff,
    PfsPanelize,
    PfsLinkCompData,
    PfsFindSerialNumber,
    PfsGenerateSerialNumbers,
    PfsSetHalt,
    PfsClearHalt,
)

# --- Retrieval procedures ---
from procedures.retrieval import (
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

# --- Utility procedures (aliased to avoid name conflicts with transaction) ---
import procedures.utility as utility_module

UtilPfsQuery = utility_module.PfsQuery
PfsExecuteProcedure = utility_module.PfsExecuteProcedure
PfsGenerateReport = utility_module.PfsGenerateReport
PfsExportData = utility_module.PfsExportData
PfsImportData = utility_module.PfsImportData
PfsGetSystemInfo = utility_module.PfsGetSystemInfo
PfsBackupDatabase = utility_module.PfsBackupDatabase
PfsRestoreDatabase = utility_module.PfsRestoreDatabase
PfsGetAuditLog = utility_module.PfsGetAuditLog
PfsGetUsers = utility_module.PfsGetUsers
PfsGetUserRoles = utility_module.PfsGetUserRoles


# ============================================================
# Transaction Procedures
# ============================================================

class TestPfsVerifyUserInput:

    def test_procedure_name_attribute(self):
        assert PfsVerifyUserInput.PROCEDURE_NAME == "PfsVerifyUserInput"

    def test_required_params_attribute(self):
        assert "DATABASE" in PfsVerifyUserInput.REQUIRED_PARAMS
        assert "USER_ID" in PfsVerifyUserInput.REQUIRED_PARAMS
        assert "PASSWORD" in PfsVerifyUserInput.REQUIRED_PARAMS

    def test_optional_params_attribute(self):
        assert "PRODUCTION_ORDER" in PfsVerifyUserInput.OPTIONAL_PARAMS

    def test_build_request_contains_request_type(self):
        result = PfsVerifyUserInput.build_request("TESTDB", "op1", "pass")
        assert "REQUEST_TYPE=PfsVerifyUserInput" in result

    def test_build_request_contains_required_params(self):
        result = PfsVerifyUserInput.build_request("TESTDB", "op1", "pass")
        assert "DATABASE=TESTDB" in result
        assert "USER_ID=op1" in result
        assert "PASSWORD=pass" in result

    def test_build_request_optional_production_order(self):
        result = PfsVerifyUserInput.build_request("TESTDB", "op1", "pass", production_order="PO001")
        assert "PRODUCTION_ORDER=PO001" in result

    def test_build_request_optional_not_included_when_none(self):
        result = PfsVerifyUserInput.build_request("TESTDB", "op1", "pass")
        assert "PRODUCTION_ORDER" not in result

    def test_parse_response_ok(self):
        result = PfsVerifyUserInput.parse_response("OK")
        assert result["status"] == "OK"

    def test_parse_response_failure(self):
        result = PfsVerifyUserInput.parse_response("PfsVerifyUserInput Failure: Invalid credentials")
        assert result["status"] == "Failure"


class TestPfsQuery:

    def test_procedure_name_attribute(self):
        assert PfsQuery.PROCEDURE_NAME == "PfsQuery"

    def test_required_params_attribute(self):
        for param in ["DATABASE", "USER_ID", "PASSWORD", "OPERATION_CODE", "SERIAL_NUMBER"]:
            assert param in PfsQuery.REQUIRED_PARAMS

    def test_build_request_contains_request_type(self):
        result = PfsQuery.build_request("TESTDB", "op1", "pass", "INSPECT", "SN001")
        assert "REQUEST_TYPE=PfsQuery" in result

    def test_build_request_contains_serial_number(self):
        result = PfsQuery.build_request("TESTDB", "op1", "pass", "INSPECT", "SN001")
        assert "SERIAL_NUMBER=SN001" in result

    def test_build_request_optional_production_order(self):
        result = PfsQuery.build_request("TESTDB", "op1", "pass", "INSPECT", "SN001", production_order="PO001")
        assert "PRODUCTION_ORDER=PO001" in result

    def test_parse_response_ok(self):
        result = PfsQuery.parse_response("OK\nSN001\n")
        assert result["status"] == "OK"

    def test_parse_response_failure(self):
        result = PfsQuery.parse_response("PfsQuery Failure: Invalid serial")
        assert result["status"] == "Failure"


class TestPfsSendResults:

    def test_procedure_name_attribute(self):
        assert PfsSendResults.PROCEDURE_NAME == "PfsSendResults"

    def test_required_params_attribute(self):
        for param in ["DATABASE", "USER_ID", "PASSWORD", "OPERATION_CODE", "SERIAL_NUMBER", "PASS_FAIL"]:
            assert param in PfsSendResults.REQUIRED_PARAMS

    def test_build_request_pass(self):
        result = PfsSendResults.build_request("TESTDB", "op1", "pass", "INSPECT", "SN001", "P")
        assert "PASS_FAIL=P" in result

    def test_build_request_fail(self):
        result = PfsSendResults.build_request("TESTDB", "op1", "pass", "INSPECT", "SN001", "F")
        assert "PASS_FAIL=F" in result

    def test_build_request_invalid_pass_fail_raises(self):
        with pytest.raises(ValueError):
            PfsSendResults.build_request("TESTDB", "op1", "pass", "INSPECT", "SN001", "X")

    def test_build_request_defects_without_defect_fields_raises(self):
        with pytest.raises(ValueError):
            PfsSendResults.build_request("TESTDB", "op1", "pass", "INSPECT", "SN001", "F", defects="[U1;PCAC08]")

    def test_build_request_defect_fields_without_defects_raises(self):
        with pytest.raises(ValueError):
            PfsSendResults.build_request("TESTDB", "op1", "pass", "INSPECT", "SN001", "F", defect_fields="REF_DES;DEFECT_CODE")

    def test_build_request_with_defects(self):
        result = PfsSendResults.build_request(
            "TESTDB", "op1", "pass", "INSPECT", "SN001", "F",
            defect_fields="REF_DES;DEFECT_CODE", defects="[U1;PCAC08]"
        )
        assert "DEFECTS=[U1;PCAC08]" in result

    def test_build_request_contains_request_type(self):
        result = PfsSendResults.build_request("TESTDB", "op1", "pass", "INSPECT", "SN001", "P")
        assert "REQUEST_TYPE=PfsSendResults" in result

    def test_parse_response_ok(self):
        result = PfsSendResults.parse_response("OK")
        assert result["status"] == "OK"

    def test_parse_response_failure(self):
        result = PfsSendResults.parse_response("PfsSendResults Failure: Invalid operation")
        assert result["status"] == "Failure"


class TestPfsSendSignoff:

    def test_procedure_name_attribute(self):
        assert PfsSendSignoff.PROCEDURE_NAME == "PfsSendSignoff"

    def test_build_request_contains_request_type(self):
        result = PfsSendSignoff.build_request("TESTDB", "op1", "pass", "SIGNOFF", "SN001")
        assert "REQUEST_TYPE=PfsSendSignoff" in result

    def test_build_request_contains_required_params(self):
        result = PfsSendSignoff.build_request("TESTDB", "op1", "pass", "SIGNOFF", "SN001")
        assert "SERIAL_NUMBER=SN001" in result
        assert "OPERATION_CODE=SIGNOFF" in result

    def test_build_request_optional_history_comment(self):
        result = PfsSendSignoff.build_request("TESTDB", "op1", "pass", "SIGNOFF", "SN001", history_comment="Done")
        assert "HISTORY_COMMENT=Done" in result

    def test_parse_response_ok(self):
        result = PfsSendSignoff.parse_response("OK")
        assert result["status"] == "OK"


class TestPfsPanelize:

    def test_procedure_name_attribute(self):
        assert PfsPanelize.PROCEDURE_NAME == "PfsPanelize"

    def test_build_request_contains_request_type(self):
        result = PfsPanelize.build_request("TESTDB", "op1", "pass", "PO001", "PANELIZE")
        assert "REQUEST_TYPE=PfsPanelize" in result

    def test_build_request_optional_panel_number(self):
        result = PfsPanelize.build_request("TESTDB", "op1", "pass", "PO001", "PANELIZE", panel_number="PN001")
        assert "PANEL_NUMBER=PN001" in result

    def test_parse_response_ok(self):
        result = PfsPanelize.parse_response("OK")
        assert result["status"] == "OK"


class TestPfsLinkCompData:

    def test_procedure_name_attribute(self):
        assert PfsLinkCompData.PROCEDURE_NAME == "PfsLinkCompData"

    def test_build_request_contains_request_type(self):
        result = PfsLinkCompData.build_request("TESTDB", "op1", "pass", "SN001", "COMPDATA")
        assert "REQUEST_TYPE=PfsLinkCompData" in result

    def test_build_request_contains_component_data(self):
        result = PfsLinkCompData.build_request("TESTDB", "op1", "pass", "SN001", "COMPDATA")
        assert "COMPONENT_DATA=COMPDATA" in result

    def test_parse_response_ok(self):
        result = PfsLinkCompData.parse_response("OK")
        assert result["status"] == "OK"


class TestPfsFindSerialNumber:

    def test_procedure_name_attribute(self):
        assert PfsFindSerialNumber.PROCEDURE_NAME == "PfsFindSerialNumber"

    def test_build_request_contains_request_type(self):
        result = PfsFindSerialNumber.build_request("TESTDB", "op1", "pass", "SN001")
        assert "REQUEST_TYPE=PfsFindSerialNumber" in result

    def test_build_request_default_return_values(self):
        result = PfsFindSerialNumber.build_request("TESTDB", "op1", "pass", "SN001")
        assert "RETURN_VALUES=PFS_SERIAL_NUMBER" in result

    def test_parse_response_ok(self):
        result = PfsFindSerialNumber.parse_response("OK\nPFS_SN001\n")
        assert result["status"] == "OK"


class TestPfsGenerateSerialNumbers:

    def test_procedure_name_attribute(self):
        assert PfsGenerateSerialNumbers.PROCEDURE_NAME == "PfsGenerateSerialNumbers"

    def test_build_request_contains_request_type(self):
        result = PfsGenerateSerialNumbers.build_request("TESTDB", "op1", "pass", "PO001", 5)
        assert "REQUEST_TYPE=PfsGenerateSerialNumbers" in result

    def test_build_request_contains_quantity(self):
        result = PfsGenerateSerialNumbers.build_request("TESTDB", "op1", "pass", "PO001", 5)
        assert "QUANTITY=5" in result

    def test_parse_response_ok(self):
        result = PfsGenerateSerialNumbers.parse_response("OK\nSN001\nSN002\n")
        assert result["status"] == "OK"


class TestPfsSetHalt:

    def test_procedure_name_attribute(self):
        assert PfsSetHalt.PROCEDURE_NAME == "PfsSetHalt"

    def test_build_request_contains_request_type(self):
        result = PfsSetHalt.build_request("TESTDB", "op1", "pass")
        assert "REQUEST_TYPE=PfsSetHalt" in result

    def test_build_request_optional_serial_number(self):
        result = PfsSetHalt.build_request("TESTDB", "op1", "pass", serial_number="SN001")
        assert "SERIAL_NUMBER=SN001" in result

    def test_parse_response_ok(self):
        result = PfsSetHalt.parse_response("OK")
        assert result["status"] == "OK"


class TestPfsClearHalt:

    def test_procedure_name_attribute(self):
        assert PfsClearHalt.PROCEDURE_NAME == "PfsClearHalt"

    def test_build_request_contains_request_type(self):
        result = PfsClearHalt.build_request("TESTDB", "op1", "pass")
        assert "REQUEST_TYPE=PfsClearHalt" in result

    def test_build_request_optional_serial_number(self):
        result = PfsClearHalt.build_request("TESTDB", "op1", "pass", serial_number="SN001")
        assert "SERIAL_NUMBER=SN001" in result

    def test_parse_response_ok(self):
        result = PfsClearHalt.parse_response("OK")
        assert result["status"] == "OK"


# ============================================================
# Retrieval Procedures — parametrized across all 25
# ============================================================

RETRIEVAL_CLASSES_NO_REQUIRED = [
    (PfsGetDefectCodes, {"build_kwargs": {}}),
    (PfsGetOperationCodes, {"build_kwargs": {}}),
    (PfsGetWorkCenters, {"build_kwargs": {}}),
    (PfsGetRepairCodes, {"build_kwargs": {}}),
    (PfsGetSerialNumbers, {"build_kwargs": {}}),
    (PfsGetUsageItems, {"build_kwargs": {}}),
    (PfsGetCurrentUserInfo, {"build_kwargs": {}}),
    (PfsGetMachineShares, {"build_kwargs": {}}),
    (PfsGetWorkInstructions, {"build_kwargs": {}}),
]

RETRIEVAL_CLASSES_WITH_REQUIRED = [
    (PfsGetBomItems, {"build_kwargs": {"item_id": "ITEM001"}}),
    (PfsGetSnDefects, {"build_kwargs": {"serial_number": "SN001"}}),
    (PfsGetSnHistory, {"build_kwargs": {"serial_number": "SN001"}}),
    (PfsGetSnLinkedData, {"build_kwargs": {"serial_number": "SN001"}}),
    (PfsGetSnMacAddresses, {"build_kwargs": {"serial_number": "SN001"}}),
    (PfsGetSnPanelNumber, {"build_kwargs": {"serial_number": "SN001"}}),
    (PfsGetSnParentItemInfo, {"build_kwargs": {"serial_number": "SN001"}}),
    (PfsGetSnStatus, {"build_kwargs": {"serial_number": "SN001"}}),
    (PfsGetSnSwitchInfo, {"build_kwargs": {"serial_number": "SN001"}}),
    (PfsGetPnlSerialNumbers, {"build_kwargs": {"panel_number": "PN001"}}),
    (PfsGetProductionOrderInfo, {"build_kwargs": {"production_order": "PO001"}}),
    (PfsGetItemInfo, {"build_kwargs": {"item_id": "ITEM001"}}),
    (PfsGetFeederInfo, {"build_kwargs": {"feeder_id": "FEEDER001"}}),
    (PfsGetMacAddrSerialNumber, {"build_kwargs": {"mac_address": "AA:BB:CC:DD:EE:FF"}}),
    (PfsGetWorkInstructionOperations, {"build_kwargs": {"work_instruction_id": "WI001"}}),
    (PfsGetWorkInstructionMachines, {"build_kwargs": {"work_instruction_id": "WI001"}}),
]

ALL_RETRIEVAL = RETRIEVAL_CLASSES_NO_REQUIRED + RETRIEVAL_CLASSES_WITH_REQUIRED


@pytest.mark.parametrize("cls,info", ALL_RETRIEVAL, ids=[c[0].__name__ for c in ALL_RETRIEVAL])
class TestRetrievalProcedures:

    def test_has_procedure_name(self, cls, info):
        assert hasattr(cls, "PROCEDURE_NAME")
        assert isinstance(cls.PROCEDURE_NAME, str)
        assert len(cls.PROCEDURE_NAME) > 0

    def test_has_required_params(self, cls, info):
        assert hasattr(cls, "REQUIRED_PARAMS")

    def test_has_optional_params(self, cls, info):
        assert hasattr(cls, "OPTIONAL_PARAMS")

    def test_build_request_contains_request_type(self, cls, info):
        result = cls.build_request(**info["build_kwargs"])
        assert f"REQUEST_TYPE={cls.PROCEDURE_NAME}" in result

    def test_build_request_has_crlf(self, cls, info):
        result = cls.build_request(**info["build_kwargs"])
        assert "\r\n" in result

    def test_build_request_with_optional_filter(self, cls, info):
        if "filter" in cls.build_request.__code__.co_varnames:
            result = cls.build_request(**info["build_kwargs"], filter="TEST_FILTER")
            assert "FILTER=TEST_FILTER" in result

    def test_build_request_with_return_values(self, cls, info):
        result = cls.build_request(**info["build_kwargs"], return_values="FIELD1;FIELD2")
        assert "RETURN_VALUES=FIELD1;FIELD2" in result

    def test_parse_response_ok(self, cls, info):
        result = cls.parse_response("OK")
        assert result["status"] == "OK"

    def test_parse_response_failure(self, cls, info):
        result = cls.parse_response(f"{cls.PROCEDURE_NAME} Failure: Not found")
        assert result["status"] == "Failure"

    def test_parse_response_error(self, cls, info):
        result = cls.parse_response(f"{cls.PROCEDURE_NAME} Error: Server error")
        assert result["status"] == "Error"


# ============================================================
# Utility Procedures — parametrized across all 11
# ============================================================

UTILITY_CLASSES = [
    (UtilPfsQuery, {"build_kwargs": {"query": "SELECT * FROM TABLE"}}),
    (PfsExecuteProcedure, {"build_kwargs": {"procedure_name": "SomeProcedure"}}),
    (PfsGenerateReport, {"build_kwargs": {"report_type": "DAILY"}}),
    (PfsExportData, {"build_kwargs": {"export_type": "CSV"}}),
    (PfsImportData, {"build_kwargs": {"import_type": "CSV", "data": "col1,col2"}}),
    (PfsGetSystemInfo, {"build_kwargs": {}}),
    (PfsBackupDatabase, {"build_kwargs": {}}),
    (PfsRestoreDatabase, {"build_kwargs": {"backup_path": "/backups/db.bak"}}),
    (PfsGetAuditLog, {"build_kwargs": {}}),
    (PfsGetUsers, {"build_kwargs": {}}),
    (PfsGetUserRoles, {"build_kwargs": {"user_id": "op1"}}),
]


@pytest.mark.parametrize("cls,info", UTILITY_CLASSES, ids=[c[0].__name__ for c in UTILITY_CLASSES])
class TestUtilityProcedures:

    def test_has_procedure_name(self, cls, info):
        assert hasattr(cls, "PROCEDURE_NAME")
        assert isinstance(cls.PROCEDURE_NAME, str)

    def test_has_required_params(self, cls, info):
        assert hasattr(cls, "REQUIRED_PARAMS")

    def test_has_optional_params(self, cls, info):
        assert hasattr(cls, "OPTIONAL_PARAMS")

    def test_build_request_contains_request_type(self, cls, info):
        result = cls.build_request(**info["build_kwargs"])
        assert f"REQUEST_TYPE={cls.PROCEDURE_NAME}" in result

    def test_build_request_has_crlf(self, cls, info):
        result = cls.build_request(**info["build_kwargs"])
        assert "\r\n" in result

    def test_parse_response_ok(self, cls, info):
        result = cls.parse_response("OK")
        assert result["status"] == "OK"

    def test_parse_response_failure(self, cls, info):
        result = cls.parse_response(f"{cls.PROCEDURE_NAME} Failure: Something failed")
        assert result["status"] == "Failure"

    def test_parse_response_error(self, cls, info):
        result = cls.parse_response(f"{cls.PROCEDURE_NAME} Error: Server error")
        assert result["status"] == "Error"


# ============================================================
# Specific utility procedure required-param inclusion tests
# ============================================================

class TestUtilPfsQuery:

    def test_procedure_name(self):
        assert UtilPfsQuery.PROCEDURE_NAME == "PfsQuery"

    def test_build_request_contains_query(self):
        result = UtilPfsQuery.build_request(query="SELECT 1")
        assert "QUERY=SELECT 1" in result


class TestPfsExecuteProcedure:

    def test_procedure_name(self):
        assert PfsExecuteProcedure.PROCEDURE_NAME == "PfsExecuteProcedure"

    def test_build_request_contains_procedure_name_param(self):
        result = PfsExecuteProcedure.build_request(procedure_name="MyProc")
        assert "PROCEDURE_NAME=MyProc" in result


class TestPfsGenerateReport:

    def test_build_request_contains_report_type(self):
        result = PfsGenerateReport.build_request(report_type="DAILY")
        assert "REPORT_TYPE=DAILY" in result


class TestPfsExportData:

    def test_build_request_contains_export_type(self):
        result = PfsExportData.build_request(export_type="CSV")
        assert "EXPORT_TYPE=CSV" in result


class TestPfsImportData:

    def test_build_request_contains_import_type_and_data(self):
        result = PfsImportData.build_request(import_type="CSV", data="col1,val1")
        assert "IMPORT_TYPE=CSV" in result
        assert "DATA=col1,val1" in result


class TestPfsRestoreDatabase:

    def test_build_request_contains_backup_path(self):
        result = PfsRestoreDatabase.build_request(backup_path="/backups/db.bak")
        assert "BACKUP_PATH=/backups/db.bak" in result


class TestPfsGetUserRoles:

    def test_build_request_contains_user_id(self):
        result = PfsGetUserRoles.build_request(user_id="op1")
        assert "USER_ID=op1" in result
