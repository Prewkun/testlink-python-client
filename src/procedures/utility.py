"""
Utility procedures module for PFS Python client.

Contains advanced and utility procedures for system maintenance and configuration.
"""

from .templates import build_request, parse_response

class PfsQuery:
    """Utility procedure: PfsQuery."""
    PROCEDURE_NAME = "PfsQuery"
    REQUIRED_PARAMS = {"QUERY": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(query, return_values=None):
        """Build PfsQuery request."""
        params = {"REQUEST_TYPE": PfsQuery.PROCEDURE_NAME}
        params["QUERY"] = query
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsQuery response."""
        return parse_response(response, PfsQuery.PROCEDURE_NAME)


class PfsExecuteProcedure:
    """Utility procedure: PfsExecuteProcedure."""
    PROCEDURE_NAME = "PfsExecuteProcedure"
    REQUIRED_PARAMS = {"PROCEDURE_NAME": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(procedure_name, return_values=None):
        """Build PfsExecuteProcedure request."""
        params = {"REQUEST_TYPE": PfsExecuteProcedure.PROCEDURE_NAME}
        params["PROCEDURE_NAME"] = procedure_name
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsExecuteProcedure response."""
        return parse_response(response, PfsExecuteProcedure.PROCEDURE_NAME)


class PfsGenerateReport:
    """Utility procedure: PfsGenerateReport."""
    PROCEDURE_NAME = "PfsGenerateReport"
    REQUIRED_PARAMS = {"REPORT_TYPE": str}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(report_type, filter=None, return_values=None):
        """Build PfsGenerateReport request."""
        params = {"REQUEST_TYPE": PfsGenerateReport.PROCEDURE_NAME}
        params["REPORT_TYPE"] = report_type
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGenerateReport response."""
        return parse_response(response, PfsGenerateReport.PROCEDURE_NAME)


class PfsExportData:
    """Utility procedure: PfsExportData."""
    PROCEDURE_NAME = "PfsExportData"
    REQUIRED_PARAMS = {"EXPORT_TYPE": str}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(export_type, filter=None, return_values=None):
        """Build PfsExportData request."""
        params = {"REQUEST_TYPE": PfsExportData.PROCEDURE_NAME}
        params["EXPORT_TYPE"] = export_type
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsExportData response."""
        return parse_response(response, PfsExportData.PROCEDURE_NAME)


class PfsImportData:
    """Utility procedure: PfsImportData."""
    PROCEDURE_NAME = "PfsImportData"
    REQUIRED_PARAMS = {"IMPORT_TYPE": str, "DATA": str}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(import_type, data, filter=None, return_values=None):
        """Build PfsImportData request."""
        params = {"REQUEST_TYPE": PfsImportData.PROCEDURE_NAME}
        params["IMPORT_TYPE"] = import_type
        params["DATA"] = data
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsImportData response."""
        return parse_response(response, PfsImportData.PROCEDURE_NAME)


class PfsGetSystemInfo:
    """Utility procedure: PfsGetSystemInfo."""
    PROCEDURE_NAME = "PfsGetSystemInfo"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetSystemInfo request."""
        params = {"REQUEST_TYPE": PfsGetSystemInfo.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSystemInfo response."""
        return parse_response(response, PfsGetSystemInfo.PROCEDURE_NAME)


class PfsBackupDatabase:
    """Utility procedure: PfsBackupDatabase."""
    PROCEDURE_NAME = "PfsBackupDatabase"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsBackupDatabase request."""
        params = {"REQUEST_TYPE": PfsBackupDatabase.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsBackupDatabase response."""
        return parse_response(response, PfsBackupDatabase.PROCEDURE_NAME)


class PfsRestoreDatabase:
    """Utility procedure: PfsRestoreDatabase."""
    PROCEDURE_NAME = "PfsRestoreDatabase"
    REQUIRED_PARAMS = {"BACKUP_PATH": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(backup_path, return_values=None):
        """Build PfsRestoreDatabase request."""
        params = {"REQUEST_TYPE": PfsRestoreDatabase.PROCEDURE_NAME}
        params["BACKUP_PATH"] = backup_path
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsRestoreDatabase response."""
        return parse_response(response, PfsRestoreDatabase.PROCEDURE_NAME)


class PfsGetAuditLog:
    """Utility procedure: PfsGetAuditLog."""
    PROCEDURE_NAME = "PfsGetAuditLog"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetAuditLog request."""
        params = {"REQUEST_TYPE": PfsGetAuditLog.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetAuditLog response."""
        return parse_response(response, PfsGetAuditLog.PROCEDURE_NAME)


class PfsGetUsers:
    """Utility procedure: PfsGetUsers."""
    PROCEDURE_NAME = "PfsGetUsers"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetUsers request."""
        params = {"REQUEST_TYPE": PfsGetUsers.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetUsers response."""
        return parse_response(response, PfsGetUsers.PROCEDURE_NAME)


class PfsGetUserRoles:
    """Utility procedure: PfsGetUserRoles."""
    PROCEDURE_NAME = "PfsGetUserRoles"
    REQUIRED_PARAMS = {"USER_ID": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(user_id, return_values=None):
        """Build PfsGetUserRoles request."""
        params = {"REQUEST_TYPE": PfsGetUserRoles.PROCEDURE_NAME}
        params["USER_ID"] = user_id
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetUserRoles response."""
        return parse_response(response, PfsGetUserRoles.PROCEDURE_NAME)

