"""
NetSuite MCP Server for FinClose AI
Provides tools for AI agents to interact with NetSuite ERP system
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import requests
from requests_oauthlib import OAuth1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration and Authentication
# ============================================================================

class NetSuiteConfig(BaseModel):
    """NetSuite connection configuration"""
    account_id: str = Field(..., description="NetSuite account ID")
    consumer_key: str = Field(..., description="OAuth consumer key")
    consumer_secret: str = Field(..., description="OAuth consumer secret")
    token_id: str = Field(..., description="OAuth token ID")
    token_secret: str = Field(..., description="OAuth token secret")
    rest_url: str = Field(..., description="NetSuite REST API base URL")


class NetSuiteClient:
    """NetSuite API client with OAuth 1.0 authentication"""
    
    def __init__(self, config: NetSuiteConfig):
        self.config = config
        self.base_url = config.rest_url
        self.oauth = OAuth1(
            client_key=config.consumer_key,
            client_secret=config.consumer_secret,
            resource_owner_key=config.token_id,
            resource_owner_secret=config.token_secret,
            realm=config.account_id,
            signature_method='HMAC-SHA256'
        )
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to NetSuite API"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.oauth,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"NetSuite API request failed: {str(e)}")
            raise
    
    def suiteql_query(self, query: str, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Execute SuiteQL query"""
        endpoint = "/services/rest/query/v1/suiteql"
        params = {
            'limit': limit,
            'offset': offset
        }
        response = self._make_request('POST', endpoint, json={'q': query}, params=params)
        return response.get('items', [])
    
    def get_record(self, record_type: str, record_id: int) -> Dict[str, Any]:
        """Get a single record by ID"""
        endpoint = f"/services/rest/record/v1/{record_type}/{record_id}"
        return self._make_request('GET', endpoint)
    
    def create_record(self, record_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        endpoint = f"/services/rest/record/v1/{record_type}"
        return self._make_request('POST', endpoint, json=data)
    
    def update_record(self, record_type: str, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record"""
        endpoint = f"/services/rest/record/v1/{record_type}/{record_id}"
        return self._make_request('PATCH', endpoint, json=data)


# ============================================================================
# Pydantic Models for Tool Inputs
# ============================================================================

class RecordType(str, Enum):
    """Supported NetSuite record types"""
    JOURNAL_ENTRY = "journalentry"
    VENDOR_BILL = "vendorbill"
    EMPLOYEE = "employee"
    ACCOUNT = "account"
    VENDOR = "vendor"
    DEPARTMENT = "department"
    CLASS_RECORD = "classification"
    LOCATION = "location"
    SUBSIDIARY = "subsidiary"


class JournalEntryLine(BaseModel):
    """Journal entry line item"""
    account: int = Field(..., description="Account internal ID")
    debit: Optional[float] = Field(None, description="Debit amount")
    credit: Optional[float] = Field(None, description="Credit amount")
    department: Optional[int] = Field(None, description="Department internal ID")
    class_id: Optional[int] = Field(None, description="Class internal ID", alias="class")
    location: Optional[int] = Field(None, description="Location internal ID")
    memo: Optional[str] = Field(None, description="Line memo")
    entity: Optional[int] = Field(None, description="Entity (vendor/employee) internal ID")


class CreateJournalEntryInput(BaseModel):
    """Input for creating a journal entry"""
    subsidiary: int = Field(..., description="Subsidiary internal ID")
    trandate: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    memo: Optional[str] = Field(None, description="Journal entry memo")
    lines: List[JournalEntryLine] = Field(..., description="Journal entry lines")
    approved: bool = Field(False, description="Whether to mark as approved")


class SearchBillsInput(BaseModel):
    """Input for searching vendor bills"""
    subsidiary: Optional[int] = Field(None, description="Filter by subsidiary ID")
    vendor: Optional[int] = Field(None, description="Filter by vendor ID")
    date_from: Optional[str] = Field(None, description="Start date YYYY-MM-DD")
    date_to: Optional[str] = Field(None, description="End date YYYY-MM-DD")
    status: Optional[str] = Field(None, description="Bill status (e.g., 'Open', 'Paid Open')")
    limit: int = Field(100, description="Maximum number of results")


class GetJournalEntriesInput(BaseModel):
    """Input for retrieving journal entries"""
    subsidiary: Optional[int] = Field(None, description="Filter by subsidiary ID")
    account: Optional[int] = Field(None, description="Filter by account ID")
    date_from: str = Field(..., description="Start date YYYY-MM-DD")
    date_to: str = Field(..., description="End date YYYY-MM-DD")
    department: Optional[int] = Field(None, description="Filter by department ID")
    limit: int = Field(500, description="Maximum number of results")


class GetEmployeeDimensionsInput(BaseModel):
    """Input for getting employee dimension mapping"""
    active_only: bool = Field(True, description="Only return active employees")
    subsidiary: Optional[int] = Field(None, description="Filter by subsidiary")


class SuiteQLQueryInput(BaseModel):
    """Input for executing SuiteQL queries"""
    query: str = Field(..., description="SuiteQL query string")
    limit: int = Field(1000, description="Maximum number of results (1-1000)")
    offset: int = Field(0, description="Offset for pagination")


# ============================================================================
# Initialize MCP Server
# ============================================================================

# Initialize FastMCP server
mcp = FastMCP("netsuite-server")

# Initialize NetSuite client (will be configured from environment)
netsuite_client: Optional[NetSuiteClient] = None


def get_client() -> NetSuiteClient:
    """Get or create NetSuite client"""
    global netsuite_client
    if netsuite_client is None:
        config = NetSuiteConfig(
            account_id=os.getenv("NETSUITE_ACCOUNT_ID", ""),
            consumer_key=os.getenv("NETSUITE_CONSUMER_KEY", ""),
            consumer_secret=os.getenv("NETSUITE_CONSUMER_SECRET", ""),
            token_id=os.getenv("NETSUITE_TOKEN_ID", ""),
            token_secret=os.getenv("NETSUITE_TOKEN_SECRET", ""),
            rest_url=os.getenv("NETSUITE_REST_URL", "")
        )
        netsuite_client = NetSuiteClient(config)
    return netsuite_client


# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool()
def netsuite_suiteql_query(input: SuiteQLQueryInput) -> str:
    """
    Execute a SuiteQL query against NetSuite.
    
    SuiteQL is NetSuite's SQL-like query language. Use this for complex data retrieval.
    
    Example queries:
    - Get accounts: SELECT id, accountnumber, accountname FROM account WHERE isinactive = 'F'
    - Get vendors: SELECT id, entityid, companyname FROM vendor WHERE isinactive = 'F'
    - Get bills: SELECT id, tranid, entity, amount FROM transaction WHERE type = 'VendBill'
    
    Returns JSON array of results.
    """
    try:
        client = get_client()
        results = client.suiteql_query(
            query=input.query,
            limit=input.limit,
            offset=input.offset
        )
        return json.dumps({
            "success": True,
            "count": len(results),
            "results": results
        }, indent=2)
    except Exception as e:
        logger.error(f"SuiteQL query failed: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def netsuite_get_record(record_type: RecordType, record_id: int) -> str:
    """
    Get a single NetSuite record by type and internal ID.
    
    Supported record types:
    - journalentry: Journal entries
    - vendorbill: Vendor bills
    - employee: Employee records
    - account: Chart of accounts
    - vendor: Vendor master
    - department: Department list
    - classification: Class list
    - location: Location list
    - subsidiary: Subsidiary list
    
    Returns complete record details in JSON format.
    """
    try:
        client = get_client()
        record = client.get_record(record_type.value, record_id)
        return json.dumps({
            "success": True,
            "record_type": record_type.value,
            "record_id": record_id,
            "data": record
        }, indent=2)
    except Exception as e:
        logger.error(f"Get record failed: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def netsuite_create_journal_entry(input: CreateJournalEntryInput) -> str:
    """
    Create a new journal entry in NetSuite.
    
    Journal entries must balance (total debits = total credits).
    Required dimensions: Account, Department, Class, Location (per Gusto requirements).
    
    The journal entry will be created in "Pending Approval" status unless approved=True.
    
    Returns the created journal entry ID and details.
    """
    try:
        client = get_client()
        
        # Validate that entry balances
        total_debit = sum(line.debit or 0 for line in input.lines)
        total_credit = sum(line.credit or 0 for line in input.lines)
        
        if abs(total_debit - total_credit) > 0.01:
            return json.dumps({
                "success": False,
                "error": f"Journal entry does not balance. Debits: {total_debit}, Credits: {total_credit}"
            }, indent=2)
        
        # Prepare journal entry data
        je_data = {
            "subsidiary": {"id": input.subsidiary},
            "trandate": input.trandate,
            "memo": input.memo,
            "approved": input.approved,
            "line": {
                "items": [
                    {
                        "account": {"id": line.account},
                        "debit": line.debit,
                        "credit": line.credit,
                        "department": {"id": line.department} if line.department else None,
                        "class": {"id": line.class_id} if line.class_id else None,
                        "location": {"id": line.location} if line.location else None,
                        "memo": line.memo,
                        "entity": {"id": line.entity} if line.entity else None
                    }
                    for line in input.lines
                ]
            }
        }
        
        result = client.create_record("journalentry", je_data)
        
        return json.dumps({
            "success": True,
            "journal_entry_id": result.get("id"),
            "tranid": result.get("tranid"),
            "message": "Journal entry created successfully",
            "data": result
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Create journal entry failed: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def netsuite_get_pending_bills(input: SearchBillsInput) -> str:
    """
    Search for pending vendor bills in NetSuite.
    
    Use this to find bills that need accrual processing. Typically used for ZIP accrual workflow
    to identify invoices that have been entered but not yet posted or paid.
    
    Returns list of bills with vendor, amount, date, and status information.
    """
    try:
        client = get_client()
        
        # Build SuiteQL query
        query_parts = [
            "SELECT t.id, t.tranid, t.trandate, t.duedate, t.status,",
            "v.entityid as vendor_name, v.id as vendor_id,",
            "t.amount, t.foreignamount, t.currency,",
            "t.memo, s.name as subsidiary",
            "FROM transaction t",
            "INNER JOIN vendor v ON t.entity = v.id",
            "LEFT JOIN subsidiary s ON t.subsidiary = s.id",
            "WHERE t.type = 'VendBill'"
        ]
        
        conditions = []
        if input.subsidiary:
            conditions.append(f"t.subsidiary = {input.subsidiary}")
        if input.vendor:
            conditions.append(f"t.entity = {input.vendor}")
        if input.date_from:
            conditions.append(f"t.trandate >= '{input.date_from}'")
        if input.date_to:
            conditions.append(f"t.trandate <= '{input.date_to}'")
        if input.status:
            conditions.append(f"t.status = '{input.status}'")
        
        if conditions:
            query_parts.append("AND " + " AND ".join(conditions))
        
        query_parts.append(f"ORDER BY t.trandate DESC LIMIT {input.limit}")
        query = " ".join(query_parts)
        
        results = client.suiteql_query(query, limit=input.limit)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "bills": results
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Get pending bills failed: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def netsuite_get_journal_entries(input: GetJournalEntriesInput) -> str:
    """
    Retrieve journal entries for a specific period.
    
    Use this for payroll reconciliation to get posted journal entries that need to be
    compared against Workday data. Can filter by date range, account, department, etc.
    
    Returns detailed journal entry information including line items and dimensions.
    """
    try:
        client = get_client()
        
        # Build SuiteQL query for journal entries
        query_parts = [
            "SELECT t.id, t.tranid, t.trandate, t.memo as header_memo,",
            "tl.account, a.accountname, tl.debit, tl.credit,",
            "tl.department, d.name as department_name,",
            "tl.class, c.name as class_name,",
            "tl.location, l.name as location_name,",
            "tl.memo as line_memo, tl.entity,",
            "s.name as subsidiary",
            "FROM transaction t",
            "INNER JOIN transactionline tl ON t.id = tl.transaction",
            "INNER JOIN account a ON tl.account = a.id",
            "LEFT JOIN department d ON tl.department = d.id",
            "LEFT JOIN classification c ON tl.class = c.id",
            "LEFT JOIN location l ON tl.location = l.id",
            "LEFT JOIN subsidiary s ON t.subsidiary = s.id",
            "WHERE t.type = 'Journal'"
        ]
        
        conditions = [
            f"t.trandate >= '{input.date_from}'",
            f"t.trandate <= '{input.date_to}'"
        ]
        
        if input.subsidiary:
            conditions.append(f"t.subsidiary = {input.subsidiary}")
        if input.account:
            conditions.append(f"tl.account = {input.account}")
        if input.department:
            conditions.append(f"tl.department = {input.department}")
        
        query_parts.append("AND " + " AND ".join(conditions))
        query_parts.append(f"ORDER BY t.trandate, t.id LIMIT {input.limit}")
        query = " ".join(query_parts)
        
        results = client.suiteql_query(query, limit=input.limit)
        
        # Group by transaction
        entries = {}
        for row in results:
            je_id = row['id']
            if je_id not in entries:
                entries[je_id] = {
                    'id': je_id,
                    'tranid': row['tranid'],
                    'trandate': row['trandate'],
                    'memo': row['header_memo'],
                    'subsidiary': row['subsidiary'],
                    'lines': []
                }
            entries[je_id]['lines'].append({
                'account': row['account'],
                'account_name': row['accountname'],
                'debit': row['debit'],
                'credit': row['credit'],
                'department': row['department'],
                'department_name': row['department_name'],
                'class': row['class'],
                'class_name': row['class_name'],
                'location': row['location'],
                'location_name': row['location_name'],
                'memo': row['line_memo'],
                'entity': row['entity']
            })
        
        return json.dumps({
            "success": True,
            "count": len(entries),
            "journal_entries": list(entries.values())
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Get journal entries failed: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def netsuite_get_employee_dimensions(input: GetEmployeeDimensionsInput) -> str:
    """
    Get employee dimension mapping (subsidiary, department, class, location).
    
    Use this for equity transaction processing to map ShareWorks employee IDs to
    NetSuite dimensions required for journal entries.
    
    Returns employee ID, name, and all dimension assignments.
    """
    try:
        client = get_client()
        
        # Build SuiteQL query
        query_parts = [
            "SELECT e.id, e.entityid as employee_id, e.firstname, e.lastname,",
            "e.subsidiary, s.name as subsidiary_name,",
            "e.department, d.name as department_name,",
            "e.class, c.name as class_name,",
            "e.location, l.name as location_name,",
            "e.isinactive",
            "FROM employee e",
            "LEFT JOIN subsidiary s ON e.subsidiary = s.id",
            "LEFT JOIN department d ON e.department = d.id",
            "LEFT JOIN classification c ON e.class = c.id",
            "LEFT JOIN location l ON e.location = l.id"
        ]
        
        conditions = []
        if input.active_only:
            conditions.append("e.isinactive = 'F'")
        if input.subsidiary:
            conditions.append(f"e.subsidiary = {input.subsidiary}")
        
        if conditions:
            query_parts.append("WHERE " + " AND ".join(conditions))
        
        query_parts.append("ORDER BY e.entityid")
        query = " ".join(query_parts)
        
        results = client.suiteql_query(query, limit=5000)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "employees": results
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Get employee dimensions failed: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def netsuite_get_chart_of_accounts() -> str:
    """
    Get the complete chart of accounts from NetSuite.
    
    Returns all active accounts with account number, name, type, and whether they are
    balance sheet or income statement accounts. Useful for validation and mapping.
    """
    try:
        client = get_client()
        
        query = """
        SELECT id, accountnumber, accountname, accttype, 
               accountsearchdisplayname, isinactive,
               CASE 
                   WHEN accttype IN ('Bank', 'Accounts Receivable', 'Other Current Asset', 
                                     'Fixed Asset', 'Other Asset', 'Accounts Payable', 
                                     'Credit Card', 'Other Current Liability', 
                                     'Long Term Liability', 'Equity') THEN 'Balance Sheet'
                   WHEN accttype IN ('Income', 'Cost of Goods Sold', 'Expense', 
                                     'Other Income', 'Other Expense') THEN 'Income Statement'
                   ELSE 'Other'
               END as statement_type
        FROM account
        WHERE isinactive = 'F'
        ORDER BY accountnumber
        """
        
        results = client.suiteql_query(query, limit=5000)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "accounts": results
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Get chart of accounts failed: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def netsuite_post_journal_entry(journal_entry_id: int) -> str:
    """
    Post (approve) a journal entry that is in pending status.
    
    Use this after human approval to finalize and post journal entries to the general ledger.
    This is a destructive operation that cannot be easily undone.
    
    Returns success status and posted journal entry details.
    """
    try:
        client = get_client()
        
        # Update the journal entry to approved status
        update_data = {
            "approved": True
        }
        
        result = client.update_record("journalentry", journal_entry_id, update_data)
        
        return json.dumps({
            "success": True,
            "journal_entry_id": journal_entry_id,
            "message": "Journal entry posted successfully",
            "data": result
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Post journal entry failed: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


# ============================================================================
# MCP Resources
# ============================================================================

@mcp.resource("netsuite://accounts")
def get_accounts_resource() -> str:
    """Chart of Accounts - All active accounts"""
    try:
        result = netsuite_get_chart_of_accounts()
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("netsuite://vendors")
def get_vendors_resource() -> str:
    """Vendor Master - All active vendors"""
    try:
        client = get_client()
        query = """
        SELECT id, entityid, companyname, email, phone, 
               isinactive, balance
        FROM vendor
        WHERE isinactive = 'F'
        ORDER BY companyname
        """
        results = client.suiteql_query(query, limit=5000)
        return json.dumps({"success": True, "count": len(results), "vendors": results}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("netsuite://employees")
def get_employees_resource() -> str:
    """Employee Dimensions - All active employees with dimension mapping"""
    try:
        input_data = GetEmployeeDimensionsInput(active_only=True)
        result = netsuite_get_employee_dimensions(input_data)
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
