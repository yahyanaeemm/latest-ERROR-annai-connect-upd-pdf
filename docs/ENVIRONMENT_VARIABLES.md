# AnnaiCONNECT Environment Variables Guide

## 📋 Overview

This document provides comprehensive information about all environment variables used in the AnnaiCONNECT application, including their purposes, default values, and configuration recommendations for different environments.

## 🔧 Backend Environment Variables

### Database Configuration

#### `MONGO_URL`
- **Description**: MongoDB connection string
- **Required**: Yes
- **Type**: String (URI)
- **Default**: `mongodb://localhost:27017`

**Examples:**
```bash
# Local Development
MONGO_URL="mongodb://localhost:27017"

# Production with Authentication
MONGO_URL="mongodb://username:password@localhost:27017/database?authSource=admin"

# MongoDB Atlas
MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/database"

# Replica Set
MONGO_URL="mongodb://host1:27017,host2:27017,host3:27017/database?replicaSet=rs0"
```

#### `DB_NAME`
- **Description**: Database name for the application
- **Required**: Yes
- **Type**: String
- **Default**: `test_database`

**Examples:**
```bash
# Development
DB_NAME="annaiconnect_development"

# Testing
DB_NAME="annaiconnect_test"

# Production
DB_NAME="annaiconnect_production"
```

### Security Configuration

#### `SECRET_KEY`
- **Description**: Secret key for JWT token signing and encryption
- **Required**: Yes
- **Type**: String (minimum 32 characters)
- **Default**: `your-secret-key-here`
- **Security**: **CRITICAL** - Must be changed in production

**Generation Examples:**
```bash
# Generate secure key using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate using OpenSSL
openssl rand -base64 32

# Generate using uuidgen
uuidgen | tr -d '-' | head -c 32
```

**Configuration:**
```bash
# Development (acceptable)
SECRET_KEY="development-secret-key-not-for-production"

# Production (required format)
SECRET_KEY="XyZ9vB2nQ8mK4pL7wR3cD6fH1jA5sG9tE2uI8oP4qM0nB7vC3x"
```

#### `ALGORITHM`
- **Description**: JWT token signing algorithm
- **Required**: Yes
- **Type**: String
- **Default**: `HS256`
- **Options**: `HS256`, `HS384`, `HS512`, `RS256`, `RS384`, `RS512`

**Examples:**
```bash
# Standard configuration (recommended)
ALGORITHM="HS256"

# High security environments
ALGORITHM="RS256"  # Requires RSA key pair
```

### Application Configuration

#### `HOST`
- **Description**: Host address for the FastAPI application
- **Required**: No
- **Type**: String (IP address)
- **Default**: `0.0.0.0`

**Examples:**
```bash
# All interfaces (production)
HOST="0.0.0.0"

# Localhost only (development)
HOST="127.0.0.1"

# Specific interface
HOST="192.168.1.100"
```

#### `PORT`
- **Description**: Port number for the FastAPI application
- **Required**: No
- **Type**: Integer
- **Default**: `8001`

**Examples:**
```bash
# Standard configuration
PORT="8001"

# Alternative port
PORT="8000"

# Custom port
PORT="3001"
```

#### `WORKERS`
- **Description**: Number of worker processes for production
- **Required**: No
- **Type**: Integer
- **Default**: `1`

**Examples:**
```bash
# Single worker (development)
WORKERS="1"

# Multiple workers (production)
WORKERS="4"

# CPU-based workers
WORKERS=$(nproc)  # Number of CPU cores
```

### File Storage Configuration

#### `UPLOAD_DIR`
- **Description**: Directory for storing uploaded files
- **Required**: No
- **Type**: String (path)
- **Default**: `uploads`

**Examples:**
```bash
# Relative path
UPLOAD_DIR="uploads"

# Absolute path
UPLOAD_DIR="/opt/annaiconnect/uploads"

# Network storage
UPLOAD_DIR="/mnt/nfs/annaiconnect/uploads"
```

