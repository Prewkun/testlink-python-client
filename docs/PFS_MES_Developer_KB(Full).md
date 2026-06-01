# PFS MES Developer Knowledge Base (TestLink)

This knowledge base summarizes the attached PFS/TestLink reference documents for developers building or maintaining MES integrations.

## Quick Links

- API cheat sheet: [PFS_MES_API_Cheat_Sheet.md](./PFS_MES_API_Cheat_Sheet.md)
- Main docs index: [../../../../DOCUMENTATION_INDEX.md](../../../../DOCUMENTATION_INDEX.md)
- Repository README: [../../../../README.md](../../../../README.md)

## Index

- [1. Purpose and Scope](#1-purpose-and-scope)
- [2. Source Documents Reviewed](#2-source-documents-reviewed)
- [3. System Overview](#3-system-overview)
- [4. Network and Protocol Specification](#4-network-and-protocol-specification)
- [5. Message Format Rules](#5-message-format-rules)
- [6. Response Semantics and Error Handling](#6-response-semantics-and-error-handling)
- [7. Recommended Client Workflow](#7-recommended-client-workflow)
- [8. Configuration and Runtime Parameters](#8-configuration-and-runtime-parameters)
- [9. Core Procedure Quick Reference](#9-core-procedure-quick-reference)
- [10. Procedure Catalog from Developer Guide](#10-procedure-catalog-from-developer-guide)
- [11. Delimited List and Escaping Rules](#11-delimited-list-and-escaping-rules)
- [12. Caching Behavior and Fresh Data Strategy](#12-caching-behavior-and-fresh-data-strategy)
- [13. Database and DNS Alias Mapping](#13-database-and-dns-alias-mapping)
- [14. Implementation Checklist for Middleware Teams](#14-implementation-checklist-for-middleware-teams)
- [15. Known Pitfalls](#15-known-pitfalls)
- [16. Summary for Engineering Managers](#16-summary-for-engineering-managers)
- [17. Full Request Templates (All Procedures)](#17-full-request-templates-all-procedures)
- [18. Implementation Patterns and Best Practices](#18-implementation-patterns-and-best-practices)

## 1. Purpose and Scope

The goal of TestLink integration is to automate PFS interactions so station software can:
- Validate operator credentials and job context.
- Verify a unit should be processed at the current operation.
- Submit pass/fail outcomes (and optional defect details) consistently.
- Reduce operator mistakes and improve throughput.

## 2. Source Documents Reviewed

- [TestLink Client Coding Tips.txt](./TestLink%20Client%20Coding%20Tips.txt)
- [TestLink Database Names and Server Aliases.txt](./TestLink%20Database%20Names%20and%20Server%20Aliases.txt)
- [Testlink Developers Guide.txt](./Testlink%20Developers%20Guide.txt)
- [TestLink_White_Paper.md](./TestLink_White_Paper.md)

## 3. System Overview

TestLink is a stateless client/server RPC interface in front of PFS.

Typical station behavior:
1. Collect login/session context.
2. Call PfsVerifyUserInput once per operator/session update.
3. For each serial number, call PfsQuery before test when possible.
4. Run test.
5. Call PfsSendResults.

## 4. Network and Protocol Specification

- Transport: secure TCP socket.
- Port: 50000.
- Encryption: TLS 1.2.
- Client certificate: not required.
- Server certificate validation: optional but recommended.
- Certificate name if validated: testlink.bench.com.
- Root CA reference: ca.corp.bench.com.

Connection model:
1. Open socket and complete TLS handshake.
2. Send one request message.
3. Receive one response message.
4. Server closes the connection.

## 5. Message Format Rules

Request shape:

REQUEST_TYPE=<procedure name>
PARAM1=<value>
PARAM2=<value>
...
<blank line>

Critical rules:
- Requests and responses are ASCII text.
- Use CRLF newlines.
- End request with a blank line (double newline after last parameter).
- Parameter names are generally case-sensitive.
- Do not place spaces around '='.
- If a parameter value contains newlines, encode as &nl;.

## 6. Response Semantics and Error Handling

Possible response classes:
- OK
- <procedure> Warning: <message>
- <procedure> Failure: <message>
- <procedure> Error: <message>

Handling guidance:
- Always parse first response line first.
- Warning: procedure completed but with caution condition (client decision needed).
- Failure: procedure completed but business/routing validation failed.
- Error: procedure did not complete and operator should stop and escalate.
- Unknown/no response: treat as Error.

Server placeholders in returned values:
- <blank>
- <not found>
- <blank line>

## 7. Recommended Client Workflow

Derived from Client Coding Tips and Developer Guide:

1. Start station software.
2. Load static config from local file:
   - server DNS alias
   - DATABASE
   - default/allowed OPERATION_CODE values
   - WORK_CENTER (can be blank)
   - communication timeout
3. Prompt operator for USER_ID, PASSWORD, PRODUCTION_ORDER, OPERATION_CODE.
4. Call PfsVerifyUserInput.
   - Failure/Error: show message, re-prompt.
5. Prompt/scan SERIAL_NUMBER.
6. Call PfsQuery.
   - Failure: do not test unit, ask for next serial number.
   - Error: show escalation message.
   - Warning: allow supervised continue/cancel decision.
7. Execute test sequence.
8. Call PfsSendResults.
   - Failure: result not stored, manual follow-up required.
   - Error: escalate.
9. Repeat from serial-number stage for next unit.

Notes:
- Do not call PfsVerifyUserInput for every board; call once per session change.
- If pre-test PfsQuery is impossible for a station architecture, continue with direct PfsSendResults (same routing checks happen there).

## 8. Configuration and Runtime Parameters

Store in config (INI/JSON equivalent):
- Server DNS alias.
- DATABASE.
- Default OPERATION_CODE and optional selectable list.
- WORK_CENTER (blank allowed where auto-resolve works).
- Socket/response timeout (recommended minimum 30 seconds).

Prompt at runtime:
- USER_ID
- PASSWORD
- PRODUCTION_ORDER
- OPERATION_CODE (if selectable/editable)
- SERIAL_NUMBER per unit

## 9. Core Procedure Quick Reference

### PfsVerifyUserInput
Purpose:
- Validate credentials and optional production context.

Required:
- REQUEST_TYPE, DATABASE, USER_ID, PASSWORD

Optional:
- PRODUCTION_ORDER, OPERATION_CODE, WI_OPERATION, ITEM_NUMBER, WORK_CENTER

### PfsQuery
Purpose:
- Verify serial number should be processed at current operation.

Required:
- REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, OPERATION_CODE, SERIAL_NUMBER

Optional:
- PRODUCTION_ORDER or ITEM_NUMBER, RETURN_VALUES, OVERRIDE_OK, MULTIPLE_PO

### PfsSendResults
Purpose:
- Record test/inspection pass/fail and optional defect/test data.

Required:
- REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, OPERATION_CODE, SERIAL_NUMBER or QUANTITY, PASS_FAIL

Optional:
- PRODUCTION_ORDER or ITEM_NUMBER, WORK_CENTER, HISTORY_COMMENT, OVERRIDE_OK, MULTIPLE_PO
- Defect-related: FAIL_REQUIRES_DEFECT, DEFECT_FIELDS, DEFECTS

### PfsSendSignoff
Purpose:
- Record Signoff operation completion.

Required:
- REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, OPERATION_CODE, SERIAL_NUMBER

Optional:
- PRODUCTION_ORDER or ITEM_NUMBER, WORK_CENTER, HISTORY_COMMENT, OVERRIDE_OK, MULTIPLE_PO

## 10. Procedure Catalog from Developer Guide

The guide includes the following major procedures:

- PfsVerifyUserInput
- PfsQuery
- PfsSendResults
- PfsSendSignoff
- PfsPanelize
- PfsLinkCompData
- PfsFindSerialNumber
- PfsGenerateSerialNumbers
- PfsGetBomItems
- PfsGetCurrentUserInfo
- PfsGetDefectCodes
- PfsGetFeederInfo
- PfsGetItemInfo
- PfsGetMacAddrSerialNumber
- PfsGetMachineShares
- PfsGetOperationCodes
- PfsGetPnlSerialNumbers
- PfsGetProductionOrderInfo
- PfsGetRepairCodes
- PfsGetSerialNumbers
- PfsGetSnDefects
- PfsGetSnHistory
- PfsGetSnLinkedData
- PfsGetSnMacAddresses
- PfsGetSnPanelNumber
- PfsGetSnParentItemInfo
- PfsGetSnStatus
- PfsGetSnSwitchInfo
- PfsGetUsageItems
- PfsGetWorkCenters
- PfsGetWorkInstructionMachines
- PfsGetWorkInstructionOperations
- PfsGetWorkInstructions
- PfsSetHalt
- PfsClearHalt

Deprecated procedures listed in the guide:
- PfsLogin
- PfsGetItemNumber
- PfsGetItemRevision
- PfsGetItemDescription
- PfsGetRouteSteps
- PfsGetLinkStationData
- PfsGetTestResultData

## 11. Delimited List and Escaping Rules

Default list delimiter is ';'.

Client can define alternate delimiter through:
- RETURN_VALUES (most requests)
- DEFECT_FIELDS (PfsSendResults)

Do not use as delimiter:
- letters, numbers, underscore, space, or square brackets.

Why it matters:
- If values can contain ';' (for example in serial or free text), choose another delimiter.
- Response uses same delimiter as request.

## 12. Caching Behavior and Fresh Data Strategy

- Server caches much PFS data for 10 minutes since last access.
- USE_CACHED_INFO=FALSE is supported for PfsGet* procedures.
- Use sparingly: fresh reads can noticeably increase response time.

## 13. Database and DNS Alias Mapping

Use DNS alias, not server hostnames/IPs.

Reference list from source document:

| Site | Database | Server DNS |
|---|---|---|
| Almelo | PFSALP4 | pfs-gw-alp4.corp.bench.com |
| Angleton | PFSTXP4 | pfs-gw-txp4.corp.bench.com |
| Austin | PFSATP4 | pfs-gw-atp4.corp.bench.com |
| Ayuthaya | PFSTHP4 | pfs-gw-thp4.corp.bench.com |
| Brasov | PFSROP4 | pfs-gw-rop4.corp.bench.com |
| Dunseith | PFSDNP4 | pfs-gw-dnp4.corp.bench.com |
| Guadalajara | PFSMXP4 | pfs-gw-mxp4.corp.bench.com |
| Huntsville | PFSHSP4 | pfs-gw-hsp4.corp.bench.com |
| Scottsdale AZ IoT Group | PFSSZP4 | pfs-gw-szp4.corp.bench.com |
| Moorpark | PFSMPP4 | pfs-gw-mpp4.corp.bench.com |
| Nashua | PFSHDP4 | pfs-gw-hdp4.corp.bench.com |
| Penang | PFSMYP4 | pfs-gw-myp4.corp.bench.com |
| Phoenix | PFSPHP4 | pfs-gw-php4.corp.bench.com |
| Precision Technologies | PFSPTP4 | pfs-gw-ptp4.corp.bench.com |
| Rochester | PFSMNP4 | pfs-gw-mnp4.corp.bench.com |
| San Jose | PFSSJP4 | pfs-gw-sjp4.corp.bench.com |
| Santa Anna | PFSSAP4 | pfs-gw-sap4.corp.bench.com |
| Suzhou | PFSCHP4 | pfs-gw-chp4.corp.bench.com |
| Tijuana | PFSTIP4 | pfs-gw-tip4.corp.bench.com |
| Tijuana (Filtros) | PFSFLP4 | pfs-gw-flp4.corp.bench.com |
| Winona | PFSMNP4 | pfs-gw-mnp4.corp.bench.com |

## 14. Implementation Checklist for Middleware Teams

- Build a single request builder enforcing CRLF and terminal blank line.
- Implement deterministic first-line response parser (OK/Warning/Failure/Error).
- Add timeout control (>=30s recommended default).
- Cache operator session context and only re-verify on context change.
- Always include PRODUCTION_ORDER or ITEM_NUMBER when feasible.
- Provide operator override flow only where policy allows.
- Add robust logging of request metadata and response class (avoid logging passwords).
- For defect upload, validate DEFECT_FIELDS/DEFECTS shape before send.
- For list data, centralize delimiter selection and escaping.
- Keep DNS alias and database in external config.

## 15. Known Pitfalls

- Missing final blank line in request causes server-side wait/timeouts.
- Using raw host/IP instead of DNS alias breaks portability.
- Assuming specific wording of Warning/Failure/Error messages.
- Sending non-ASCII payloads.
- Calling PfsSendResults with unexpected parameters unintentionally stores extra test data.
- Using MULTIPLE_PO=TRUE unnecessarily can slow requests.

## 16. Summary for Engineering Managers

TestLink integration is a high-leverage automation for PFS MES stations. Correctly implemented, it improves traceability, reduces data-entry risk, and increases throughput. The highest-impact engineering controls are strict message formatting, robust response-state handling, and operator flow design around PfsVerifyUserInput, PfsQuery, and PfsSendResults.

## 17. Full Request Templates (All Procedures)

Each procedure has Required Parameters, Optional Parameters, and a Request Example. Use the examples as implementation starters; replace placeholder values and include optional parameters only when needed.

### Routing and Transaction Procedures

#### PfsVerifyUserInput

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD

**Optional:** PRODUCTION_ORDER, OPERATION_CODE, WI_OPERATION, ITEM_NUMBER, WORK_CENTER

**Example:**
```text
REQUEST_TYPE=PfsVerifyUserInput
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
OPERATION_CODE=FCT_1

```

#### PfsQuery

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, OPERATION_CODE, SERIAL_NUMBER

**Optional:** PRODUCTION_ORDER, ITEM_NUMBER, RETURN_VALUES, OVERRIDE_OK, MULTIPLE_PO

**Example:**
```text
REQUEST_TYPE=PfsQuery
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
OPERATION_CODE=FCT_1
SERIAL_NUMBER=ABC1234
PRODUCTION_ORDER=JOBONTHEFLOOR

```

#### PfsSendResults

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, OPERATION_CODE, SERIAL_NUMBER, PASS_FAIL

**Optional:** PRODUCTION_ORDER, ITEM_NUMBER, WORK_CENTER, HISTORY_COMMENT, OVERRIDE_OK, MULTIPLE_PO, FAIL_REQUIRES_DEFECT, DEFECT_FIELDS, DEFECTS, custom test-data parameters

**Example (Pass):**
```text
REQUEST_TYPE=PfsSendResults
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
OPERATION_CODE=FCT_1
SERIAL_NUMBER=ABC1234
PASS_FAIL=P
PRODUCTION_ORDER=JOBONTHEFLOOR
HISTORY_COMMENT=Test completed successfully

```

**Example (Fail with defects):**
```text
REQUEST_TYPE=PfsSendResults
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
OPERATION_CODE=FCT_1
SERIAL_NUMBER=ABC1235
PASS_FAIL=F
PRODUCTION_ORDER=JOBONTHEFLOOR
DEFECT_FIELDS=FAILURE_CODE;FAILURE_COMMENT
DEFECTS=[F0001;5V measurement failed low]

```

#### PfsSendSignoff

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, OPERATION_CODE, SERIAL_NUMBER

**Optional:** PRODUCTION_ORDER, ITEM_NUMBER, WORK_CENTER, HISTORY_COMMENT, OVERRIDE_OK, MULTIPLE_PO

**Example:**
```text
REQUEST_TYPE=PfsSendSignoff
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
OPERATION_CODE=SIGNOFF_OP
SERIAL_NUMBER=ABC1234

```

#### PfsPanelize

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER), OPERATION_CODE, SERIAL_NUMBER

**Optional:** PANEL_NUMBER, PANEL_NUMBER_COMMENT, WORK_CENTER, HISTORY_COMMENT, RETURN_VALUES

**Example:**
```text
REQUEST_TYPE=PfsPanelize
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
OPERATION_CODE=PANELIZE
SERIAL_NUMBER=ABC1234
RETURN_VALUES=PANEL_NUMBER

```

#### PfsLinkCompData

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER), OPERATION_CODE, SERIAL_NUMBER, REF_DES, COMP_SERIAL_NUMBER

**Optional:** COMP_ITEM_NUMBER, COMP_ITEM_REVISION, COUNTRY_OF_ORIGIN, WORK_CENTER, HISTORY_COMMENT

**Example:**
```text
REQUEST_TYPE=PfsLinkCompData
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
OPERATION_CODE=LINKCOMP
SERIAL_NUMBER=ABC1234
REF_DES=U1;U2
COMP_SERIAL_NUMBER=XYZ0001;XYZ0002

```

#### PfsFindSerialNumber

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, SERIAL_NUMBER, RETURN_VALUES

**Optional:** PRODUCTION_ORDER, ITEM_NUMBER, OPERATION_CODE

**Example:**
```text
REQUEST_TYPE=PfsFindSerialNumber
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
SERIAL_NUMBER=ABC1234
RETURN_VALUES=PFS_SERIAL_NUMBER

```

#### PfsGenerateSerialNumbers

**Required:** REQUEST_TYPE, DATABASE, PRODUCTION_ORDER, OPERATION_CODE, WORK_CENTER, STARTING_SERIAL_NUMBER, (ENDING_SERIAL_NUMBER or QUANTITY), BASE

**Optional:** PREFIX_LENGTH, SUFFIX_LENGTH, INCREMENT, GENERATE_NUMBERS, RETURN_NUMBERS, COMMENT

**Example:**
```text
REQUEST_TYPE=PfsGenerateSerialNumbers
DATABASE=PFSXXP4
PRODUCTION_ORDER=JOBONTHEFLOOR
OPERATION_CODE=GENSNGEN
WORK_CENTER=GENSNGEN_WC
STARTING_SERIAL_NUMBER=SN001
QUANTITY=100
BASE=10
GENERATE_NUMBERS=TRUE
RETURN_NUMBERS=TRUE

```

#### PfsSetHalt

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER), SERIAL_NUMBER, HALT_COMMENT

**Optional:** none

**Example:**
```text
REQUEST_TYPE=PfsSetHalt
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
SERIAL_NUMBER=ABC1234
HALT_COMMENT=Awaiting rework authorization

```

#### PfsClearHalt

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER), SERIAL_NUMBER

**Optional:** none

**Example:**
```text
REQUEST_TYPE=PfsClearHalt
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
SERIAL_NUMBER=ABC1234

```


### Information Retrieval Procedures (PfsGet*)

#### PfsGetBomItems

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or (ITEM_NUMBER and SERIAL_NUMBER)), RETURN_VALUES

**Allowed RETURN_VALUES:** COMP_ITEM_NUMBER, COMP_ITEM_DESC, QUANTITY, REF_DES

**Example:**
```text
REQUEST_TYPE=PfsGetBomItems
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=COMP_ITEM_NUMBER;COMP_ITEM_DESC;QUANTITY;REF_DES

```

#### PfsGetCurrentUserInfo

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, RETURN_VALUES

**Allowed RETURN_VALUES:** LOGIN, LAST_NAME, FIRST_NAME, COWOKER_NUMBER, EMAIL_ADDRESS

**Example:**
```text
REQUEST_TYPE=PfsGetCurrentUserInfo
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
RETURN_VALUES=LOGIN;LAST_NAME;FIRST_NAME;EMAIL_ADDRESS

```

#### PfsGetDefectCodes

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, RETURN_VALUES

**Optional:** PRODUCTION_ORDER, (ITEM_NUMBER and SERIAL_NUMBER), OPERATION_CODE

**Allowed RETURN_VALUES:** DEFECT_CODE, DEFECT_DESC, DEFECT_TYPE

**Example:**
```text
REQUEST_TYPE=PfsGetDefectCodes
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
OPERATION_CODE=FCT_1
RETURN_VALUES=DEFECT_CODE;DEFECT_DESC;DEFECT_TYPE

```

#### PfsGetFeederInfo

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or (ITEM_NUMBER and SERIAL_NUMBER)), RETURN_VALUES

**Optional:** OPERATION_CODE

**Example:**
```text
REQUEST_TYPE=PfsGetFeederInfo
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=MACHINE;FEEDER_DEVICE_ID;COMP_ITEM_NUMBER

```

#### PfsGetItemInfo

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (ITEM_NUMBER or PRODUCTION_ORDER or SERIAL_NUMBER), RETURN_VALUES

**Allowed RETURN_VALUES:** COMP_ITEM_NUMBER, COMP_ITEM_DESC, CUST_ASSEMBLY_NUM, CUST_ASSEMBLY_REV

**Example:**
```text
REQUEST_TYPE=PfsGetItemInfo
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=COMP_ITEM_NUMBER;COMP_ITEM_DESC

```

#### PfsGetMacAddrSerialNumber

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, MAC_ADDRESS, RETURN_VALUES

**Allowed RETURN_VALUES:** COMP_SERIAL_NUMBER, COMP_ITEM_NUMBER

**Example:**
```text
REQUEST_TYPE=PfsGetMacAddrSerialNumber
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
MAC_ADDRESS=AA:BB:CC:DD:EE:FF
RETURN_VALUES=COMP_SERIAL_NUMBER;COMP_ITEM_NUMBER

```

#### PfsGetMachineShares

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, RETURN_VALUES

**Allowed RETURN_VALUES:** SERVER_PATH, LOCAL_PATH

**Example:**
```text
REQUEST_TYPE=PfsGetMachineShares
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
RETURN_VALUES=SERVER_PATH;LOCAL_PATH

```

#### PfsGetOperationCodes

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, RETURN_VALUES

**Optional:** PRODUCTION_ORDER, (ITEM_NUMBER and SERIAL_NUMBER)

**Allowed RETURN_VALUES:** OPERATION_CODE, OPERATION_DESC, OPERATION_TYPE, STATION_TYPE, ROUTE_VERIFICATION, (STEP_TYPE, STEP_ORDER, WI_OPERATION, BAAN_TASK, BAAN_TASK_DESC if PO provided)

**Example:**
```text
REQUEST_TYPE=PfsGetOperationCodes
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=OPERATION_CODE;OPERATION_DESC;OPERATION_TYPE;STATION_TYPE

```

#### PfsGetPnlSerialNumbers

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PANEL_NUMBER or SERIAL_NUMBER), RETURN_VALUES

**Allowed RETURN_VALUES:** COMP_SERIAL_NUMBER, COMP_ITEM_NUMBER, PANEL_NUMBER, PANEL_NUMBER_COMMENT

**Example:**
```text
REQUEST_TYPE=PfsGetPnlSerialNumbers
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PANEL_NUMBER=PANEL001
RETURN_VALUES=COMP_SERIAL_NUMBER;COMP_ITEM_NUMBER

```

#### PfsGetProductionOrderInfo

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or (ITEM_NUMBER and SERIAL_NUMBER) or SERIAL_NUMBER), RETURN_VALUES

**Allowed RETURN_VALUES:** PRODUCTION_ORDER, COMP_ITEM_NUMBER, CUST_ITEM_REV, QUANTITY, CREATE_DATE, RELEASE_DATE, WORK_ORDER, SALES_ORDER

**Example:**
```text
REQUEST_TYPE=PfsGetProductionOrderInfo
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=PRODUCTION_ORDER;COMP_ITEM_NUMBER;QUANTITY

```

#### PfsGetRepairCodes

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, RETURN_VALUES

**Optional:** PRODUCTION_ORDER, (ITEM_NUMBER and SERIAL_NUMBER), OPERATION_CODE

**Allowed RETURN_VALUES:** REPAIR_CODE, REPAIR_DESC, REPAIR_TYPE

**Example:**
```text
REQUEST_TYPE=PfsGetRepairCodes
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=REPAIR_CODE;REPAIR_DESC;REPAIR_TYPE

```

#### PfsGetSerialNumbers

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, PRODUCTION_ORDER, RETURN_VALUES

**Allowed RETURN_VALUES:** COMP_SERIAL_NUMBER, COMP_ITEM_NUMBER

**Example:**
```text
REQUEST_TYPE=PfsGetSerialNumbers
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=COMP_SERIAL_NUMBER;COMP_ITEM_NUMBER

```

#### PfsGetSnDefects

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER), SERIAL_NUMBER, RETURN_VALUES

**Allowed RETURN_VALUES:** SRC_OPERATION_CODE, SRC_PRODUCTION_ORDER, FAILURE_CODE, FAILURE_COMMENT, FAILURE_ORIGIN, REF_DES, DEFECT_CODE, DEBUG_COMMENT, REPAIR_CODE

**Example:**
```text
REQUEST_TYPE=PfsGetSnDefects
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
SERIAL_NUMBER=ABC1234
RETURN_VALUES=SRC_OPERATION_CODE;FAILURE_CODE;DEFECT_CODE

```

#### PfsGetSnHistory

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, SERIAL_NUMBER, RETURN_VALUES

**Optional:** PRODUCTION_ORDER, ITEM_NUMBER, TEST_DATA_KEY

**Allowed RETURN_VALUES:** SERIAL_NUMBER, SRC_PRODUCTION_ORDER, SRC_OPERATION_CODE, PASS_FAIL, WORK_CENTER, HISTORY_COMMENT, OPERATOR_ID, TEST_DATA_KEY, TEST_DATA_VALUE

**Example:**
```text
REQUEST_TYPE=PfsGetSnHistory
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
SERIAL_NUMBER=ABC1234
TEST_DATA_KEY=5_VOLT_MEASUREMENT
RETURN_VALUES=TEST_DATA_VALUE

```

#### PfsGetSnLinkedData

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER), SERIAL_NUMBER, RETURN_VALUES

**Optional:** REF_DES

**Allowed RETURN_VALUES:** DATA_VALUE, REF_DES, COMP_SERIAL_NUMBER, COMP_ITEM_NUMBER, COMP_ITEM_DESC, SRC_PRODUCTION_ORDER, SRC_OPERATION_CODE, CREATE_DATE

**Example:**
```text
REQUEST_TYPE=PfsGetSnLinkedData
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
SERIAL_NUMBER=ABC1234
REF_DES=M5
RETURN_VALUES=COMP_SERIAL_NUMBER

```

#### PfsGetSnMacAddresses

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER), SERIAL_NUMBER, RETURN_VALUES

**Allowed RETURN_VALUES:** MAC_ADDRESS, PORT_NUMBER

**Example:**
```text
REQUEST_TYPE=PfsGetSnMacAddresses
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
SERIAL_NUMBER=ABC1234
RETURN_VALUES=MAC_ADDRESS;PORT_NUMBER

```

#### PfsGetSnPanelNumber

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, SERIAL_NUMBER, RETURN_VALUES

**Allowed RETURN_VALUES:** PANEL_NUMBER, PANEL_NUMBER_COMMENT

**Example:**
```text
REQUEST_TYPE=PfsGetSnPanelNumber
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
SERIAL_NUMBER=ABC1234
RETURN_VALUES=PANEL_NUMBER;PANEL_NUMBER_COMMENT

```

#### PfsGetSnParentItemInfo

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (ITEM_NUMBER or PRODUCTION_ORDER), SERIAL_NUMBER, RETURN_VALUES

**Allowed RETURN_VALUES:** COMP_SERIAL_NUMBER, COMP_ITEM_NUMBER, COMP_ITEM_DESC

**Example:**
```text
REQUEST_TYPE=PfsGetSnParentItemInfo
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
ITEM_NUMBER=ITEM12345
SERIAL_NUMBER=ABC1234
RETURN_VALUES=COMP_SERIAL_NUMBER;COMP_ITEM_NUMBER

```

#### PfsGetSnStatus

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (ITEM_NUMBER or PRODUCTION_ORDER), SERIAL_NUMBER, RETURN_VALUES

**Allowed RETURN_VALUES:** STATUS, COMMENTS, ITEM_NUMBER, PRODUCTION_ORDER, OPERATION_CODE, DATE, USER

**Example:**
```text
REQUEST_TYPE=PfsGetSnStatus
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
SERIAL_NUMBER=ABC1234
RETURN_VALUES=STATUS;COMMENTS

```

#### PfsGetSnSwitchInfo

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, PRODUCTION_ORDER, RETURN_VALUES

**Allowed RETURN_VALUES:** COMP_SERIAL_NUMBER, COMP_ITEM_NUMBER

**Example:**
```text
REQUEST_TYPE=PfsGetSnSwitchInfo
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=COMP_SERIAL_NUMBER;COMP_ITEM_NUMBER

```

#### PfsGetUsageItems

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or (ITEM_NUMBER and SERIAL_NUMBER)), (WI_OPERATION or OPERATION_CODE), RETURN_VALUES

**Allowed RETURN_VALUES:** COMP_ITEM_NUMBER, COMP_ITEM_DESC, QUANTITY, REF_DES

**Example:**
```text
REQUEST_TYPE=PfsGetUsageItems
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
OPERATION_CODE=PNP_OP
RETURN_VALUES=COMP_ITEM_NUMBER;QUANTITY;REF_DES

```

#### PfsGetWorkCenters

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, RETURN_VALUES

**Allowed RETURN_VALUES:** WORK_CENTER, WORK_CENTER_DESC

**Example:**
```text
REQUEST_TYPE=PfsGetWorkCenters
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
RETURN_VALUES=WORK_CENTER;WORK_CENTER_DESC

```

#### PfsGetWorkInstructionMachines

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or (ITEM_NUMBER and SERIAL_NUMBER)), (WI_OPERATION or OPERATION_CODE), RETURN_VALUES

**Allowed RETURN_VALUES:** MACHINE, SIDE, PROGRAM, PATH, PRIORITY

**Example:**
```text
REQUEST_TYPE=PfsGetWorkInstructionMachines
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
OPERATION_CODE=PNP_OP
RETURN_VALUES=MACHINE;SIDE;PROGRAM;PATH

```

#### PfsGetWorkInstructionOperations

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or (ITEM_NUMBER and SERIAL_NUMBER)), RETURN_VALUES

**Allowed RETURN_VALUES:** WI_OPERATION, BAAN_TASK, BAAN_TASK_DESC, WORK_CENTER, COUNT_POINT

**Example:**
```text
REQUEST_TYPE=PfsGetWorkInstructionOperations
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=WI_OPERATION;BAAN_TASK;WORK_CENTER

```

#### PfsGetWorkInstructions

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or (ITEM_NUMBER and SERIAL_NUMBER)), (WI_OPERATION or OPERATION_CODE), FIELD

**Optional:** KEY

**FIELD values:** MACHINE_PROGRAMS, MATERIALS, TOOLING, SPECIAL_INSTRUCTIONS, LABELS

**Example:**
```text
REQUEST_TYPE=PfsGetWorkInstructions
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
OPERATION_CODE=PNP_OP
FIELD=SPECIAL_INSTRUCTIONS

```


### Deprecated Procedures (Template Reference Only)

Use these only if maintaining legacy clients. New development should use the non-deprecated alternatives.

#### PfsLogin (Use: PfsVerifyUserInput)

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD

**Optional:** PRODUCTION_ORDER, ITEM_NUMBER, OPERATION_CODE, WORK_CENTER

**Example:**
```text
REQUEST_TYPE=PfsLogin
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR

```

#### PfsGetItemNumber (Use: PfsGetItemInfo)

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or SERIAL_NUMBER)

**Example:**
```text
REQUEST_TYPE=PfsGetItemNumber
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR

```

#### PfsGetItemRevision (Use: PfsGetItemInfo)

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER)

**Example:**
```text
REQUEST_TYPE=PfsGetItemRevision
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
ITEM_NUMBER=ITEM12345

```

#### PfsGetItemDescription (Use: PfsGetItemInfo)

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (ITEM_NUMBER or PRODUCTION_ORDER)

**Example:**
```text
REQUEST_TYPE=PfsGetItemDescription
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR

```

#### PfsGetRouteSteps (Use: PfsGetOperationCodes)

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or (ITEM_NUMBER and SERIAL_NUMBER)), RETURN_VALUES

