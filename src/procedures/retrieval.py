"""
Retrieval procedures module for PFS Python client.

Contains GET procedures for retrieving data from TestLink/PFS system.
Each procedure implements static build_request() and parse_response() methods.
"""

from .templates import build_request, parse_response

class PfsGetDefectCodes:
    """Retrieve data using PfsGetDefectCodes procedure."""
    PROCEDURE_NAME = "PfsGetDefectCodes"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetDefectCodes request."""
        params = {"REQUEST_TYPE": PfsGetDefectCodes.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetDefectCodes response."""
        return parse_response(response, PfsGetDefectCodes.PROCEDURE_NAME)


class PfsGetOperationCodes:
    """Retrieve data using PfsGetOperationCodes procedure."""
    PROCEDURE_NAME = "PfsGetOperationCodes"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetOperationCodes request."""
        params = {"REQUEST_TYPE": PfsGetOperationCodes.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetOperationCodes response."""
        return parse_response(response, PfsGetOperationCodes.PROCEDURE_NAME)


class PfsGetWorkCenters:
    """Retrieve data using PfsGetWorkCenters procedure."""
    PROCEDURE_NAME = "PfsGetWorkCenters"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetWorkCenters request."""
        params = {"REQUEST_TYPE": PfsGetWorkCenters.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetWorkCenters response."""
        return parse_response(response, PfsGetWorkCenters.PROCEDURE_NAME)


class PfsGetRepairCodes:
    """Retrieve data using PfsGetRepairCodes procedure."""
    PROCEDURE_NAME = "PfsGetRepairCodes"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetRepairCodes request."""
        params = {"REQUEST_TYPE": PfsGetRepairCodes.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetRepairCodes response."""
        return parse_response(response, PfsGetRepairCodes.PROCEDURE_NAME)


