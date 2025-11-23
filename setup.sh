#!/bin/bash

# FinClose AI Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "=================================================="
echo "  FinClose AI - Setup Script"
echo "=================================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi
echo "✅ Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi
echo "✅ Docker Compose found: $(docker-compose --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+ first."
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

echo ""
echo "=================================================="
echo "  Setting up environment"
echo "=================================================="

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file with your actual credentials"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/uploads
echo "✅ Directories created"

# Build Docker images
echo ""
echo "=================================================="
echo "  Building Docker images"
echo "=================================================="

docker-compose build

echo ""
echo "✅ Docker images built successfully"

# Initialize database
echo ""
echo "=================================================="
echo "  Initializing database"
echo "=================================================="

# Start postgres and redis first
docker-compose up -d postgres redis

echo "Waiting for PostgreSQL to be ready..."
sleep 10

# Create database schema
docker-compose exec -T postgres psql -U finclose -d finclose_ai << EOF
-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS processing;
CREATE SCHEMA IF NOT EXISTS approval;
CREATE SCHEMA IF NOT EXISTS output;
CREATE SCHEMA IF NOT EXISTS workflow;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create core tables
CREATE TABLE IF NOT EXISTS workflow.executions (
    id SERIAL PRIMARY KEY,
    workflow_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS approval.queue (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(50) UNIQUE NOT NULL,
    workflow_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    data JSONB NOT NULL,
    approver VARCHAR(100),
    approved_at TIMESTAMP,
    comments TEXT
);

CREATE TABLE IF NOT EXISTS audit.log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_name VARCHAR(100),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details JSONB
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow.executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_type ON workflow.executions(workflow_type);
CREATE INDEX IF NOT EXISTS idx_approval_status ON approval.queue(status);
CREATE INDEX IF NOT EXISTS idx_approval_created ON approval.queue(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit.log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit.log(user_name);

EOF

echo "✅ Database initialized"

echo ""
echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   - NetSuite OAuth credentials"
echo "   - Anthropic API key"
echo "   - Other service credentials"
echo ""
echo "2. Start all services:"
echo "   docker-compose up -d"
echo ""
echo "3. Check service status:"
echo "   docker-compose ps"
echo ""
echo "4. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "5. Access the application:"
echo "   - Streamlit UI: http://localhost:8501"
echo "   - MCP Server: http://localhost:8000"
echo "   - Agent API: http://localhost:8001"
echo ""
echo "For more information, see README.md"
echo ""