**Allowed RETURN_VALUES:** OPERATION_CODE, OPERATION_DESC, OPERATION_TYPE, STATION_TYPE, STEP_TYPE, STEP_ORDER

**Example:**
```text
REQUEST_TYPE=PfsGetRouteSteps
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
RETURN_VALUES=OPERATION_CODE;OPERATION_DESC;STATION_TYPE

```

#### PfsGetLinkStationData (Use: PfsGetSnLinkedData)

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER), SERIAL_NUMBER, RETURN_VALUES

**Allowed RETURN_VALUES:** DATA_VALUE, LINK_STATION_TYPE, LINK_STATION_ID, LINK_STATION_PROMPT, REF_DES, COMP_SERIAL_NUMBER, COMP_ITEM_NUMBER, COMP_ITEM_DESC

**Example:**
```text
REQUEST_TYPE=PfsGetLinkStationData
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
SERIAL_NUMBER=ABC1234
RETURN_VALUES=DATA_VALUE;REF_DES

```

#### PfsGetTestResultData (Use: PfsGetSnHistory)

**Required:** REQUEST_TYPE, DATABASE, USER_ID, PASSWORD, (PRODUCTION_ORDER or ITEM_NUMBER), SERIAL_NUMBER, SRC_OPERATION_CODE, RETURN_VALUES