#### `MAX_FILE_SIZE`
- **Description**: Maximum file upload size in bytes
- **Required**: No
- **Type**: Integer
- **Default**: `52428800` (50MB)

**Examples:**
```bash
# 50MB (default)
MAX_FILE_SIZE="52428800"

# 100MB
MAX_FILE_SIZE="104857600"

# 10MB (restricted)
MAX_FILE_SIZE="10485760"
```

### Email Configuration (Optional)

#### `SMTP_HOST`
- **Description**: SMTP server hostname
- **Required**: No (if email features used)
- **Type**: String

**Examples:**
```bash
# Gmail
SMTP_HOST="smtp.gmail.com"

# Outlook
SMTP_HOST="smtp-mail.outlook.com"

# Custom SMTP
SMTP_HOST="mail.yourdomain.com"
```

#### `SMTP_PORT`
- **Description**: SMTP server port
- **Required**: No
- **Type**: Integer
- **Default**: `587`

**Examples:**
```bash
# TLS (recommended)
SMTP_PORT="587"

# SSL
SMTP_PORT="465"

# Non-encrypted (not recommended)
SMTP_PORT="25"
```

#### `SMTP_USERNAME`
- **Description**: SMTP authentication username
- **Required**: No
- **Type**: String

#### `SMTP_PASSWORD`
- **Description**: SMTP authentication password
- **Required**: No
- **Type**: String
- **Security**: Store securely, use app passwords when possible

### Logging Configuration

#### `LOG_LEVEL`
- **Description**: Application logging level
- **Required**: No
- **Type**: String
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Examples:**
```bash
# Development
LOG_LEVEL="DEBUG"

# Production
LOG_LEVEL="INFO"

# Error monitoring
LOG_LEVEL="ERROR"
```

#### `LOG_FILE`
- **Description**: Log file path
- **Required**: No
- **Type**: String

**Examples:**
```bash
# Relative path
LOG_FILE="logs/application.log"

# Absolute path
LOG_FILE="/var/log/annaiconnect/application.log"

# Date-based rotation
LOG_FILE="/var/log/annaiconnect/app-$(date +%Y%m%d).log"
```

### Performance Configuration

#### `REDIS_URL`
- **Description**: Redis connection string for caching
- **Required**: No
- **Type**: String (URI)

**Examples:**
```bash
# Local Redis
REDIS_URL="redis://localhost:6379"

# Redis with password
REDIS_URL="redis://:password@localhost:6379"

# Redis Cluster
REDIS_URL="redis://localhost:7000,localhost:7001,localhost:7002"
```

#### `CACHE_TTL`
- **Description**: Default cache time-to-live in seconds
- **Required**: No
- **Type**: Integer
- **Default**: `3600` (1 hour)

**Examples:**
```bash
# 1 hour
CACHE_TTL="3600"

# 1 day
CACHE_TTL="86400"

# 5 minutes
CACHE_TTL="300"
```

---

## 🌐 Frontend Environment Variables

### API Configuration

#### `REACT_APP_BACKEND_URL`
- **Description**: Backend API base URL
- **Required**: Yes
- **Type**: String (URL)
- **Default**: `http://localhost:8001`

**Examples:**
```bash
# Local Development
REACT_APP_BACKEND_URL="http://localhost:8001"

# Production
REACT_APP_BACKEND_URL="https://api.yourdomain.com"

# Staging
REACT_APP_BACKEND_URL="https://staging-api.yourdomain.com"
```

#### `REACT_APP_API_TIMEOUT`
- **Description**: API request timeout in milliseconds
- **Required**: No
- **Type**: Integer
- **Default**: `30000` (30 seconds)

**Examples:**
```bash
# Standard timeout
REACT_APP_API_TIMEOUT="30000"

# Extended timeout
REACT_APP_API_TIMEOUT="60000"

# Quick timeout
REACT_APP_API_TIMEOUT="10000"
```

