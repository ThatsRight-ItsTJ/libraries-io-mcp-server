# Deployment Guide

This comprehensive deployment guide covers multiple deployment options for the Libraries.io MCP Server, including local development, Docker, cloud platforms, and enterprise deployments.

## Table of Contents

- [Overview](#overview)
- [Local Development Deployment](#local-development-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Platform Deployment](#cloud-platform-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Enterprise Deployment](#enterprise-deployment)
- [Monitoring and Logging](#monitoring-and-logging)
- [Performance Optimization](#performance-optimization)
- [Scaling Strategies](#scaling-strategies)
- [Security Considerations](#security-considerations)
- [Backup and Recovery](#backup-and-recovery)

## Overview

The Libraries.io MCP Server can be deployed in various environments depending on your requirements:

| Deployment Type | Best For | Complexity | Scalability | Cost |
|----------------|----------|------------|-------------|------|
| Local Development | Development and testing | Low | Low | Free |
| Docker | Consistent environments | Medium | Medium | Low |
| Cloud Platform | Production workloads | Medium-High | High | Variable |
| Kubernetes | Enterprise/High availability | High | Very High | High |
| Serverless | Event-driven workloads | Medium | High | Pay-as-you-go |

## Local Development Deployment

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/librariesio/libraries-io-mcp-server.git
cd libraries-io-mcp-server

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Set up environment
cp .env.example .env
# Edit .env with your configuration
```

### Configuration

Create a `.env` file with the following settings:

```env
# Required
LIBRARIES_IO_API_KEY=your_api_key_here

# Optional
LIBRARIES_IO_BASE_URL=https://libraries.io/api/v1
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### Running Locally

```bash
# Development mode with auto-reload
uvicorn src.libraries_io_mcp.server:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.libraries_io_mcp.server:app --host 0.0.0.0 --port 8000
```

### Using Systemd (Linux)

Create a systemd service file:

```ini
# /etc/systemd/system/libraries-io-mcp-server.service
[Unit]
Description=Libraries.io MCP Server
After=network.target

[Service]
Type=simple
User=appuser
Group=appuser
WorkingDirectory=/opt/libraries-io-mcp-server
Environment=PATH=/opt/libraries-io-mcp-server/venv/bin
ExecStart=/opt/libraries-io-mcp-server/venv/bin/uvicorn src.libraries_io_mcp.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start the service
sudo systemctl enable libraries-io-mcp-server
sudo systemctl start libraries-io-mcp-server
sudo systemctl status libraries-io-mcp-server
```

## Docker Deployment

### Quick Start

```bash
# Clone and setup
git clone https://github.com/librariesio/libraries-io-mcp-server.git
cd libraries-io-mcp-server

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Build and run
docker-compose up --build -d
```

### Docker Compose Configuration

#### Basic Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  libraries-io-mcp-server:
    build: .
    container_name: libraries-io-mcp-server
    ports:
      - "8000:8000"
    environment:
      - LIBRARIES_IO_API_KEY=${LIBRARIES_IO_API_KEY}
      - LIBRARIES_IO_BASE_URL=${LIBRARIES_IO_BASE_URL}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - RATE_LIMIT_REQUESTS=${RATE_LIMIT_REQUESTS:-100}
      - RATE_LIMIT_WINDOW=${RATE_LIMIT_WINDOW:-3600}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  libraries-io-mcp-server:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: libraries-io-mcp-server-prod
    ports:
      - "80:8000"
    environment:
      - LIBRARIES_IO_API_KEY=${LIBRARIES_IO_API_KEY}
      - LIBRARIES_IO_BASE_URL=${LIBRARIES_IO_BASE_URL}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - RATE_LIMIT_REQUESTS=${RATE_LIMIT_REQUESTS:-100}
      - RATE_LIMIT_WINDOW=${RATE_LIMIT_WINDOW:-3600}
      - METRICS_ENABLED=true
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - libraries-io-network

  nginx:
    image: nginx:alpine
    container_name: libraries-io-mcp-nginx
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - libraries-io-mcp-server
    networks:
      - libraries-io-network

networks:
  libraries-io-network:
    driver: bridge
```

### Dockerfile Options

#### Development Dockerfile

```dockerfile
# Dockerfile.dev
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.libraries_io_mcp.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Production Dockerfile

```dockerfile
# Dockerfile.prod
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.libraries_io_mcp.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Build and Push

```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t your-registry/libraries-io-mcp-server:latest .

# Push to registry
docker buildx build --platform linux/amd64,linux/arm64 -t your-registry/libraries-io-mcp-server:latest --push .

# Tag and push specific version
docker tag libraries-io-mcp-server:latest your-registry/libraries-io-mcp-server:v1.0.0
docker push your-registry/libraries-io-mcp-server:v1.0.0
```

## Cloud Platform Deployment

### AWS Deployment

#### AWS ECS (Elastic Container Service)

```yaml
# task-definition.json
{
  "family": "libraries-io-mcp-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "libraries-io-mcp-server",
      "image": "your-registry/libraries-io-mcp-server:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LIBRARIES_IO_API_KEY",
          "value": "your_api_key_here"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/libraries-io-mcp-server",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 40
      }
    }
  ]
}
```

#### AWS Lambda (Serverless)

```python
# lambda_handler.py
import json
import os
from libraries_io_mcp.server import create_server

# Initialize server once (outside handler for reuse)
server = None

def lambda_handler(event, context):
    global server
    
    if server is None:
        server = create_server()
    
    # Handle different event types
    if event.get('httpMethod') == 'GET':
        return handle_get_request(event, server)
    elif event.get('httpMethod') == 'POST':
        return handle_post_request(event, server)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

def handle_get_request(event, server):
    path = event.get('path', '')
    
    if path == '/health':
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'healthy'})
        }
    
    # Add other GET endpoint handlers
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'})
    }