**RETURN_VALUES:** Custom test-data keys from previous PfsSendResults

**Example:**
```text
REQUEST_TYPE=PfsGetTestResultData
DATABASE=PFSXXP4
USER_ID=pfs_user
PASSWORD=secret
PRODUCTION_ORDER=JOBONTHEFLOOR
SERIAL_NUMBER=ABC1234
SRC_OPERATION_CODE=FCT_1
RETURN_VALUES=5_VOLT_MEASUREMENT;TEST_TIME_SECONDS

```

## 18. Implementation Patterns and Best Practices

This section documents proven patterns from production implementations in Python, C#, and Perl.

### Connection and Retry Strategy

**Pattern: Exponential backoff with retry limit**

```python
communicationAttempts = 0
communicationSuccessful = False
while not communicationSuccessful:
    communicationAttempts += 1
    try:
        connectionAttempts = 0
        connectionSuccessful = False
        while not connectionSuccessful:
            connectionAttempts += 1
            if connectionAttempts > 2:
                raise ConnectionError()
            try:
                socket = ssl_connect(host, port, timeout=60)
                connectionSuccessful = True
            except SocketError:
                time.sleep(2)  # backoff before retry
        # send and receive
        communicationSuccessful = True
    except Exception:
        if communicationAttempts > 2:
            raise
        time.sleep(2)
```