### Development Configuration

#### `WDS_SOCKET_PORT`
- **Description**: WebSocket port for hot reload
- **Required**: No (development only)
- **Type**: Integer
- **Default**: `3000`

**Examples:**
```bash
# Standard development
WDS_SOCKET_PORT="3000"

# Custom port
WDS_SOCKET_PORT="3001"

# HTTPS development
WDS_SOCKET_PORT="443"
```

#### `REACT_APP_ENV`
- **Description**: Application environment
- **Required**: No
- **Type**: String
- **Default**: `development`
- **Options**: `development`, `staging`, `production`

**Examples:**
```bash
# Development
REACT_APP_ENV="development"

# Staging
REACT_APP_ENV="staging"

# Production
REACT_APP_ENV="production"
```

### Feature Flags

#### `REACT_APP_ENABLE_ANALYTICS`
- **Description**: Enable analytics tracking
- **Required**: No
- **Type**: Boolean
- **Default**: `false`

**Examples:**
```bash
# Enable analytics
REACT_APP_ENABLE_ANALYTICS="true"

# Disable analytics
REACT_APP_ENABLE_ANALYTICS="false"
```

#### `REACT_APP_DEBUG_MODE`
- **Description**: Enable debug features
- **Required**: No
- **Type**: Boolean
- **Default**: `false`

**Examples:**
```bash
# Debug enabled (development)
REACT_APP_DEBUG_MODE="true"

# Debug disabled (production)
REACT_APP_DEBUG_MODE="false"
```

### UI Configuration

#### `REACT_APP_THEME`
- **Description**: Default application theme
- **Required**: No
- **Type**: String
- **Default**: `light`
- **Options**: `light`, `dark`, `auto`

**Examples:**
```bash
# Light theme
REACT_APP_THEME="light"

# Dark theme
REACT_APP_THEME="dark"

# System preference
REACT_APP_THEME="auto"
```

#### `REACT_APP_LANGUAGE`
- **Description**: Default application language
- **Required**: No
- **Type**: String
- **Default**: `en`

**Examples:**
```bash
# English
REACT_APP_LANGUAGE="en"

# Spanish
REACT_APP_LANGUAGE="es"

# Multi-language
REACT_APP_LANGUAGE="auto"
```

---

## 📁 Environment Files

### File Structure

```
project/
├── backend/
│   ├── .env                    # Main backend environment
│   ├── .env.development        # Development overrides
│   ├── .env.staging            # Staging configuration
│   ├── .env.production         # Production configuration
│   └── .env.example            # Example configuration
└── frontend/
    ├── .env                    # Main frontend environment
    ├── .env.local              # Local overrides
    ├── .env.development        # Development configuration
    ├── .env.staging            # Staging configuration
    ├── .env.production         # Production configuration
    └── .env.example            # Example configuration
```

### Environment File Examples

#### Backend .env.example
```bash
# Database Configuration
MONGO_URL="mongodb://localhost:27017"
DB_NAME="annaiconnect_development"

# Security Configuration
SECRET_KEY="your-secure-secret-key-minimum-32-characters"
ALGORITHM="HS256"

# Application Configuration
HOST="0.0.0.0"
PORT="8001"
WORKERS="1"

# File Storage
UPLOAD_DIR="uploads"
MAX_FILE_SIZE="52428800"

# Logging
LOG_LEVEL="INFO"
LOG_FILE="logs/application.log"

# Optional: Email Configuration
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USERNAME="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"

# Optional: Caching
REDIS_URL="redis://localhost:6379"
CACHE_TTL="3600"
```

#### Frontend .env.example
```bash
# API Configuration
REACT_APP_BACKEND_URL="http://localhost:8001"
REACT_APP_API_TIMEOUT="30000"

# Development Configuration
WDS_SOCKET_PORT="3000"
REACT_APP_ENV="development"

# Feature Flags
REACT_APP_ENABLE_ANALYTICS="false"
REACT_APP_DEBUG_MODE="false"

# UI Configuration
REACT_APP_THEME="light"
REACT_APP_LANGUAGE="en"
```