def handle_post_request(event, server):
    # Handle MCP tool calls
    try:
        body = json.loads(event.get('body', '{}'))
        tool_name = body.get('tool')
        parameters = body.get('parameters', {})
        
        # Route to appropriate tool handler
        result = await server.handle_tool_call(tool_name, parameters)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

#### AWS EKS (Elastic Kubernetes Service)

```yaml
# eks-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: libraries-io-mcp-server
  labels:
    app: libraries-io-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: libraries-io-mcp-server
  template:
    metadata:
      labels:
        app: libraries-io-mcp-server
    spec:
      containers:
      - name: libraries-io-mcp-server
        image: your-registry/libraries-io-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: LIBRARIES_IO_API_KEY
          valueFrom:
            secretKeyRef:
              name: libraries-io-secrets
              key: api-key
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: libraries-io-mcp-server-service
spec:
  selector:
    app: libraries-io-mcp-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Google Cloud Platform Deployment

#### Google Cloud Run

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT-ID/libraries-io-mcp-server
gcloud run deploy libraries-io-mcp-server \
  --image gcr.io/PROJECT-ID/libraries-io-mcp-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="LIBRARIES_IO_API_KEY=your_api_key_here,LOG_LEVEL=INFO"
```

#### Google Kubernetes Engine (GKE)

```yaml
# gke-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: libraries-io-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: libraries-io-mcp-server
  template:
    metadata:
      labels:
        app: libraries-io-mcp-server
    spec:
      containers:
      - name: libraries-io-mcp-server
        image: gcr.io/PROJECT-ID/libraries-io-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: LIBRARIES_IO_API_KEY
          valueFrom:
            secretKeyRef:
              name: libraries-io-secrets
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: libraries-io-mcp-server-service
spec:
  selector:
    app: libraries-io-mcp-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Azure Deployment

#### Azure Container Instances

```bash
# Deploy to Azure Container Instances
az container create \
  --resource-group myResourceGroup \
  --name libraries-io-mcp-server \
  --image your-registry/libraries-io-mcp-server:latest \
  --ports 8000 \
  --environment-variables 'LIBRARIES_IO_API_KEY=your_api_key_here' 'LOG_LEVEL=INFO' \
  --dns-name-label libraries-io-mcp-server \
  --location eastus
```

#### Azure Kubernetes Service (AKS)

```yaml
# aks-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: libraries-io-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: libraries-io-mcp-server
  template:
    metadata:
      labels:
        app: libraries-io-mcp-server
    spec:
      containers:
      - name: libraries-io-mcp-server
        image: your-registry.azurecr.io/libraries-io-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: LIBRARIES_IO_API_KEY
          valueFrom:
            secretKeyRef:
              name: libraries-io-secrets
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: libraries-io-mcp-server-service
spec:
  selector:
    app: libraries-io-mcp-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## Kubernetes Deployment

### Helm Chart

```yaml
# Chart.yaml
apiVersion: v2
name: libraries-io-mcp-server
description: A Helm chart for Libraries.io MCP Server
type: application
version: 0.1.0
appVersion: "1.0.0"
```