class PfsGetBomItems:
    """Retrieve data using PfsGetBomItems procedure."""
    PROCEDURE_NAME = "PfsGetBomItems"
    REQUIRED_PARAMS = {"ITEM_ID": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(item_id, return_values=None):
        """Build PfsGetBomItems request."""
        params = {"REQUEST_TYPE": PfsGetBomItems.PROCEDURE_NAME}
        params["ITEM_ID"] = item_id
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetBomItems response."""
        return parse_response(response, PfsGetBomItems.PROCEDURE_NAME)


class PfsGetSerialNumbers:
    """Retrieve data using PfsGetSerialNumbers procedure."""
    PROCEDURE_NAME = "PfsGetSerialNumbers"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetSerialNumbers request."""
        params = {"REQUEST_TYPE": PfsGetSerialNumbers.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSerialNumbers response."""
        return parse_response(response, PfsGetSerialNumbers.PROCEDURE_NAME)


class PfsGetSnDefects:
    """Retrieve data using PfsGetSnDefects procedure."""
    PROCEDURE_NAME = "PfsGetSnDefects"
    REQUIRED_PARAMS = {"SERIAL_NUMBER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(serial_number, return_values=None):
        """Build PfsGetSnDefects request."""
        params = {"REQUEST_TYPE": PfsGetSnDefects.PROCEDURE_NAME}
        params["SERIAL_NUMBER"] = serial_number
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSnDefects response."""
        return parse_response(response, PfsGetSnDefects.PROCEDURE_NAME)


class PfsGetSnHistory:
    """Retrieve data using PfsGetSnHistory procedure."""
    PROCEDURE_NAME = "PfsGetSnHistory"
    REQUIRED_PARAMS = {"SERIAL_NUMBER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(serial_number, return_values=None):
        """Build PfsGetSnHistory request."""
        params = {"REQUEST_TYPE": PfsGetSnHistory.PROCEDURE_NAME}
        params["SERIAL_NUMBER"] = serial_number
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSnHistory response."""
        return parse_response(response, PfsGetSnHistory.PROCEDURE_NAME)


class PfsGetSnLinkedData:
    """Retrieve data using PfsGetSnLinkedData procedure."""
    PROCEDURE_NAME = "PfsGetSnLinkedData"
    REQUIRED_PARAMS = {"SERIAL_NUMBER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(serial_number, return_values=None):
        """Build PfsGetSnLinkedData request."""
        params = {"REQUEST_TYPE": PfsGetSnLinkedData.PROCEDURE_NAME}
        params["SERIAL_NUMBER"] = serial_number
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSnLinkedData response."""
        return parse_response(response, PfsGetSnLinkedData.PROCEDURE_NAME)


class PfsGetSnMacAddresses:
    """Retrieve data using PfsGetSnMacAddresses procedure."""
    PROCEDURE_NAME = "PfsGetSnMacAddresses"
    REQUIRED_PARAMS = {"SERIAL_NUMBER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(serial_number, return_values=None):
        """Build PfsGetSnMacAddresses request."""
        params = {"REQUEST_TYPE": PfsGetSnMacAddresses.PROCEDURE_NAME}
        params["SERIAL_NUMBER"] = serial_number
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSnMacAddresses response."""
        return parse_response(response, PfsGetSnMacAddresses.PROCEDURE_NAME)


class PfsGetSnPanelNumber:
    """Retrieve data using PfsGetSnPanelNumber procedure."""
    PROCEDURE_NAME = "PfsGetSnPanelNumber"
    REQUIRED_PARAMS = {"SERIAL_NUMBER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(serial_number, return_values=None):
        """Build PfsGetSnPanelNumber request."""
        params = {"REQUEST_TYPE": PfsGetSnPanelNumber.PROCEDURE_NAME}
        params["SERIAL_NUMBER"] = serial_number
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSnPanelNumber response."""
        return parse_response(response, PfsGetSnPanelNumber.PROCEDURE_NAME)


class PfsGetSnParentItemInfo:
    """Retrieve data using PfsGetSnParentItemInfo procedure."""
    PROCEDURE_NAME = "PfsGetSnParentItemInfo"
    REQUIRED_PARAMS = {"SERIAL_NUMBER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(serial_number, return_values=None):
        """Build PfsGetSnParentItemInfo request."""
        params = {"REQUEST_TYPE": PfsGetSnParentItemInfo.PROCEDURE_NAME}
        params["SERIAL_NUMBER"] = serial_number
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSnParentItemInfo response."""
        return parse_response(response, PfsGetSnParentItemInfo.PROCEDURE_NAME)


class PfsGetSnStatus:
    """Retrieve data using PfsGetSnStatus procedure."""
    PROCEDURE_NAME = "PfsGetSnStatus"
    REQUIRED_PARAMS = {"SERIAL_NUMBER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(serial_number, return_values=None):
        """Build PfsGetSnStatus request."""
        params = {"REQUEST_TYPE": PfsGetSnStatus.PROCEDURE_NAME}
        params["SERIAL_NUMBER"] = serial_number
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSnStatus response."""
        return parse_response(response, PfsGetSnStatus.PROCEDURE_NAME)


class PfsGetSnSwitchInfo:
    """Retrieve data using PfsGetSnSwitchInfo procedure."""
    PROCEDURE_NAME = "PfsGetSnSwitchInfo"
    REQUIRED_PARAMS = {"SERIAL_NUMBER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(serial_number, return_values=None):
        """Build PfsGetSnSwitchInfo request."""
        params = {"REQUEST_TYPE": PfsGetSnSwitchInfo.PROCEDURE_NAME}
        params["SERIAL_NUMBER"] = serial_number
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetSnSwitchInfo response."""
        return parse_response(response, PfsGetSnSwitchInfo.PROCEDURE_NAME)


class PfsGetPnlSerialNumbers:
    """Retrieve data using PfsGetPnlSerialNumbers procedure."""
    PROCEDURE_NAME = "PfsGetPnlSerialNumbers"
    REQUIRED_PARAMS = {"PANEL_NUMBER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(panel_number, return_values=None):
        """Build PfsGetPnlSerialNumbers request."""
        params = {"REQUEST_TYPE": PfsGetPnlSerialNumbers.PROCEDURE_NAME}
        params["PANEL_NUMBER"] = panel_number
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetPnlSerialNumbers response."""
        return parse_response(response, PfsGetPnlSerialNumbers.PROCEDURE_NAME)


class PfsGetProductionOrderInfo:
    """Retrieve data using PfsGetProductionOrderInfo procedure."""
    PROCEDURE_NAME = "PfsGetProductionOrderInfo"
    REQUIRED_PARAMS = {"PRODUCTION_ORDER": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(production_order, return_values=None):
        """Build PfsGetProductionOrderInfo request."""
        params = {"REQUEST_TYPE": PfsGetProductionOrderInfo.PROCEDURE_NAME}
        params["PRODUCTION_ORDER"] = production_order
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetProductionOrderInfo response."""
        return parse_response(response, PfsGetProductionOrderInfo.PROCEDURE_NAME)


class PfsGetItemInfo:
    """Retrieve data using PfsGetItemInfo procedure."""
    PROCEDURE_NAME = "PfsGetItemInfo"
    REQUIRED_PARAMS = {"ITEM_ID": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(item_id, return_values=None):
        """Build PfsGetItemInfo request."""
        params = {"REQUEST_TYPE": PfsGetItemInfo.PROCEDURE_NAME}
        params["ITEM_ID"] = item_id
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetItemInfo response."""
        return parse_response(response, PfsGetItemInfo.PROCEDURE_NAME)


class PfsGetUsageItems:
    """Retrieve data using PfsGetUsageItems procedure."""
    PROCEDURE_NAME = "PfsGetUsageItems"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetUsageItems request."""
        params = {"REQUEST_TYPE": PfsGetUsageItems.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetUsageItems response."""
        return parse_response(response, PfsGetUsageItems.PROCEDURE_NAME)


class PfsGetCurrentUserInfo:
    """Retrieve data using PfsGetCurrentUserInfo procedure."""
    PROCEDURE_NAME = "PfsGetCurrentUserInfo"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(return_values=None):
        """Build PfsGetCurrentUserInfo request."""
        params = {"REQUEST_TYPE": PfsGetCurrentUserInfo.PROCEDURE_NAME}
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetCurrentUserInfo response."""
        return parse_response(response, PfsGetCurrentUserInfo.PROCEDURE_NAME)


class PfsGetFeederInfo:
    """Retrieve data using PfsGetFeederInfo procedure."""
    PROCEDURE_NAME = "PfsGetFeederInfo"
    REQUIRED_PARAMS = {"FEEDER_ID": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(feeder_id, return_values=None):
        """Build PfsGetFeederInfo request."""
        params = {"REQUEST_TYPE": PfsGetFeederInfo.PROCEDURE_NAME}
        params["FEEDER_ID"] = feeder_id
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetFeederInfo response."""
        return parse_response(response, PfsGetFeederInfo.PROCEDURE_NAME)


class PfsGetMachineShares:
    """Retrieve data using PfsGetMachineShares procedure."""
    PROCEDURE_NAME = "PfsGetMachineShares"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetMachineShares request."""
        params = {"REQUEST_TYPE": PfsGetMachineShares.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetMachineShares response."""
        return parse_response(response, PfsGetMachineShares.PROCEDURE_NAME)


class PfsGetMacAddrSerialNumber:
    """Retrieve data using PfsGetMacAddrSerialNumber procedure."""
    PROCEDURE_NAME = "PfsGetMacAddrSerialNumber"
    REQUIRED_PARAMS = {"MAC_ADDRESS": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(mac_address, return_values=None):
        """Build PfsGetMacAddrSerialNumber request."""
        params = {"REQUEST_TYPE": PfsGetMacAddrSerialNumber.PROCEDURE_NAME}
        params["MAC_ADDRESS"] = mac_address
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetMacAddrSerialNumber response."""
        return parse_response(response, PfsGetMacAddrSerialNumber.PROCEDURE_NAME)


class PfsGetWorkInstructions:
    """Retrieve data using PfsGetWorkInstructions procedure."""
    PROCEDURE_NAME = "PfsGetWorkInstructions"
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {"FILTER": str, "RETURN_VALUES": str}

    @staticmethod
    def build_request(filter=None, return_values=None):
        """Build PfsGetWorkInstructions request."""
        params = {"REQUEST_TYPE": PfsGetWorkInstructions.PROCEDURE_NAME}
        if filter is not None:
            params["FILTER"] = filter
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetWorkInstructions response."""
        return parse_response(response, PfsGetWorkInstructions.PROCEDURE_NAME)


class PfsGetWorkInstructionOperations:
    """Retrieve data using PfsGetWorkInstructionOperations procedure."""
    PROCEDURE_NAME = "PfsGetWorkInstructionOperations"
    REQUIRED_PARAMS = {"WORK_INSTRUCTION_ID": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(work_instruction_id, return_values=None):
        """Build PfsGetWorkInstructionOperations request."""
        params = {"REQUEST_TYPE": PfsGetWorkInstructionOperations.PROCEDURE_NAME}
        params["WORK_INSTRUCTION_ID"] = work_instruction_id
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetWorkInstructionOperations response."""
        return parse_response(response, PfsGetWorkInstructionOperations.PROCEDURE_NAME)


class PfsGetWorkInstructionMachines:
    """Retrieve data using PfsGetWorkInstructionMachines procedure."""
    PROCEDURE_NAME = "PfsGetWorkInstructionMachines"
    REQUIRED_PARAMS = {"WORK_INSTRUCTION_ID": str}
    OPTIONAL_PARAMS = {"RETURN_VALUES": str}

    @staticmethod
    def build_request(work_instruction_id, return_values=None):
        """Build PfsGetWorkInstructionMachines request."""
        params = {"REQUEST_TYPE": PfsGetWorkInstructionMachines.PROCEDURE_NAME}
        params["WORK_INSTRUCTION_ID"] = work_instruction_id
        if return_values is not None:
            params["RETURN_VALUES"] = return_values
        return build_request(params)

    @staticmethod
    def parse_response(response):
        """Parse PfsGetWorkInstructionMachines response."""
        return parse_response(response, PfsGetWorkInstructionMachines.PROCEDURE_NAME)