**Recommendations:**
- **Connection retries**: 2-3 attempts before failing
- **Communication retries**: 2-3 attempts before failing
- **Backoff delay**: 2-5 seconds between retries
- **Timeout**: Minimum 30 seconds for full request-response cycle (connection + I/O)
- **One connection per request**: Establish fresh connection for each request, close after receiving response

### Exception Handling and Response Classification

**Pattern: Custom exception classes for each response type**

```python
class PfsErrorException(Exception):     # Unexpected server error
    pass

class PfsFailureException(Exception):   # Operation failed (expected condition)
    pass

class PfsWarningException(Exception):   # Operation succeeded with warnings
    pass

# Usage:
if response.startswith('OK'):
    return True
elif 'Error:' in response:
    raise PfsErrorException(response)
elif 'Failure:' in response:
    raise PfsFailureException(response)
elif 'Warning:' in response:
    raise PfsWarningException(response)
```

**Response parsing rules:**
1. Read entire response first
2. Check first line for response class: OK, Error, Failure, or Warning
3. For OK responses: Parse data lines (each parameter=value)
4. For non-OK responses: Treat entire response as error message
5. Never assume response structure; always validate before parsing

**Operator guidance by response class:**
- **OK**: Continue processing
- **Warning** (e.g., MULTIPLE_PO): Ask operator to confirm, allow override
- **Failure** (e.g., invalid serial): Board cannot be tested at this op, prompt for next board
- **Error**: Unrecoverable condition, exit test station software with diagnostics

