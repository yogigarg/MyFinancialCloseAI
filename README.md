# FinClose AI - Month-End Close Automation

**AI-powered automation for Gusto's financial close process using LangGraph agents and Claude 3.5 Sonnet**

## 🎯 Overview

FinClose AI automates Gusto's month-end financial close process using AI-powered agents that handle:

- **ZIP Accrual Processing**: Automated invoice extraction, service period identification, proration calculations
- **Payroll Reconciliation**: Workday-to-NetSuite reconciliation with variance analysis
- **Equity Transaction Processing**: ShareWorks data processing with employee dimension mapping
- **Journal Entry Generation**: Automated JE creation with validation and posting

### Key Benefits

| Metric | Current State | With FinClose AI | Improvement |
|--------|---------------|------------------|-------------|
| ZIP Accrual Time | 2-3 hours | 15 minutes | 88-92% reduction |
| Payroll Recon Time | 1-2 hours | 20 minutes | 83-90% reduction |
| Error Rate | ~5% | <1% | 80% reduction |
| Audit Trail | Manual docs | Automated | 100% coverage |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  User Interface                      │
│            Streamlit Web Application                 │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────┐
│              LangGraph Orchestration                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │   ZIP    │  │ Payroll  │  │  Equity  │          │
│  │  Agent   │  │  Agent   │  │  Agent   │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────┐
│              NetSuite MCP Server                     │
│         (Model Context Protocol)                     │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────┐
│               External Systems                       │
│  NetSuite │ Google Drive │ Workday │ ShareWorks    │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- AWS Account (for EKS deployment)
- NetSuite account with OAuth credentials
- Anthropic API key for Claude

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finclose-ai
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Streamlit UI: http://localhost:8501
   - MCP Server: http://localhost:8000
   - Agent API: http://localhost:8001

### Running Individual Components

#### NetSuite MCP Server
```bash
cd mcp-server
pip install -r requirements.txt
python netsuite_server.py
```

#### LangGraph Agents
```bash
cd agents
pip install -r requirements.txt
python zip_accrual_agent.py
```

#### Streamlit Application
```bash
cd streamlit-app
pip install -r requirements.txt
streamlit run app.py
```

---

## 📦 Project Structure

```
finclose-ai/
├── mcp-server/              # NetSuite MCP Server
│   ├── netsuite_server.py   # Main MCP server implementation
│   ├── requirements.txt
│   └── Dockerfile
│
├── agents/                   # LangGraph AI Agents
│   ├── zip_accrual_agent.py         # ZIP accrual automation
│   ├── payroll_recon_agent.py       # Payroll reconciliation
│   ├── equity_processing_agent.py   # Equity transaction processing
│   ├── requirements.txt
│   └── Dockerfile
│
├── streamlit-app/           # User Interface
│   ├── app.py              # Main Streamlit application
│   ├── requirements.txt
│   └── Dockerfile
│
├── shared/                  # Shared utilities
│   ├── models.py           # Data models and types
│   └── utils.py            # Helper functions
│
├── docs/                    # Documentation
│   ├── k8s-*.yaml          # Kubernetes deployment files
│   └── architecture.md     # Architecture documentation
│
├── tests/                   # Test suites
│   ├── test_mcp_server.py
│   ├── test_agents.py
│   └── test_integration.py
│
├── docker-compose.yml       # Local development setup
└── README.md               # This file
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# NetSuite Configuration
NETSUITE_ACCOUNT_ID=your_account_id
NETSUITE_CONSUMER_KEY=your_consumer_key
NETSUITE_CONSUMER_SECRET=your_consumer_secret
NETSUITE_TOKEN_ID=your_token_id
NETSUITE_TOKEN_SECRET=your_token_secret
NETSUITE_REST_URL=https://your-account.suitetalk.api.netsuite.com

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key

# LangSmith (for monitoring)
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=finclose-ai

# Database
POSTGRES_PASSWORD=secure_password_here
DATABASE_URL=postgresql://finclose:password@postgres:5432/finclose_ai

# Redis
REDIS_URL=redis://redis:6379/0

# AWS (for production deployment)
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=123456789012
```

---

## 🤖 AI Agents

### 1. ZIP Accrual Agent

Automates the ZIP invoice accrual process:

1. Extracts pending invoices from ZIP system
2. Fetches existing NetSuite bills
3. Uses AI to identify service periods from descriptions
4. Calculates day-by-day prorated accruals
5. Generates journal entries
6. Creates approval request

**Usage:**
```python
from agents.zip_accrual_agent import ZIPAccrualAgent

agent = ZIPAccrualAgent()
result = agent.run({
    "close_date": "2025-11-30",
    "subsidiary": 1,
    "zip_file_path": "/path/to/zip_export.csv"
})
```

### 2. Payroll Reconciliation Agent