---

## 🔐 Security Best Practices

### Sensitive Information

#### Never Commit Secrets
```bash
# Add to .gitignore
.env
.env.local
.env.production
.env.staging
*.key
*.pem
```

#### Environment Variable Validation
```python
# Backend validation example
import os
from typing import Optional

def get_required_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

def get_optional_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)

# Usage
MONGO_URL = get_required_env("MONGO_URL")
SECRET_KEY = get_required_env("SECRET_KEY")
LOG_LEVEL = get_optional_env("LOG_LEVEL", "INFO")
```

#### Secret Management Tools

**AWS Secrets Manager**
```bash
# Store secret
aws secretsmanager create-secret \
    --name "annaiconnect/database" \
    --secret-string '{"username":"admin","password":"secure_password"}'

# Retrieve in application
import boto3
client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='annaiconnect/database')
```

**HashiCorp Vault**
```bash
# Store secret
vault kv put secret/annaiconnect/db \
    username=admin \
    password=secure_password

# Retrieve in application
import hvac
client = hvac.Client(url='https://vault.company.com')
secret = client.secrets.kv.v2.read_secret_version(path='annaiconnect/db')
```

### Environment Separation

#### Development Environment
```bash
# .env.development
MONGO_URL="mongodb://localhost:27017"
DB_NAME="annaiconnect_development"
SECRET_KEY="development-secret-not-for-production"
LOG_LEVEL="DEBUG"
REACT_APP_DEBUG_MODE="true"
```

#### Staging Environment
```bash
# .env.staging
MONGO_URL="mongodb://staging-db:27017"
DB_NAME="annaiconnect_staging"
SECRET_KEY="staging-secret-key-32-characters-long"
LOG_LEVEL="INFO"
REACT_APP_DEBUG_MODE="false"
```

#### Production Environment
```bash
# .env.production
MONGO_URL="mongodb://prod-user:secure-pass@prod-db:27017/annaiconnect_production"
DB_NAME="annaiconnect_production"
SECRET_KEY="production-ultra-secure-secret-key-64-chars-minimum"
LOG_LEVEL="WARNING"
REACT_APP_DEBUG_MODE="false"
```

---

## 🚀 Deployment Configurations

### Docker Environment

#### docker-compose.yml Environment
```yaml
version: '3.8'
services:
  backend:
    environment:
      - MONGO_URL=${MONGO_URL}
      - DB_NAME=${DB_NAME}
      - SECRET_KEY=${SECRET_KEY}
    env_file:
      - ./backend/.env
  
  frontend:
    environment:
      - REACT_APP_BACKEND_URL=${REACT_APP_BACKEND_URL}
    env_file:
      - ./frontend/.env
```

#### Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: annaiconnect-config
data:
  DB_NAME: "annaiconnect_production"
  LOG_LEVEL: "INFO"
  REACT_APP_THEME: "light"
---
apiVersion: v1
kind: Secret
metadata:
  name: annaiconnect-secrets
type: Opaque
stringData:
  MONGO_URL: "mongodb://user:pass@mongo:27017/prod"
  SECRET_KEY: "ultra-secure-production-secret-key"
```

### Cloud Platform Configurations

#### AWS ECS Task Definition
```json
{
  "environment": [
    {
      "name": "DB_NAME",
      "value": "annaiconnect_production"
    },
    {
      "name": "LOG_LEVEL",
      "value": "INFO"
    }
  ],
  "secrets": [
    {
      "name": "MONGO_URL",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:mongo-url"
    },
    {
      "name": "SECRET_KEY",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:jwt-secret"
    }
  ]
}
```

#### Heroku Configuration
```bash
# Set environment variables
heroku config:set MONGO_URL="mongodb://user:pass@host/db"
heroku config:set SECRET_KEY="secure-secret-key"
heroku config:set DB_NAME="annaiconnect_production"

