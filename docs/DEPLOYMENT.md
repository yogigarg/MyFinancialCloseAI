# FinClose AI - Deployment Guide

This guide covers deploying FinClose AI from local development to production on AWS EKS.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [AWS Infrastructure Setup](#aws-infrastructure-setup)
3. [Container Registry Setup](#container-registry-setup)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Database Migration](#database-migration)
6. [Monitoring Setup](#monitoring-setup)
7. [Post-Deployment Verification](#post-deployment-verification)

---

## Local Development Setup

### Prerequisites

- Docker 24.0+
- Docker Compose 2.0+
- Python 3.11+
- Git

### Steps

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd finclose-ai
   ./setup.sh
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Verify**
   ```bash
   docker-compose ps
   curl http://localhost:8501
   curl http://localhost:8000/health
   ```

---

## AWS Infrastructure Setup

### 1. Create VPC

```bash
# Using AWS CLI
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=finclose-vpc}]'

# Create subnets (2 public, 2 private, 2 data across 2 AZs)
aws ec2 create-subnet \
  --vpc-id <vpc-id> \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-west-2a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=finclose-public-1a}]'
```

### 2. Create RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier finclose-postgres \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.4 \
  --master-username finclose \
  --master-user-password <secure-password> \
  --allocated-storage 100 \
  --vpc-security-group-ids <sg-id> \
  --db-subnet-group-name finclose-db-subnet \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted \
  --tags Key=Project,Value=FinClose-AI
```

### 3. Create ElastiCache Redis

```bash
aws elasticache create-replication-group \
  --replication-group-id finclose-redis \
  --replication-group-description "FinClose AI Redis" \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled \
  --cache-subnet-group-name finclose-redis-subnet \
  --security-group-ids <sg-id>
```

### 4. Create S3 Bucket

```bash
aws s3 mb s3://finclose-ai-data --region us-west-2

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket finclose-ai-data \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket finclose-ai-data \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

---

## Container Registry Setup

### 1. Create ECR Repositories

```bash
# MCP Server
aws ecr create-repository \
  --repository-name finclose-mcp-server \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256

# Streamlit App
aws ecr create-repository \
  --repository-name finclose-streamlit \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256

# Agent Workers
aws ecr create-repository \
  --repository-name finclose-agents \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256
```

### 2. Build and Push Images

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Build and push MCP Server
cd mcp-server
docker build -t finclose-mcp-server .
docker tag finclose-mcp-server:latest \
  <account-id>.dkr.ecr.us-west-2.amazonaws.com/finclose-mcp-server:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/finclose-mcp-server:latest

# Build and push Streamlit
cd ../streamlit-app
docker build -t finclose-streamlit .
docker tag finclose-streamlit:latest \
  <account-id>.dkr.ecr.us-west-2.amazonaws.com/finclose-streamlit:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/finclose-streamlit:latest

# Build and push Agents
cd ../agents
docker build -t finclose-agents .
docker tag finclose-agents:latest \
  <account-id>.dkr.ecr.us-west-2.amazonaws.com/finclose-agents:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/finclose-agents:latest
```

---

## Kubernetes Deployment

### 1. Create EKS Cluster

```bash
eksctl create cluster \
  --name finclose-ai-cluster \
  --region us-west-2 \
  --version 1.28 \
  --vpc-cidr 10.0.0.0/16 \
  --nodegroup-name finclose-nodes \
  --node-type t3.large \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 10 \
  --managed \
  --ssh-access \
  --ssh-public-key my-key
```

### 2. Configure kubectl

```bash
aws eks update-kubeconfig \
  --region us-west-2 \
  --name finclose-ai-cluster
```

### 3. Create Namespaces

```bash
kubectl create namespace finclose-prod
kubectl create namespace finclose-staging
```

### 4. Create Secrets

```bash
# NetSuite credentials
kubectl create secret generic netsuite-credentials \
  --from-literal=account_id=$NETSUITE_ACCOUNT_ID \
  --from-literal=consumer_key=$NETSUITE_CONSUMER_KEY \
  --from-literal=consumer_secret=$NETSUITE_CONSUMER_SECRET \
  --from-literal=token_id=$NETSUITE_TOKEN_ID \
  --from-literal=token_secret=$NETSUITE_TOKEN_SECRET \
  --namespace=finclose-prod

# Application secrets
kubectl create secret generic finclose-secrets \
  --from-literal=database_url=$DATABASE_URL \
  --from-literal=redis_url=$REDIS_URL \
  --from-literal=anthropic_api_key=$ANTHROPIC_API_KEY \
  --from-literal=langsmith_api_key=$LANGSMITH_API_KEY \
  --namespace=finclose-prod
```

### 5. Create ConfigMaps

```bash
kubectl create configmap finclose-config \
  --from-literal=netsuite_rest_url=$NETSUITE_REST_URL \
  --from-literal=backend_api_url=http://agent-workers-service:8001 \
  --from-literal=environment=production \
  --namespace=finclose-prod
```

### 6. Deploy Applications

```bash
# Deploy MCP Server
kubectl apply -f docs/k8s-mcp-deployment.yaml

# Deploy Streamlit App
kubectl apply -f docs/k8s-streamlit-deployment.yaml

# Deploy Agent Workers
kubectl apply -f docs/k8s-agents-deployment.yaml
```

### 7. Verify Deployments

```bash
# Check pods
kubectl get pods -n finclose-prod

# Check services
kubectl get services -n finclose-prod

# Check ingress
kubectl get ingress -n finclose-prod

# View logs
kubectl logs -f deployment/streamlit-app -n finclose-prod
```

---

## Database Migration

### 1. Connect to RDS

```bash
# Get RDS endpoint
aws rds describe-db-instances \
  --db-instance-identifier finclose-postgres \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text

# Connect
psql -h <rds-endpoint> -U finclose -d finclose_ai
```

### 2. Run Migrations

```sql
-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS processing;
CREATE SCHEMA IF NOT EXISTS approval;
CREATE SCHEMA IF NOT EXISTS output;
CREATE SCHEMA IF NOT EXISTS workflow;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create tables (see setup.sh for full SQL)
```

---

## Monitoring Setup

### 1. CloudWatch Configuration

```bash
# Create log groups
aws logs create-log-group --log-group-name /aws/eks/finclose-ai/mcp-server
aws logs create-log-group --log-group-name /aws/eks/finclose-ai/streamlit
aws logs create-log-group --log-group-name /aws/eks/finclose-ai/agents

# Set retention
aws logs put-retention-policy \
  --log-group-name /aws/eks/finclose-ai/mcp-server \
  --retention-in-days 30
```

### 2. LangSmith Setup

1. Create project at https://smith.langchain.com
2. Get API key
3. Configure in application secrets

### 3. Prometheus & Grafana

```bash
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

---

## Post-Deployment Verification

### 1. Health Checks

```bash
# Check all pods are running
kubectl get pods -n finclose-prod | grep Running

# Check all services are available
kubectl get svc -n finclose-prod

# Test MCP Server
curl http://<mcp-service-endpoint>/health

# Test Streamlit
curl http://<streamlit-endpoint>/_stcore/health
```

### 2. Smoke Tests

```bash
# Run test workflow
kubectl exec -it deployment/agent-workers -n finclose-prod -- \
  python -c "from agents.zip_accrual_agent import ZIPAccrualAgent; \
             agent = ZIPAccrualAgent(); \
             print('Agent initialized successfully')"
```

### 3. Security Verification

```bash
# Check network policies
kubectl get networkpolicies -n finclose-prod

# Check security contexts
kubectl get pods -n finclose-prod -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext}{"\n"}{end}'

# Check secrets encryption
kubectl get secrets -n finclose-prod -o json | jq '.items[].metadata.name'
```

### 4. Performance Testing

```bash
# Load test Streamlit
ab -n 1000 -c 10 http://<streamlit-endpoint>/

# Monitor metrics
kubectl top pods -n finclose-prod
kubectl top nodes
```

---

## Rollback Procedure

If deployment fails:

```bash
# Rollback deployment
kubectl rollout undo deployment/streamlit-app -n finclose-prod
kubectl rollout undo deployment/netsuite-mcp-server -n finclose-prod

# Check rollout status
kubectl rollout status deployment/streamlit-app -n finclose-prod

# Restore from backup
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier finclose-postgres-restored \
  --db-snapshot-identifier finclose-postgres-snapshot-20251122
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Get pod details
kubectl describe pod <pod-name> -n finclose-prod

# Check logs
kubectl logs <pod-name> -n finclose-prod --previous

# Check events
kubectl get events -n finclose-prod --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Test connectivity from pod
kubectl exec -it <pod-name> -n finclose-prod -- \
  psql -h <rds-endpoint> -U finclose -d finclose_ai -c "SELECT 1"

# Check security groups
aws ec2 describe-security-groups \
  --group-ids <sg-id> \
  --query 'SecurityGroups[0].IpPermissions'
```

### Performance Issues

```bash
# Check resource usage
kubectl top pods -n finclose-prod

# Check HPA status
kubectl get hpa -n finclose-prod

# Scale manually if needed
kubectl scale deployment/streamlit-app --replicas=5 -n finclose-prod
```

---

## Maintenance

### Regular Tasks

1. **Daily**
   - Monitor CloudWatch dashboards
   - Review error logs
   - Check approval queue

2. **Weekly**
   - Review LangSmith traces
   - Analyze cost metrics
   - Update documentation

3. **Monthly**
   - Database backup verification
   - Security patch updates
   - Performance optimization

### Backup Strategy

```bash
# RDS automated backups (already enabled)
# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier finclose-postgres \
  --db-snapshot-identifier finclose-manual-$(date +%Y%m%d)

# Backup application data
kubectl exec -it deployment/agent-workers -n finclose-prod -- \
  pg_dump -h <rds-endpoint> -U finclose finclose_ai > backup-$(date +%Y%m%d).sql
```

---

## Production Checklist

Before going live:

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Security groups properly configured
- [ ] SSL certificates installed
- [ ] Monitoring and alerting active
- [ ] Backup strategy tested
- [ ] Disaster recovery plan documented
- [ ] User access and permissions configured
- [ ] Integration tests passed
- [ ] Performance benchmarks met
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Go-live runbook prepared

---

## Support Contacts

- **Infrastructure**: DevOps Team
- **Application**: Jade Global Development Team
- **Business**: Gusto Finance Team

---

**Document Version**: 1.0  
**Last Updated**: November 22, 2025  
**Next Review**: December 22, 2025
