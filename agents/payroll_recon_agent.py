"""
Payroll Reconciliation Agent for FinClose AI
Automates Workday to NetSuite payroll reconciliation with variance analysis
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

import sys
sys.path.append('..')
from shared.models import (
    PayrollReconState, Variance, ApprovalRequest,
    WorkflowStatus, VarianceClassification,
    calculate_materiality, generate_request_id
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Payroll Reconciliation Agent
# ============================================================================

class PayrollReconciliationAgent:
    """
    Agent for automating payroll reconciliation between Workday and NetSuite
    
    Workflow:
    1. Extract Workday payroll data (summary level)
    2. Fetch NetSuite journal entries for payroll
    3. Perform account-by-account reconciliation
    4. Classify variances (Timing, True Variance, Known Adjustment)
    5. Apply $1,000 materiality threshold
    6. Route to approval if needed
    """
    
    MATERIALITY_THRESHOLD = 1000.0
    
    def __init__(self, llm_model: str = "claude-3-5-sonnet-20241022"):
        self.llm = ChatAnthropic(model=llm_model, temperature=0)
        self.graph = None
        self.checkpointer = MemorySaver()
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(PayrollReconState)
        
        # Add nodes
        workflow.add_node("extract_workday_data", self.extract_workday_data)
        workflow.add_node("fetch_netsuite_data", self.fetch_netsuite_data)
        workflow.add_node("reconcile_accounts", self.reconcile_accounts)
        workflow.add_node("classify_variances", self.classify_variances)
        workflow.add_node("determine_approval_needed", self.determine_approval_needed)
        workflow.add_node("create_approval_request", self.create_approval_request)
        workflow.add_node("auto_approve", self.auto_approve)
        workflow.add_node("send_notification", self.send_notification)
        
        # Define edges
        workflow.set_entry_point("extract_workday_data")
        workflow.add_edge("extract_workday_data", "fetch_netsuite_data")
        workflow.add_edge("fetch_netsuite_data", "reconcile_accounts")
        workflow.add_edge("reconcile_accounts", "classify_variances")
        workflow.add_edge("classify_variances", "determine_approval_needed")
        
        # Conditional routing based on approval need
        workflow.add_conditional_edges(
            "determine_approval_needed",
            self.route_approval,
            {
                "needs_approval": "create_approval_request",
                "auto_approve": "auto_approve"
            }
        )
        
        workflow.add_edge("create_approval_request", "send_notification")
        workflow.add_edge("auto_approve", "send_notification")
        workflow.add_edge("send_notification", END)
        
        self.graph = workflow.compile(checkpointer=self.checkpointer)
        return self.graph
    
    def extract_workday_data(self, state: PayrollReconState) -> PayrollReconState:
        """Extract payroll data from Workday report"""
        logger.info("Extracting Workday payroll data...")
        
        try:
            # In production, this would read from Google Drive or Workday API
            # For now, simulated data
            
            workday_data = [
                {
                    "account": "6501",
                    "account_name": "Gross Wages - Salary",
                    "amount": 2500000.00,
                    "pay_period": "2025-11-15",
                    "department": "Engineering"
                },
                {
                    "account": "6502",
                    "account_name": "Gross Wages - Hourly",
                    "amount": 150000.00,
                    "pay_period": "2025-11-15",
                    "department": "Operations"
                },
                {
                    "account": "2301",
                    "account_name": "Accrued Payroll Taxes",
                    "amount": 425000.00,
                    "pay_period": "2025-11-15",
                    "department": "All"
                },
                {
                    "account": "2302",
                    "account_name": "Employee Tax Withholdings",
                    "amount": 650000.00,
                    "pay_period": "2025-11-15",
                    "department": "All"
                }
            ]
            
            state["workday_data"] = workday_data
            state["status"] = WorkflowStatus.IN_PROGRESS
            state["messages"].append({
                "role": "system",
                "content": f"Extracted Workday data for {len(workday_data)} accounts"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to extract Workday data: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def fetch_netsuite_data(self, state: PayrollReconState) -> PayrollReconState:
        """Fetch NetSuite journal entries for payroll"""
        logger.info("Fetching NetSuite payroll journal entries...")
        
        try:
            # In production, this would call NetSuite MCP server
            # Example MCP call:
            # result = call_tool("netsuite_get_journal_entries", {
            #     "date_from": "2025-11-15",
            #     "date_to": "2025-11-15",
            #     "subsidiary": 1
            # })
            
            netsuite_data = [
                {
                    "account": "6501",
                    "account_name": "Gross Wages - Salary",
                    "amount": 2498500.00,  # Slight variance
                    "journal_id": "JE-12345",
                    "trandate": "2025-11-15"
                },
                {
                    "account": "6502",
                    "account_name": "Gross Wages - Hourly",
                    "amount": 150000.00,  # Perfect match
                    "journal_id": "JE-12345",
                    "trandate": "2025-11-15"
                },
                {
                    "account": "2301",
                    "account_name": "Accrued Payroll Taxes",
                    "amount": 426200.00,  # Material variance
                    "journal_id": "JE-12345",
                    "trandate": "2025-11-15"
                },
                {
                    "account": "2302",
                    "account_name": "Employee Tax Withholdings",
                    "amount": 650000.00,  # Perfect match
                    "journal_id": "JE-12345",
                    "trandate": "2025-11-15"
                }
            ]
            
            state["netsuite_data"] = netsuite_data
            state["messages"].append({
                "role": "system",
                "content": f"Fetched NetSuite data for {len(netsuite_data)} accounts"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to fetch NetSuite data: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def reconcile_accounts(self, state: PayrollReconState) -> PayrollReconState:
        """Perform account-by-account reconciliation"""
        logger.info("Reconciling accounts...")
        
        try:
            # Create lookup for NetSuite data
            netsuite_lookup = {
                item["account"]: item for item in state["netsuite_data"]
            }
            
            reconciliation_results = []
            variances = []
            
            for workday_item in state["workday_data"]:
                account = workday_item["account"]
                netsuite_item = netsuite_lookup.get(account)
                
                if not netsuite_item:
                    # Account in Workday but not in NetSuite
                    variance = Variance(
                        account=account,
                        account_name=workday_item["account_name"],
                        source_amount=workday_item["amount"],
                        target_amount=0.0,
                        variance_amount=workday_item["amount"],
                        variance_percent=100.0,
                        is_material=calculate_materiality(
                            workday_item["amount"],
                            self.MATERIALITY_THRESHOLD
                        ),
                        requires_approval=True
                    )
                    variances.append(variance)
                else:
                    # Compare amounts
                    variance_amount = workday_item["amount"] - netsuite_item["amount"]
                    
                    if abs(variance_amount) > 0.01:  # Not a perfect match
                        variance_percent = (
                            (variance_amount / workday_item["amount"] * 100)
                            if workday_item["amount"] != 0 else 0
                        )
                        
                        variance = Variance(
                            account=account,
                            account_name=workday_item["account_name"],
                            source_amount=workday_item["amount"],
                            target_amount=netsuite_item["amount"],
                            variance_amount=variance_amount,
                            variance_percent=variance_percent,
                            is_material=calculate_materiality(
                                variance_amount,
                                self.MATERIALITY_THRESHOLD
                            ),
                            requires_approval=False  # Will be determined in next step
                        )
                        variances.append(variance)
                
                reconciliation_results.append({
                    "account": account,
                    "account_name": workday_item["account_name"],
                    "workday_amount": workday_item["amount"],
                    "netsuite_amount": netsuite_item["amount"] if netsuite_item else 0.0,
                    "variance": variance_amount if netsuite_item else workday_item["amount"],
                    "matched": abs(variance_amount if netsuite_item else workday_item["amount"]) < 0.01
                })
            
            state["reconciliation_results"] = reconciliation_results
            state["variances"] = variances
            
            matched_count = sum(1 for r in reconciliation_results if r["matched"])
            state["messages"].append({
                "role": "assistant",
                "content": f"Reconciliation complete: {matched_count}/{len(reconciliation_results)} accounts matched"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Reconciliation failed: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def classify_variances(self, state: PayrollReconState) -> PayrollReconState:
        """Use AI to classify variances"""
        logger.info("Classifying variances with AI...")
        
        try:
            for variance in state["variances"]:
                if not variance.is_material:
                    variance.classification = VarianceClassification.IMMATERIAL
                    variance.explanation = f"Variance of ${abs(variance.variance_amount):,.2f} is below materiality threshold"
                    continue
                
                # Use LLM to classify material variances
                prompt = f"""
                Classify this payroll reconciliation variance:
                
                Account: {variance.account_name}
                Workday Amount: ${variance.source_amount:,.2f}
                NetSuite Amount: ${variance.target_amount:,.2f}
                Variance: ${variance.variance_amount:,.2f} ({variance.variance_percent:.2f}%)
                
                Classifications:
                1. TIMING - Difference due to timing of accruals or payments (e.g., one system accrues, other doesn't)
                2. TRUE_VARIANCE - Actual difference requiring investigation or correction
                3. KNOWN_ADJUSTMENT - Expected difference due to known process (e.g., manual adjustments, corrections)
                
                Return JSON:
                {{
                    "classification": "TIMING|TRUE_VARIANCE|KNOWN_ADJUSTMENT",
                    "explanation": "Brief explanation of the variance",
                    "requires_approval": true|false,
                    "recommended_action": "Suggested next step"
                }}
                """
                
                messages = [
                    SystemMessage(content="You are an expert at analyzing payroll reconciliation variances."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                
                try:
                    classification = json.loads(response.content)
                    variance.classification = VarianceClassification[classification["classification"]]
                    variance.explanation = classification["explanation"]
                    variance.requires_approval = classification["requires_approval"]
                except:
                    # Fallback classification
                    variance.classification = VarianceClassification.TRUE_VARIANCE
                    variance.explanation = "Classification failed, requires manual review"
                    variance.requires_approval = True
            
            state["messages"].append({
                "role": "assistant",
                "content": f"Classified {len(state['variances'])} variances"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Variance classification failed: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def determine_approval_needed(self, state: PayrollReconState) -> PayrollReconState:
        """Determine if human approval is needed"""
        logger.info("Determining approval requirements...")
        
        try:
            needs_approval = any(v.requires_approval for v in state["variances"])
            
            state["metadata"]["needs_approval"] = needs_approval
            state["messages"].append({
                "role": "system",
                "content": f"Approval {'required' if needs_approval else 'not required'}"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to determine approval: {str(e)}")
            state["status"] = WorkflowStatus.ERROR
            state["error"] = str(e)
            return state
    
    def route_approval(self, state: PayrollReconState) -> str:
        """Route to approval or auto-approve"""
        return "needs_approval" if state["metadata"].get("needs_approval") else "auto_approve"
    
    def create_approval_request(self, state: PayrollReconState) -> PayrollReconState:
        """Create approval request for Selena Ochoa"""
        logger.info("Creating approval request...")
        
        try:
            approval_request = ApprovalRequest(
                request_id=generate_request_id(),
                workflow_type="payroll_reconciliation",
                created_at=datetime.now(),
                data={
                    "pay_period": state["metadata"].get("pay_period"),
                    "total_accounts": len(state["reconciliation_results"]),
                    "matched_accounts": sum(1 for r in state["reconciliation_results"] if r["matched"]),
                    "material_variances": sum(1 for v in state["variances"] if v.is_material)
                },
                variances=[v for v in state["variances"] if v.requires_approval],
                journal_entries=[]
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
    
    def auto_approve(self, state: PayrollReconState) -> PayrollReconState:
        """Auto-approve when no material variances"""
        logger.info("Auto-approving reconciliation...")
        
        state["status"] = WorkflowStatus.COMPLETED
        state["messages"].append({
            "role": "system",
            "content": "Reconciliation auto-approved - all variances immaterial or explained"
        })
        
        return state
    
    def send_notification(self, state: PayrollReconState) -> PayrollReconState:
        """Send email notification to Selena Ochoa"""
        logger.info("Sending notification email...")
        
        try:
            # In production, this would use SendGrid or similar
            recipient = "selena.ochoa@gusto.com"
            
            if state["status"] == WorkflowStatus.AWAITING_APPROVAL:
                subject = f"Payroll Reconciliation Requires Approval - {state['approval_request'].request_id}"
                body = f"""
                Material variances detected in payroll reconciliation.
                
                Pay Period: {state['metadata'].get('pay_period')}
                Material Variances: {len([v for v in state['variances'] if v.requires_approval])}
                
                Please review in FinClose AI dashboard.
                """
            else:
                subject = f"Payroll Reconciliation Complete - Auto-Approved"
                body = f"""
                Payroll reconciliation completed successfully.
                
                Pay Period: {state['metadata'].get('pay_period')}
                All variances: Immaterial or explained
                
                No action required.
                """
            
            state["messages"].append({
                "role": "system",
                "content": f"Notification sent to {recipient}"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            # Don't fail the workflow for notification errors
            return state
    
    def run(self, inputs: Dict[str, Any]) -> PayrollReconState:
        """Execute the payroll reconciliation workflow"""
        logger.info("Starting Payroll Reconciliation workflow...")
        
        # Initialize state
        initial_state: PayrollReconState = {
            "messages": [],
            "status": WorkflowStatus.PENDING,
            "error": None,
            "metadata": inputs,
            "workday_data": [],
            "netsuite_data": [],
            "reconciliation_results": [],
            "variances": [],
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
    # Example: Run payroll reconciliation agent
    agent = PayrollReconciliationAgent()
    
    inputs = {
        "pay_period": "2025-11-15",
        "subsidiary": 1,
        "workday_file_path": "/path/to/workday_export.csv",
        "thread_id": "payroll-nov-15-2025"
    }
    
    result = agent.run(inputs)
    
    print(f"\nWorkflow Status: {result['status']}")
    print(f"Total Accounts: {len(result['reconciliation_results'])}")
    print(f"Variances: {len(result['variances'])}")
    
    if result.get('approval_request'):
        print(f"Approval Request: {result['approval_request'].request_id}")