```yaml
# values.yaml
replicaCount: 3

image:
  repository: your-registry/libraries-io-mcp-server
  pullPolicy: IfNotPresent
  tag: "latest"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}

podSecurityContext: {}
  # fsGroup: 2000

securityContext: {}
  # capabilities:
  #   drop:
  #   - ALL
  # readOnlyRootFilesystem: true
  # runAsNonRoot: true
  # runAsUser: 1000

service:
  type: LoadBalancer
  port: 80

ingress:
  enabled: false
  className: ""
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []
  #  - secretName: chart-example-tls
  #    hosts:
  #      - chart-example.local

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80
  # targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}

env:
  LIBRARIES_IO_API_KEY: ""
  LOG_LEVEL: "INFO"
  RATE_LIMIT_REQUESTS: "100"
  RATE_LIMIT_WINDOW: "3600"

secrets:
  libraries-io-api-key:
    enabled: true
    name: libraries-io-secrets
    keys:
      api-key: LIBRARIES_IO_API_KEY

volumes:
  - name: logs
    emptyDir: {}

volumeMounts:
  - name: logs
    mountPath: /app/logs

livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Kubernetes Deployment Commands

```bash
# Install the Helm chart
helm install libraries-io-mcp-server ./charts/libraries-io-mcp-server

# Upgrade the chart
helm upgrade libraries-io-mcp-server ./charts/libraries-io-mcp-server

# Uninstall the chart
helm uninstall libraries-io-mcp-server

# Check deployment status
kubectl get pods -l app=libraries-io-mcp-server
kubectl get services libraries-io-mcp-server-service
kubectl logs -f deployment/libraries-io-mcp-server
```

## Enterprise Deployment

### High Availability Configuration

```yaml
# enterprise-deployment.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: libraries-io-mcp-server-config
data:
  config.yaml: |
    rate_limit:
      requests: 1000
      window: 3600
    cache:
      ttl: 300
      max_size: 10000
    logging:
      level: INFO
      format: json
    monitoring:
      enabled: true
      metrics_port: 9090
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: libraries-io-mcp-server
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: libraries-io-mcp-server
  template:
    metadata:
      labels:
        app: libraries-io-mcp-server
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - libraries-io-mcp-server
              topologyKey: "kubernetes.io/hostname"
      containers:
      - name: libraries-io-mcp-server
        image: your-registry/libraries-io-mcp-server:latest
        ports:
        - containerPort: 8000
        - containerPort: 9090
        env:
        - name: LIBRARIES_IO_API_KEY
          valueFrom:
            secretKeyRef:
              name: libraries-io-secrets
              key: api-key
        - name: CONFIG_PATH
          value: "/app/config/config.yaml"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config-volume
        configMap:
          name: libraries-io-mcp-server-config
---
apiVersion: v1
kind: Service
metadata:
  name: libraries-io-mcp-server-service
spec:
  selector:
    app: libraries-io-mcp-server
  ports:
    - name: http
      protocol: TCP
      port: 80
      targetPort: 8000
    - name: metrics
      protocol: TCP
      port: 9090
      targetPort: 9090
  type: LoadBalancer
```

### Multi-Region Deployment

```yaml
# multi-region-deployment.yaml
apiVersion: v1
kind: Service
metadata:
  name: libraries-io-mcp-server-global
spec:
  selector:
    app: libraries-io-mcp-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ExternalName
  externalName: libraries-io-mcp-server-dns.global
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: libraries-io-mcp-server-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "route"
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
spec:
  tls:
  - hosts:
    - libraries-io.example.com
    secretName: libraries-io-tls
  rules:
  - host: libraries-io.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: libraries-io-mcp-server-service
            port:
              number: 80
```

## Monitoring and Logging

### Prometheus Monitoring

```yaml
# prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    scrape_configs:
    - job_name: 'libraries-io-mcp-server'
      static_configs:
      - targets: ['libraries-io-mcp-server-service:9090']
      metrics_path: /metrics
      scrape_interval: 15s
      scrape_timeout: 10s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Libraries.io MCP Server",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error Rate"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

```python
# logging_config.py
import logging
import logging.handlers
import os

def setup_logging():
    """Setup structured logging for production."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logger
    logger = logging.getLogger('libraries_io_mcp')
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (for production)
    if os.getenv('ENVIRONMENT') == 'production':
        file_handler = logging.handlers.RotatingFileHandler(
            '/app/logs/app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
```

## Performance Optimization

### Caching Configuration

```python
# cache_config.py
from datetime import timedelta
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis

async def init_cache():
    """Initialize Redis cache."""
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        db=0
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    return redis_client

@cache(expire=300)  # 5 minutes cache
async def get_cached_package_info(platform: str, name: str):
    """Get cached package information."""
    # Implementation
    pass
```

### Database Optimization

