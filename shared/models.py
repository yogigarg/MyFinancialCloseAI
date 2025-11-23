"""
Shared models and utilities for FinClose AI agents
"""

from typing import Any, Dict, List, Optional, TypedDict, Annotated
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import operator


# ============================================================================
# Enums
# ============================================================================

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    ERROR = "error"


class VarianceClassification(str, Enum):
    """Classification of variances in reconciliation"""
    TIMING = "timing"
    TRUE_VARIANCE = "true_variance"
    KNOWN_ADJUSTMENT = "known_adjustment"
    IMMATERIAL = "immaterial"


class ApprovalDecision(str, Enum):
    """Human approval decisions"""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_INVESTIGATION = "needs_investigation"


# ============================================================================
# Base Models
# ============================================================================

class JournalEntryLine(BaseModel):
    """Journal entry line item"""
    account: int
    account_name: str
    debit: Optional[float] = 0.0
    credit: Optional[float] = 0.0
    department: Optional[int] = None
    department_name: Optional[str] = None
    class_id: Optional[int] = Field(None, alias="class")
    class_name: Optional[str] = None
    location: Optional[int] = None
    location_name: Optional[str] = None
    memo: Optional[str] = None
    entity: Optional[int] = None


class JournalEntry(BaseModel):
    """Complete journal entry"""
    subsidiary: int
    subsidiary_name: str
    trandate: str
    memo: str
    lines: List[JournalEntryLine]
    total_debit: float = 0.0
    total_credit: float = 0.0
    
    def validate_balance(self) -> bool:
        """Check if journal entry balances"""
        self.total_debit = sum(line.debit or 0 for line in self.lines)
        self.total_credit = sum(line.credit or 0 for line in self.lines)
        return abs(self.total_debit - self.total_credit) < 0.01


class Variance(BaseModel):
    """Variance identified during reconciliation"""
    account: str
    account_name: str
    source_amount: float
    target_amount: float
    variance_amount: float
    variance_percent: float
    classification: Optional[VarianceClassification] = None
    explanation: Optional[str] = None
    is_material: bool = False
    requires_approval: bool = False


class ApprovalRequest(BaseModel):
    """Request for human approval"""
    request_id: str
    workflow_type: str
    created_at: datetime
    data: Dict[str, Any]
    variances: List[Variance] = []
    journal_entries: List[JournalEntry] = []
    status: ApprovalDecision = Field(default=None)
    approver: Optional[str] = None
    approved_at: Optional[datetime] = None
    comments: Optional[str] = None


# ============================================================================
# Agent State Types
# ============================================================================

class BaseAgentState(TypedDict):
    """Base state for all agents"""
    messages: Annotated[List[Dict[str, Any]], operator.add]
    status: WorkflowStatus
    error: Optional[str]
    metadata: Dict[str, Any]


class ZIPAccrualState(BaseAgentState):
    """State for ZIP Accrual Agent"""
    zip_invoices: List[Dict[str, Any]]
    netsuite_bills: List[Dict[str, Any]]
    accrual_calculations: List[Dict[str, Any]]
    journal_entries: List[JournalEntry]
    approval_request: Optional[ApprovalRequest]


class PayrollReconState(BaseAgentState):
    """State for Payroll Reconciliation Agent"""
    workday_data: List[Dict[str, Any]]
    netsuite_data: List[Dict[str, Any]]
    reconciliation_results: List[Dict[str, Any]]
    variances: List[Variance]
    approval_request: Optional[ApprovalRequest]


class EquityProcessingState(BaseAgentState):
    """State for Equity Processing Agent"""
    shareworks_data: List[Dict[str, Any]]
    employee_dimensions: List[Dict[str, Any]]
    mapped_data: List[Dict[str, Any]]
    reconciliation: Dict[str, Any]
    journal_entries: List[JournalEntry]
    approval_request: Optional[ApprovalRequest]


# ============================================================================
# Utility Functions
# ============================================================================

def calculate_materiality(amount: float, threshold: float = 1000.0) -> bool:
    """Check if variance is material"""
    return abs(amount) >= threshold


def classify_variance(variance: Variance, patterns: Dict[str, Any]) -> VarianceClassification:
    """
    Classify variance based on patterns and rules
    This would use AI in production to analyze variance patterns
    """
    if not variance.is_material:
        return VarianceClassification.IMMATERIAL
    
    # Check for known patterns
    if variance.account_name in patterns.get("known_adjustments", []):
        return VarianceClassification.KNOWN_ADJUSTMENT
    
    # Timing differences (this is simplified)
    if abs(variance.variance_percent) < 5:
        return VarianceClassification.TIMING
    
    return VarianceClassification.TRUE_VARIANCE


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.2f}%"


def generate_request_id() -> str:
    """Generate unique request ID"""
    return f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


# ============================================================================
# Error Handling
# ============================================================================

class FinCloseError(Exception):
    """Base exception for FinClose AI"""
    pass


class DataExtractionError(FinCloseError):
    """Error during data extraction"""
    pass


class ValidationError(FinCloseError):
    """Error during validation"""
    pass


class ReconciliationError(FinCloseError):
    """Error during reconciliation"""
    pass


class NetSuiteError(FinCloseError):
    """Error interacting with NetSuite"""
    pass