### Safe Retry Logic for PfsSendResults

**Pattern: Ignore Failure on retry if board passed query**

```python
if requestType == 'PfsSendResults' and communicationAttempts > 1:
    if response.find('Failure:') != -1:
        # Assume results were received on first attempt,
        # treat retry failure as safe (results already recorded)
        response = 'OK'
```

**When safe to retry PfsSendResults:**
- Board passed initial PfsQuery at this operation
- First attempt to PfsSendResults may have succeeded despite timeout
- Treating second failure as OK is safe if results will be de-duped server-side

**When NOT safe to retry:**
- If you never called PfsQuery before PfsSendResults (no proof of validity)
- Remove this logic in that case

### TLS 1.2 Configuration Across Languages

**Python example:**
```python
import ssl
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pfsSocket = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_2)
pfsSocket.connect((host, port))
pfsSocket.settimeout(60)  # timeout in seconds
```

**C# example:**
```csharp
TcpClient tcpClient = new TcpClient(server, 50000);
SslStream clientStream = new SslStream(tcpClient.GetStream(), false, 
    ValidateServerCertificate, null);
clientStream.AuthenticateAsClient(
    serverCertificateName, 
    null, 
    SslProtocols.Tls12, 
    false);
```

**Perl example:**
```perl
my $socket = new IO::Socket::SSL(
    PeerAddr        => $host,
    PeerPort        => 50000,
    Proto           => 'tcp',
    Timeout         => 5,
    SSL_version     => 'TLSv12',
    SSL_verify_mode => SSL_VERIFY_NONE,
);
```