```python
# database_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

def create_database_engine():
    """Create optimized database connection pool."""
    return create_engine(
        os.getenv('DATABASE_URL'),
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False  # Set to True for SQL debugging
    )

def create_session_factory(engine):
    """Create session factory with optimized settings."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False
    )
```

### Connection Pooling

```python
# connection_pool.py
import httpx
from typing import Optional

class ConnectionPool:
    """HTTP connection pool for API calls."""
    
    def __init__(self, max_connections: int = 100):
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=20
            ),
            timeout=httpx.Timeout(30.0)
        )
    
    async def get(self, url: str, **kwargs) -> Optional[httpx.Response]:
        """Make GET request with connection pooling."""
        try:
            response = await self.client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
    
    async def close(self):
        """Close the connection pool."""
        await self.client.aclose()

# Global connection pool instance
connection_pool = ConnectionPool()
```

## Scaling Strategies

### Horizontal Scaling

```yaml
# horizontal-scaling.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: libraries-io-mcp-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: libraries-io-mcp-server
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

### Vertical Scaling

```yaml
# vertical-scaling.yaml
apiVersion: autoscaling/v2
kind: VerticalPodAutoscaler
metadata:
  name: libraries-io-mcp-server-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: libraries-io-mcp-server
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: libraries-io-mcp-server
      minAllowed:
        cpu: "500m"
        memory: "512Mi"
      maxAllowed:
        cpu: "2000m"
        memory: "2Gi"
      controlledResources: ["cpu", "memory"]
```

### Cluster Autoscaling

```yaml
# cluster-autoscaler.yaml
apiVersion: autoscaling/v2beta2
kind: ClusterAutoscaler
metadata:
  name: cluster-autoscaler
spec:
  scaleDown:
    enabled: true
    delayAfterAdd: 10m
    delayAfterDelete: 10s
    delayAfterFailure: 30s
    unneededTime: 10m
  scaleUp:
    enabled: true
    delayAfterAdd: 10s
    delayAfterFailure: 10s
    maxProvisioningRate: 10
    maxUnneededNodes: 10
    newPodScaleUpDelay: 10s
```

## Security Considerations

### Network Security

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: libraries-io-mcp-server-network-policy
spec:
  podSelector:
    matchLabels:
      app: libraries-io-mcp-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: default
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: default
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 10.0.0.0/8
        - 172.16.0.0/12
        - 192.168.0.0/16
    ports:
    - protocol: TCP
      port: 443
```

### RBAC Configuration

```yaml
# rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: libraries-io-mcp-server-sa
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: libraries-io-mcp-server-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: libraries-io-mcp-server-rolebinding
subjects:
- kind: ServiceAccount
  name: libraries-io-mcp-server-sa
roleRef:
  kind: Role
  name: libraries-io-mcp-server-role
  apiGroup: rbac.authorization.k8s.io
```

### Security Context

```yaml
# security-context.yaml
apiVersion: v1
kind: Pod
metadata:
  name: libraries-io-mcp-server-secure
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: libraries-io-mcp-server
    image: your-registry/libraries-io-mcp-server:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
        - ALL
      seccompProfile:
        type: RuntimeDefault
```

## Backup and Recovery

### Data Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
NAMESPACE="default"
POD_NAME="libraries-io-mcp-server-0"

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup configuration files
kubectl get configmap libraries-io-mcp-server-config -n $NAMESPACE -o yaml > $BACKUP_DIR/$DATE/configmap.yaml

# Backup secrets
kubectl get secret libraries-io-secrets -n $NAMESPACE -o yaml > $BACKUP_DIR/$DATE/secrets.yaml

# Backup deployment configuration
kubectl get deployment libraries-io-mcp-server -n $NAMESPACE -o yaml > $BACKUP_DIR/$DATE/deployment.yaml

# Backup logs
kubectl logs -n $NAMESPACE deployment/libraries-io-mcp-server > $BACKUP_DIR/$DATE/logs.txt