Reconciles Workday payroll data with NetSuite:

1. Extracts Workday payroll data
2. Fetches NetSuite journal entries
3. Performs account-by-account reconciliation
4. Classifies variances (Timing, True Variance, Known)
5. Applies $1,000 materiality threshold
6. Routes to approval if needed

**Usage:**
```python
from agents.payroll_recon_agent import PayrollReconciliationAgent

agent = PayrollReconciliationAgent()
result = agent.run({
    "pay_period": "2025-11-15",
    "subsidiary": 1,
    "workday_file_path": "/path/to/workday.csv"
})
```

### 3. Equity Processing Agent

Processes equity transactions from ShareWorks:

1. Downloads ShareWorks equity report
2. Fetches NetSuite employee dimensions
3. Maps employees to dimensions
4. Performs three-way reconciliation
5. Generates journal entries
6. Presents for approval

---

## 🔌 NetSuite MCP Server

The MCP (Model Context Protocol) server provides standardized tools for AI agents to interact with NetSuite.

### Available Tools

- `netsuite_suiteql_query`: Execute SuiteQL queries
- `netsuite_get_record`: Get record by type and ID
- `netsuite_create_journal_entry`: Create journal entries
- `netsuite_get_pending_bills`: Search vendor bills
- `netsuite_get_journal_entries`: Retrieve JEs for period
- `netsuite_get_employee_dimensions`: Get employee mapping
- `netsuite_post_journal_entry`: Post/approve JE
- `netsuite_get_chart_of_accounts`: Get COA

### Available Resources

- `netsuite://accounts`: Chart of accounts
- `netsuite://vendors`: Vendor master
- `netsuite://employees`: Employee dimensions

---

## 🚢 Deployment

### AWS EKS Deployment

1. **Set up EKS cluster**
   ```bash
   eksctl create cluster -f docs/eks-cluster.yaml
   ```

2. **Create namespaces**
   ```bash
   kubectl create namespace finclose-prod
   kubectl create namespace finclose-staging
   ```

3. **Deploy secrets**
   ```bash
   kubectl create secret generic netsuite-credentials \
     --from-literal=account_id=$NETSUITE_ACCOUNT_ID \
     --from-literal=consumer_key=$NETSUITE_CONSUMER_KEY \
     --namespace=finclose-prod
   ```

4. **Deploy applications**
   ```bash
   kubectl apply -f docs/k8s-mcp-deployment.yaml
   kubectl apply -f docs/k8s-streamlit-deployment.yaml
   kubectl apply -f docs/k8s-agents-deployment.yaml
   ```

5. **Verify deployment**
   ```bash
   kubectl get pods -n finclose-prod
   kubectl get services -n finclose-prod
   ```

---

## 🧪 Testing

### Run unit tests
```bash
pytest tests/
```

### Run integration tests
```bash
pytest tests/test_integration.py
```

### Test MCP server
```bash
# Using MCP Inspector
npx @modelcontextprotocol/inspector python mcp-server/netsuite_server.py
```

---

## 📊 Monitoring

### LangSmith

All agent executions are traced in LangSmith:
- Visit: https://smith.langchain.com
- Project: finclose-ai
- View traces, performance metrics, and token usage

### CloudWatch

Infrastructure monitoring via CloudWatch:
- Application logs
- Resource metrics
- Custom dashboards
- Alarms and alerts

---

## 🔒 Security

### Security Layers

1. **Network Security**
   - VPC isolation
   - Private subnets for workloads
   - Security groups for access control

2. **Authentication & Authorization**
   - AWS Cognito for user authentication
   - Role-based access control (RBAC)
   - JWT tokens for API access
   - MFA for production access

3. **Data Protection**
   - Encryption at rest (RDS, S3, EBS)
   - Encryption in transit (TLS 1.2+)
   - Secrets Manager for credentials
   - PII data masking

4. **Audit & Compliance**
   - Comprehensive audit logging
   - 7-year retention for financial data
   - SOC 2 Type II alignment

---

## 👥 Team

**Gusto Team:**
- Justine O'Sullivan: Month-end close lead
- Selena Ochoa: Payroll reconciliation
- Ample Pesquesa: Equity processing
- Will Ott: Equity oversight

**Jade Global Team:**
- Yogi Garg: Project Lead
- Vikas Manchanda: Solution Architect
- Chetan Gangwal: Technical Lead
- Development Team: Rahul Jain, Jayakumar Viswanathan

---

## 📝 License

Copyright © 2025 Jade Global. All rights reserved.

---

## 🤝 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Contact: support@jadeglobal.com
- Documentation: [docs/](docs/)

---

## 🎓 Additional Resources

- [NetSuite REST API Documentation](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/book_1559132836.html)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Built with ❤️ by Jade Global AI & Automation Team**