# View all config vars
heroku config
```

---

## 🔍 Troubleshooting

### Common Issues

#### Missing Environment Variables
```bash
# Check if variable is set
echo $MONGO_URL

# List all environment variables
env | grep REACT_APP

# Validate required variables
python3 -c "import os; print('MONGO_URL:', os.getenv('MONGO_URL', 'NOT SET'))"
```

#### Environment File Loading
```bash
# Verify file exists
ls -la .env

# Check file permissions
ls -la .env
# Should be readable: -rw-------

# Verify file content (be careful with secrets)
head -n 5 .env
```

#### Variable Precedence
Environment variables are loaded in this order (later overrides earlier):
1. System environment variables
2. `.env` file
3. `.env.local` file (frontend)
4. `.env.development` / `.env.production` file
5. Command line arguments

### Debugging Tools

#### Environment Variable Checker Script
```bash
#!/bin/bash
# check_env.sh

echo "=== Environment Variable Check ==="

# Required backend variables
required_backend=(
    "MONGO_URL"
    "DB_NAME"
    "SECRET_KEY"
)

# Required frontend variables
required_frontend=(
    "REACT_APP_BACKEND_URL"
)

echo "Backend Variables:"
for var in "${required_backend[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ $var: NOT SET"
    else
        echo "✅ $var: SET"
    fi
done

echo "Frontend Variables:"
for var in "${required_frontend[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ $var: NOT SET"
    else
        echo "✅ $var: SET"
    fi
done
```

#### Python Environment Validator
```python
#!/usr/bin/env python3
# validate_env.py

import os
import sys
from typing import List, Tuple

def validate_environment() -> List[Tuple[str, bool, str]]:
    """Validate all required environment variables."""
    
    required_vars = [
        ("MONGO_URL", True, "Database connection string"),
        ("DB_NAME", True, "Database name"),
        ("SECRET_KEY", True, "JWT secret key"),
        ("LOG_LEVEL", False, "Logging level"),
        ("UPLOAD_DIR", False, "Upload directory"),
    ]
    
    results = []
    
    for var_name, required, description in required_vars:
        value = os.getenv(var_name)
        is_set = bool(value and value.strip())
        results.append((var_name, is_set, description))
        
        # Additional validation
        if var_name == "SECRET_KEY" and is_set:
            if len(value) < 32:
                print(f"⚠️  {var_name}: Too short (minimum 32 characters)")
        
        if var_name == "MONGO_URL" and is_set:
            if not value.startswith("mongodb://") and not value.startswith("mongodb+srv://"):
                print(f"⚠️  {var_name}: Invalid MongoDB URL format")
    
    return results

def main():
    print("🔍 Environment Variable Validation")
    print("=" * 40)
    
    results = validate_environment()
    all_required_set = True
    
    for var_name, is_set, description in results:
        status = "✅" if is_set else "❌"
        print(f"{status} {var_name}: {description}")
        
        if not is_set:
            all_required_set = False
    
    print("=" * 40)
    
    if all_required_set:
        print("✅ All required environment variables are set!")
        sys.exit(0)
    else:
        print("❌ Some required environment variables are missing!")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 📚 References

### Official Documentation
- [FastAPI Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
- [React Environment Variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)
- [MongoDB Connection URI](https://docs.mongodb.com/manual/reference/connection-string/)

### Security Resources
- [OWASP Configuration](https://owasp.org/www-project-top-ten/2017/A6_2017-Security_Misconfiguration)
- [JWT Security Best Practices](https://tools.ietf.org/html/rfc8725)
- [Environment Variable Security](https://12factor.net/config)

### Tools and Utilities
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Python environment loading
- [cross-env](https://www.npmjs.com/package/cross-env) - Cross-platform environment variables
- [env-cmd](https://www.npmjs.com/package/env-cmd) - Environment file execution

---

For additional help with environment configuration, please contact the development team or refer to the main documentation.