# Compress backup
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR $DATE

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/backup_$DATE.tar.gz"
```

### Disaster Recovery Plan

```yaml
# disaster-recovery.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: disaster-recovery-config
data:
  recovery-plan: |
    # Disaster Recovery Plan for Libraries.io MCP Server
    
    ## Recovery Steps
    
    ### 1. Assess the Situation
    - Check cluster status: `kubectl get nodes`
    - Check pod status: `kubectl get pods -A`
    - Check service availability: `kubectl get services -A`
    
    ### 2. Restore from Backup
    - Restore configuration: `kubectl apply -f backup/configmap.yaml`
    - Restore secrets: `kubectl apply -f backup/secrets.yaml`
    - Restore deployment: `kubectl apply -f backup/deployment.yaml`
    
    ### 3. Verify Services
    - Check pod status: `kubectl get pods -l app=libraries-io-mcp-server`
    - Check service endpoints: `kubectl get endpoints libraries-io-mcp-server-service`
    - Test application health: `curl http://<service-ip>/health`
    
    ### 4. Monitor Recovery
    - Monitor logs: `kubectl logs -f deployment/libraries-io-mcp-server`
    - Monitor metrics: `kubectl top pods -l app=libraries-io-mcp-server`
    - Monitor performance: Check response times and error rates
    
    ## Contact Information
    - On-call engineer: +1-555-0123
    - Support team: support@example.com
    - Emergency contact: emergency@example.com
```

### Automated Backup Script

```python
# automated_backup.py
import asyncio
import subprocess
import os
from datetime import datetime
import logging

class BackupManager:
    """Automated backup manager for Libraries.io MCP Server."""
    
    def __init__(self, backup_dir="/backups", retention_days=7):
        self.backup_dir = backup_dir
        self.retention_days = retention_days
        self.logger = logging.getLogger(__name__)
    
    async def create_backup(self, namespace="default"):
        """Create automated backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, timestamp)
        
        try:
            # Create backup directory
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup configuration
            await self._backup_configmaps(namespace, backup_path)
            await self._backup_secrets(namespace, backup_path)
            await self._backup_deployments(namespace, backup_path)
            await self._backup_logs(namespace, backup_path)
            
            # Compress backup
            await self._compress_backup(backup_path, timestamp)
            
            # Clean old backups
            await self._cleanup_old_backups()
            
            self.logger.info(f"Backup completed: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    async def _backup_configmaps(self, namespace, backup_path):
        """Backup configmaps."""
        result = subprocess.run([
            "kubectl", "get", "configmap", "-n", namespace, "-o", "yaml"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            with open(os.path.join(backup_path, "configmaps.yaml"), "w") as f:
                f.write(result.stdout)
    
    async def _backup_secrets(self, namespace, backup_path):
        """Backup secrets."""
        result = subprocess.run([
            "kubectl", "get", "secret", "-n", namespace, "-o", "yaml"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            with open(os.path.join(backup_path, "secrets.yaml"), "w") as f:
                f.write(result.stdout)
    
    async def _backup_deployments(self, namespace, backup_path):
        """Backup deployments."""
        result = subprocess.run([
            "kubectl", "get", "deployment", "-n", namespace, "-o", "yaml"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            with open(os.path.join(backup_path, "deployments.yaml"), "w") as f:
                f.write(result.stdout)
    
    async def _backup_logs(self, namespace, backup_path):
        """Backup logs."""
        result = subprocess.run([
            "kubectl", "logs", "-n", namespace", "deployment/libraries-io-mcp-server"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            with open(os.path.join(backup_path, "logs.txt"), "w") as f:
                f.write(result.stdout)
    
    async def _compress_backup(self, backup_path, timestamp):
        """Compress backup directory."""
        import tarfile
        
        with tarfile.open(f"{self.backup_dir}/backup_{timestamp}.tar.gz", "w:gz") as tar:
            tar.add(backup_path, arcname=os.path.basename(backup_path))
        
        # Remove uncompressed backup
        import shutil
        shutil.rmtree(backup_path)
    
    async def _cleanup_old_backups(self):
        """Clean up old backups."""
        import time
        
        cutoff_time = time.time() - (self.retention_days * 24 * 60 * 60)
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith("backup_") and filename.endswith(".tar.gz"):
                filepath = os.path.join(self.backup_dir, filename)
                file_time = os.path.getmtime(filepath)
                
                if file_time < cutoff_time:
                    os.remove(filepath)
                    self.logger.info(f"Removed old backup: {filename}")

# Usage
async def main():
    backup_manager = BackupManager()
    success = await backup_manager.create_backup()
    if success:
        print("Backup completed successfully")
    else:
        print("Backup failed")

if __name__ == "__main__":
    asyncio.run(main())
```

## Conclusion

This comprehensive deployment guide provides multiple options for deploying the Libraries.io MCP Server across different environments. Choose the deployment strategy that best fits your requirements for scalability, performance, and cost-effectiveness.

For additional support and questions:
- Check the [GitHub Issues](https://github.com/librariesio/libraries-io-mcp-server/issues)
- Review the [troubleshooting guide](docs/troubleshooting.md)
- Join the [community discussions](https://github.com/librariesio/libraries-io-mcp-server/discussions)