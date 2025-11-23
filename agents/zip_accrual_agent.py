"""
ZIP Accrual Agent for FinClose AI
Automates the ZIP invoice accrual process with AI-powered service period identification
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from calendar import monthrange

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

import sys
sys.path.append('..')
from shared.models import (
    ZIPAccrualState, JournalEntry, JournalEntryLine,
    ApprovalRequest, WorkflowStatus, generate_request_id
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ZIP Accrual Agent
# ============================================================================

class ZIPAccrualAgent:
    """
    Agent for automating ZIP invoice accrual processing
    
    Workflow:
    1. Extract pending invoices from ZIP (Google Drive)
    2. Fetch existing NetSuite bills
    3. Use AI to identify service periods from descriptions
    4. Calculate day-by-day prorated accruals
    5. Generate journal entries
    6. Return for approval/posting
    """
    
    def __init__(self, llm_model: str = "claude-3-5-sonnet-20241022"):
        self.llm = ChatAnthropic(model=llm_model, temperature=0)
        self.graph = None
        self.checkpointer = MemorySaver()
        
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(ZIPAccrualState)
        
        # Add nodes
        workflow.add_node("extract_zip_data", self.extract_zip_data)
        workflow.add_node("fetch_netsuite_bills", self.fetch_netsuite_bills)
        workflow.add_node("identify_service_periods", self.identify_service_periods)
        workflow.add_node("calculate_accruals", self.calculate_accruals)
        workflow.add_node("generate_journal_entries", self.generate_journal_entries)
        workflow.add_node("validate_entries", self.validate_entries)
        workflow.add_node("create_approval_request", self.create_approval_request)
        
        # Define edges
        workflow.set_entry_point("extract_zip_data")
        workflow.add_edge("extract_zip_data", "fetch_netsuite_bills")
        workflow.add_edge("fetch_netsuite_bills", "identify_service_periods")
        workflow.add_edge("identify_service_periods", "calculate_accruals")
        workflow.add_edge("calculate_accruals", "generate_journal_entries")
        workflow.add_edge("generate_journal_entries", "validate_entries")
        workflow.add_edge("validate_entries", "create_approval_request")
        workflow.add_edge("create_approval_request", END)
        
        self.graph = workflow.compile(checkpointer=self.checkpointer)
        return self.graph
    
    def extract_zip_data(self, state: ZIPAccrualState) -> ZIPAccrualState:
        """Extract pending invoices from ZIP system"""
        logger.info("Extracting ZIP pending invoices...")
        
        try:
            # In production, this would call Google Drive API to fetch ZIP exports
            # For now, we'll simulate the data structure
            
            # Example: Read from Google Drive CSV export
            # zip_file_path = state["metadata"].get("zip_file_path")
            # zip_invoices = self._read_zip_file(zip_file_path)
            
            # Simulated data structure
            zip_invoices = [
                {
                    "invoice_id": "INV-001",
                    "vendor": "Acme Software Inc",
                    "vendor_id": 1234,
                    "amount": 12000.0,
                    "invoice_date": "2025-11-15",
                    "description": "Software subscription service for December 2025",
                    "account": 6100,
                    "department": 10,
                    "class": 5,
                    "location": 1,
                    "status": "Pending"
                },
                {
                    "invoice_id": "INV-002",
                    "vendor": "Legal Services LLC",
                    "vendor_id": 5678,
                    "amount": 25000.0,
                    "invoice_date": "2025-11-20",
                    "description": "Legal services rendered October 15 - November 30, 2025",
                    "account": 6200,
                    "department": 15,
                    "class": 5,
                    "location": 1,
                    "status": "Pending"
                }
            ]
            
            state["zip_invoices"] = zip_invoices
            state["status"] = WorkflowStatus.IN_PROGRESS
            state["messages"].append({
                "role": "system",
                "content": f"Extracted {len(zip_invoices)} pending invoices from ZIP"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to extract ZIP data: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def fetch_netsuite_bills(self, state: ZIPAccrualState) -> ZIPAccrualState:
        """Fetch existing NetSuite bills to check for duplicates"""
        logger.info("Fetching NetSuite bills...")
        
        try:
            # In production, this would call NetSuite MCP server
            # For now, we'll simulate
            
            # Example MCP call:
            # from mcp_client import call_tool
            # result = call_tool("netsuite_get_pending_bills", {
            #     "date_from": "2025-11-01",
            #     "date_to": "2025-11-30",
            #     "status": "Pending Approval"
            # })
            
            netsuite_bills = []
            
            state["netsuite_bills"] = netsuite_bills
            state["messages"].append({
                "role": "system",
                "content": f"Fetched {len(netsuite_bills)} existing bills from NetSuite"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to fetch NetSuite bills: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def identify_service_periods(self, state: ZIPAccrualState) -> ZIPAccrualState:
        """Use AI to identify service periods from invoice descriptions"""
        logger.info("Identifying service periods with AI...")
        
        try:
            invoices_with_periods = []
            
            for invoice in state["zip_invoices"]:
                # Use LLM to extract service period
                prompt = f"""
                Analyze this invoice description and identify the service period:
                
                Invoice: {invoice['invoice_id']}
                Vendor: {invoice['vendor']}
                Amount: ${invoice['amount']:,.2f}
                Date: {invoice['invoice_date']}
                Description: {invoice['description']}
                
                Extract the service period and return in JSON format:
                {{
                    "service_start_date": "YYYY-MM-DD",
                    "service_end_date": "YYYY-MM-DD",
                    "confidence": "high|medium|low",
                    "reasoning": "brief explanation"
                }}
                
                Rules:
                - If description mentions a future month, that's the service period
                - If description mentions a date range, use that
                - If no period mentioned and amount < $200, assume current month
                - For recurring services, assume one month period
                """
                
                messages = [
                    SystemMessage(content="You are an expert at analyzing invoices and identifying service periods."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                
                # Parse LLM response
                try:
                    period_info = json.loads(response.content)
                except:
                    # Fallback if LLM doesn't return valid JSON
                    period_info = {
                        "service_start_date": invoice["invoice_date"],
                        "service_end_date": invoice["invoice_date"],
                        "confidence": "low",
                        "reasoning": "Could not parse service period from description"
                    }
                
                invoice["service_period"] = period_info
                invoices_with_periods.append(invoice)
            
            state["zip_invoices"] = invoices_with_periods
            state["messages"].append({
                "role": "assistant",
                "content": f"Identified service periods for {len(invoices_with_periods)} invoices"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to identify service periods: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def calculate_accruals(self, state: ZIPAccrualState) -> ZIPAccrualState:
        """Calculate day-by-day prorated accruals"""
        logger.info("Calculating prorated accruals...")
        
        try:
            close_date = datetime.strptime(
                state["metadata"].get("close_date", "2025-11-30"),
                "%Y-%m-%d"
            )
            
            accrual_calculations = []
            
            for invoice in state["zip_invoices"]:
                period = invoice["service_period"]
                start_date = datetime.strptime(period["service_start_date"], "%Y-%m-%d")
                end_date = datetime.strptime(period["service_end_date"], "%Y-%m-%d")
                
                # Calculate total service days
                total_days = (end_date - start_date).days + 1
                daily_rate = invoice["amount"] / total_days
                
                # Calculate days in current period (up to close date)
                if end_date <= close_date:
                    # Entire service period is in current month
                    accrual_days = total_days
                    accrual_amount = invoice["amount"]
                elif start_date > close_date:
                    # Entire service period is in future
                    accrual_days = 0
                    accrual_amount = 0.0
                else:
                    # Partial period in current month
                    accrual_days = (close_date - start_date).days + 1
                    accrual_amount = daily_rate * accrual_days
                
                calculation = {
                    "invoice_id": invoice["invoice_id"],
                    "vendor": invoice["vendor"],
                    "vendor_id": invoice["vendor_id"],
                    "total_amount": invoice["amount"],
                    "service_start": period["service_start_date"],
                    "service_end": period["service_end_date"],
                    "total_days": total_days,
                    "daily_rate": daily_rate,
                    "accrual_days": accrual_days,
                    "accrual_amount": round(accrual_amount, 2),
                    "account": invoice["account"],
                    "department": invoice["department"],
                    "class": invoice["class"],
                    "location": invoice["location"],
                    "confidence": period["confidence"]
                }
                
                accrual_calculations.append(calculation)
            
            state["accrual_calculations"] = accrual_calculations
            state["messages"].append({
                "role": "assistant",
                "content": f"Calculated accruals for {len(accrual_calculations)} invoices"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to calculate accruals: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def generate_journal_entries(self, state: ZIPAccrualState) -> ZIPAccrualState:
        """Generate journal entries for accruals"""
        logger.info("Generating journal entries...")
        
        try:
            close_date = state["metadata"].get("close_date", "2025-11-30")
            subsidiary = state["metadata"].get("subsidiary", 1)
            
            # Group accruals by account/department/class/location
            grouped = {}
            for calc in state["accrual_calculations"]:
                if calc["accrual_amount"] > 0:
                    key = (
                        calc["account"],
                        calc["department"],
                        calc["class"],
                        calc["location"]
                    )
                    if key not in grouped:
                        grouped[key] = {
                            "account": calc["account"],
                            "department": calc["department"],
                            "class": calc["class"],
                            "location": calc["location"],
                            "amount": 0.0,
                            "invoices": []
                        }
                    grouped[key]["amount"] += calc["accrual_amount"]
                    grouped[key]["invoices"].append(calc["invoice_id"])
            
            # Create journal entry
            lines = []
            
            # Debit lines (expense accounts)
            for key, data in grouped.items():
                lines.append(JournalEntryLine(
                    account=data["account"],
                    account_name=f"Account {data['account']}",  # Would lookup from COA
                    debit=data["amount"],
                    credit=0.0,
                    department=data["department"],
                    class_id=data["class"],
                    location=data["location"],
                    memo=f"Accrual for invoices: {', '.join(data['invoices'])}"
                ))
            
            # Credit line (accrued liabilities)
            total_accrual = sum(data["amount"] for data in grouped.values())
            lines.append(JournalEntryLine(
                account=2110,  # Accrued Liabilities
                account_name="Accrued Liabilities",
                debit=0.0,
                credit=total_accrual,
                department=None,
                class_id=None,
                location=None,
                memo="ZIP accrual entry"
            ))
            
            je = JournalEntry(
                subsidiary=subsidiary,
                subsidiary_name="Gusto US",
                trandate=close_date,
                memo=f"ZIP Accruals - {close_date}",
                lines=lines
            )
            
            # Validate balance
            if not je.validate_balance():
                raise ValueError(f"Journal entry does not balance: DR={je.total_debit}, CR={je.total_credit}")
            
            state["journal_entries"] = [je]
            state["messages"].append({
                "role": "assistant",
                "content": f"Generated journal entry with {len(lines)} lines, total amount: ${total_accrual:,.2f}"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to generate journal entries: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def validate_entries(self, state: ZIPAccrualState) -> ZIPAccrualState:
        """Validate journal entries"""
        logger.info("Validating journal entries...")
        
        try:
            validation_errors = []
            
            for je in state["journal_entries"]:
                # Check balance
                if not je.validate_balance():
                    validation_errors.append(
                        f"JE does not balance: DR={je.total_debit}, CR={je.total_credit}"
                    )
                
                # Check required fields
                for line in je.lines:
                    if not line.account:
                        validation_errors.append(f"Missing account on line")
                    if line.debit and line.credit:
                        validation_errors.append(f"Line has both debit and credit")
                    if not line.debit and not line.credit:
                        validation_errors.append(f"Line has no amount")
            
            if validation_errors:
                state["status"] = WorkflowStatus.ERROR
                state["error"] = "; ".join(validation_errors)
            else:
                state["messages"].append({
                    "role": "system",
                    "content": "All journal entries validated successfully"
                })
            
            return state
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def create_approval_request(self, state: ZIPAccrualState) -> ZIPAccrualState:
        """Create approval request for human review"""
        logger.info("Creating approval request...")
        
        try:
            approval_request = ApprovalRequest(
                request_id=generate_request_id(),
                workflow_type="zip_accrual",
                created_at=datetime.now(),
                data={
                    "close_date": state["metadata"].get("close_date"),
                    "invoice_count": len(state["zip_invoices"]),
                    "total_accrual": state["journal_entries"][0].total_debit if state["journal_entries"] else 0
                },
                variances=[],
                journal_entries=state["journal_entries"]
            )
            
            state["approval_request"] = approval_request
            state["status"] = WorkflowStatus.AWAITING_APPROVAL
            state["messages"].append({
                "role": "system",
                "content": f"Approval request created: {approval_request.request_id}"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to create approval request: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def run(self, inputs: Dict[str, Any]) -> ZIPAccrualState:
        """Execute the ZIP accrual workflow"""
        logger.info("Starting ZIP Accrual workflow...")
        
        # Initialize state
        initial_state: ZIPAccrualState = {
            "messages": [],
            "status": WorkflowStatus.PENDING,
            "error": None,
            "metadata": inputs,
            "zip_invoices": [],
            "netsuite_bills": [],
            "accrual_calculations": [],
            "journal_entries": [],
            "approval_request": None
        }
        
        # Build and run graph
        if not self.graph:
            self.build_graph()
        
        config = {"configurable": {"thread_id": inputs.get("thread_id", "default")}}
        result = self.graph.invoke(initial_state, config)
        
        return result


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Run ZIP accrual agent
    agent = ZIPAccrualAgent()
    
    inputs = {
        "close_date": "2025-11-30",
        "subsidiary": 1,
        "zip_file_path": "/path/to/zip_export.csv",
        "thread_id": "zip-nov-2025"
    }
    
    result = agent.run(inputs)
    
    print(f"\nWorkflow Status: {result['status']}")
    if result.get('approval_request'):
        print(f"Approval Request ID: {result['approval_request'].request_id}")
        print(f"Journal Entries: {len(result['journal_entries'])}")
        for je in result['journal_entries']:
            print(f"  - {je.memo}: ${je.total_debit:,.2f}")