**Critical:**
- Explicit TLS 1.2 specification required (not "auto-negotiate" with older versions)
- Certificate validation: Either validate against trusted root or explicitly skip (as shown above for internal networks)
- Perl caveat: Requires IO::Socket::SSL 1.956+ and Net::SSLeay 1.59+ for TLS 1.2 support

### Configuration Management Pattern

**Recommended INI file structure:**
```ini
[PFS]
Server=pfs-gw-thp4.corp.bench.com
Database=PFSTHP4
CertificateServerName=testlink.bench.com
Timeout=60
ConnectionRetries=2
CommunicationRetries=2
BackoffDelaySeconds=2

[Station]
WorkCenter=E07102
OperationCodes=F_PACK,T_FCT

[Credentials]
; Prompt operator at runtime rather than storing in config
```

**Pre-populate request dictionary from config:**
```python
requestData = {}
if config.has('PFS', 'Database'):
    requestData['DATABASE'] = config.get('PFS', 'Database')
if config.has('Station', 'WorkCenter'):
    requestData['WORK_CENTER'] = config.get('Station', 'WorkCenter')
# Operator inputs (USER_ID, PASSWORD, SERIAL_NUMBER, etc.) filled at runtime
```

### Request Data Management

**Pattern: Dictionary with inheritance from defaults**

```python
# Initialize request with static config values
requestData = {'DATABASE': 'PFSXXP4', 'WORK_CENTER': 'E07102'}

# Add method-specific defaults
def pfs_query(request_dict):
    request_dict['REQUEST_TYPE'] = 'PfsQuery'
    request_dict['OPERATION_CODE'] = 'FCT_1'  # default
    send_request(request_dict)

# Allow callers to override
my_request = {'DATABASE': 'PFSXXP4', 'SERIAL_NUMBER': 'ABC1234'}
pfs_query(my_request)  # REQUEST_TYPE and OPERATION_CODE auto-filled
```

### Line-Ending and Text I/O Patterns

**Pattern: Use binary I/O with explicit line-end conversion**

**Python (makefile binary mode):**
```python
pfsSocketFile = pfsSocket.makefile('rwb', 0)  # binary mode
pfsSocketFile.write(str.encode(request_string))
pfsSocketFile.flush()
line = pfsSocketFile.readline().decode("utf-8").rstrip('\r\n')
```

**C# (StreamWriter with AutoFlush):**
```csharp
StreamWriter clientSocketStreamWriter = new StreamWriter(clientStream) { 
    AutoFlush = true 
};
clientSocketStreamWriter.Write(request);
clientSocketStreamWriter.WriteLine();  // Extra blank line

StreamReader clientSocketStreamReader = new StreamReader(clientStream);
string line;
while ((line = clientSocketStreamReader.ReadLine()) != "")
{
    response.AppendLine(line);
}
```

**Perl (with manual CRLF conversion):**
```perl
$request =~ s/\n*$/ \n\n/;      # Ensure two trailing newlines
$request =~ s/\n/$CRLF/g;           # Convert all LF to CRLF

print $socket $request;

local ($/) = $LF;  # Read lines ending with LF
while (<$socket>) {
    s/$CR?$LF/\n/;  # Normalize line endings
    $response .= $_;
}
```

**Critical points:**
- Request must end with blank line (two consecutive line breaks: `\r\n\r\n`)
- Read lines until you receive a blank line (empty string after rstrip)
- Convert platform-specific line endings to LF for internal use
- Always use CRLF on the wire

### Socket Lifecycle and Resource Cleanup

**Pattern: Try-finally with explicit cleanup**

**Python:**
```python
pfsSocket = None
pfsSocketFile = None
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pfsSocket = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_2)
    pfsSocket.connect((host, port))
    pfsSocketFile = pfsSocket.makefile('rwb')
    # send and receive
finally:
    if pfsSocketFile is not None:
        pfsSocketFile.close()
        pfsSocketFile = None
    if pfsSocket is not None:
        pfsSocket.close()
        pfsSocket = None
```

**C#:**
```csharp
TcpClient tcpClient = null;
Stream clientSocketStream = null;
StreamReader clientSocketStreamReader = null;
StreamWriter clientSocketStreamWriter = null;
try {
    tcpClient = new TcpClient(Server, 50000);
    clientSocketStream = new SslStream(tcpClient.GetStream(), ...);
    (clientSocketStream as SslStream).AuthenticateAsClient(...);
    // send and receive
finally {
    if (clientSocketStreamWriter != null) clientSocketStreamWriter.Close();
    if (clientSocketStreamReader != null) clientSocketStreamReader.Close();
    if (clientSocketStream != null) clientSocketStream.Close();
    if (tcpClient != null) tcpClient.Close();
}
```

**Critical points:**
- Initialize socket references to null before try block
- Check for null before closing in finally (avoids double-close exceptions)
- Close in reverse order of opening (StreamWriter → StreamReader → Stream → Socket)
- Use try-finally (or using-statements in C#) unconditionally

### Operator UI Flow Pattern

**Recommended workflow:**

```
┌─ STARTUP ─────────────────────────────────────────┐
│ 1. Load config from INI file                       │
│ 2. Prompt operator:                                │
│    - USER_ID (required)                            │
│    - PASSWORD (required)                           │
│    - PRODUCTION_ORDER (required)                   │
│    - OPERATION_CODE (menu selection or custom)     │
│ 3. Call PfsVerifyUserInput                         │
└────────────────────────────────────────────────────┘
           ↓ (success)
┌─ PER-BOARD LOOP ──────────────────────────────────┐
│ 1. Prompt operator for SERIAL_NUMBER               │
│ 2. Call PfsQuery                                   │
│    → OK: continue to test                          │
│    → Failure: show error, prompt next board        │
│    → Warning: ask operator to confirm              │
│ 3. Run test (harness-specific)                     │
│ 4. Call PfsSendResults with PASS_FAIL              │
│    → OK: continue to next board                    │
│    → Failure: show error, prompt next board        │
│ 5. Loop for next board (empty SERIAL_NUMBER exits) │
└────────────────────────────────────────────────────┘
```

**Operator prompts by response type:**
- **Query Failure** "This board cannot be tested at this operation. Press [Enter] for next board"
- **Query Warning** "Warning: [message]. Continue? [y/n]"
- **SendResults Failure** "Results not recorded. Press [Enter] for next board"
- **Error (any method)** "Fatal error: [message]. Contact engineer. Press [Enter] to exit"

### Flexible Request Input Pattern

**Pattern: Accept both string and dictionary formats**

**Perl example:**
```perl
sub pfs_send_request {
    my ($requestData) = @_;
    my $request;
    
    if (ref($requestData)) {
        # Hash reference: convert to string
        $request = join("\n", map {"$_=$requestData->{$_}"} keys %{$requestData});
    } else {
        # String: use as-is
        $request = $requestData;
    }
    
    # Normalize line endings
    $request =~ s/\n*$/ \n\n/;      # Trailing newlines
    $request =~ s/\n/$CRLF/g;        # LF to CRLF
    # ... send request
}
```

**Benefits:**
- Callers can pre-format complex requests manually
- Or use simpler dictionary syntax for straightforward calls
- Same function handles both cases

### Response Data Extraction

**Pattern: Parse name=value pairs from OK response**

```python
if response.startswith('OK'):
    lines = response.split('\n')[1:]  # Skip 'OK' line
    result = {}
    for line in lines:
        if '=' in line:
            key, value = line.split('=', 1)
            result[key.strip()] = value.strip()
    return result
```

**For delimited list returns:**
```python
# If RETURN_VALUES=ITEM_NUMBER;COMP_SERIAL_NUMBER;QUANTITY
# Response might be:
# OK\n
# ITEM_NUMBER;COMP_SERIAL_NUMBER;QUANTITY\n
# ITEM_ABC;SN123;5\n

# Parse as:
lines = [l for l in response.split('\n')[1:] if l]
if len(lines) >= 2:
    headers = lines[0].split(';')
    for row in lines[1:]:
        values = row.split(';')
        result_dict = dict(zip(headers, values))
```

### Logging and Diagnostics

**Pattern: Capture full request and response for debugging**

```python
import logging

logger = logging.getLogger('PfsClient')

def send_request(request_dict):
    try:
        logger.debug(f'Sending: {request_dict}')
        response = _socket_io()
        logger.info(f'Response: {response[:100]}')
        return response
    except Exception as e:
        logger.error(f'PFS Error: {str(e)}')
        logger.debug(f'Failed request: {request_dict}')
        raise
```

**What to log:**
- REQUEST_TYPE and key parameters (not PASSWORD)
- First 100 chars of response
- Connection attempt counts
- Retry backoff delays
- Full errors to diagnostics log

### Performance Considerations

**Caching strategy:**
- **Never cache** PfsQuery results (serial numbers are one-time)  
- **Cache for session** PfsGetOperationCodes, PfsGetDefectCodes (change rarely, ~hourly)
- **Cache indefinitely** PfsGetBomItems, PfsGetItemInfo (static reference data)

**Timeout tuning:**
- Default timeout of 30-60 seconds works for most operations
- PfsGetSnHistory with many records may need 90+ seconds
- Reduce to 10-15 seconds only for LAN-only test stations

**Connection reuse:**
- Do NOT reuse connections across requests
- Each request gets fresh connection (reduces state-related bugs)
- Automatic connection pooling not recommended (adds complexity)

### Multi-Language Implementation Checklist

**Before deploying to production, verify:**

- [ ] TLS 1.2 explicitly configured (not auto-negotiate)
- [ ] Certificate validation configured (custom callback or system store)
- [ ] Connection retries with backoff implemented (2-3 attempts)
- [ ] Timeout configured (30-60 seconds)
- [ ] Exception classes defined for Error/Failure/Warning
- [ ] Socket lifecycle has try-finally for cleanup
- [ ] Request ends with blank line (`\r\n\r\n`)
- [ ] Response parsing reads until blank line
- [ ] Line endings normalized (platform-independent)
- [ ] PfsVerifyUserInput called before PfsQuery
- [ ] PfsQuery called before each PfsSendResults
- [ ] Operator given appropriate feedback by response class
- [ ] Configuration loaded from INI or environment
- [ ] Credentials NOT logged or stored
- [ ] DATABASE, OPERATION_CODE, WORK_CENTER pre-populated from config
- [ ] SERIAL_NUMBER, USER_ID, PASSWORD prompted at runtime
- [ ] Full request/response logged for debugging
- [ ] Empty socket response treated as error (not success)
- [ ] Response starts with OK validated before parsing data

