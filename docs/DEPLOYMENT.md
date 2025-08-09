# AnnaiCONNECT Production Deployment Guide

## 🚀 Overview

This guide covers deploying AnnaiCONNECT to production environments with high availability, security, and performance considerations.

## 📋 Pre-Deployment Checklist

### System Requirements
- [ ] **Server Specifications**: 
  - CPU: 4+ cores
  - RAM: 8GB+ (16GB recommended)
  - Storage: 100GB+ SSD
  - Network: 100Mbps+ bandwidth

- [ ] **Software Requirements**:
  - Ubuntu 20.04+ or CentOS 8+
  - Python 3.11+
  - Node.js 18+
  - MongoDB 5.0+
  - Nginx 1.18+
  - SSL certificates

- [ ] **Security Requirements**:
  - Firewall configured
  - SSH key-based authentication
  - Non-root user with sudo privileges
  - SSL/TLS certificates ready

---

## 🏗️ Infrastructure Setup

### 1. Server Provisioning

#### Cloud Provider Setup (AWS/Azure/GCP)
```bash
# AWS EC2 instance
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx
```

#### Basic Server Hardening
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Create application user
sudo useradd -m -s /bin/bash annaiconnect
sudo usermod -aG sudo annaiconnect

# Setup SSH keys
sudo mkdir -p /home/annaiconnect/.ssh
sudo cp ~/.ssh/authorized_keys /home/annaiconnect/.ssh/
sudo chown -R annaiconnect:annaiconnect /home/annaiconnect/.ssh
sudo chmod 700 /home/annaiconnect/.ssh
sudo chmod 600 /home/annaiconnect/.ssh/authorized_keys
```

### 2. Firewall Configuration

```bash
# Setup UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from your-admin-ip to any port 22

# Check status
sudo ufw status verbose
```

### 3. Install System Dependencies

```bash
# System packages
sudo apt install -y curl wget git vim htop unzip \
  software-properties-common apt-transport-https \
  ca-certificates gnupg lsb-release

# Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev

# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Yarn
npm install -g yarn

# MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Nginx
sudo apt install -y nginx

# Certbot for SSL
sudo apt install -y certbot python3-certbot-nginx
```

---

## 📦 Application Deployment

### 1. Deploy Application Code

```bash
# Switch to application user
sudo su - annaiconnect

# Clone repository
git clone <repository-url> /opt/annaiconnect
cd /opt/annaiconnect

# Set correct permissions
sudo chown -R annaiconnect:annaiconnect /opt/annaiconnect
```

### 2. Backend Deployment

```bash
cd /opt/annaiconnect/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install production server
pip install gunicorn

# Create production environment file
cat > .env << EOF
MONGO_URL=mongodb://annaiconnect_user:SECURE_PASSWORD@localhost:27017/annaiconnect_production
DB_NAME=annaiconnect_production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ALGORITHM=HS256
EOF

# Set secure permissions
chmod 600 .env
```

### 3. Frontend Deployment

```bash
cd /opt/annaiconnect/frontend

# Install dependencies
yarn install --frozen-lockfile

# Create production environment file
cat > .env << EOF
REACT_APP_BACKEND_URL=https://api.yourdomain.com
WDS_SOCKET_PORT=443
EOF

# Build for production
yarn build

# Set permissions
sudo chown -R www-data:www-data build/
```

### 4. Database Setup

#### MongoDB Configuration
```bash
# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Secure MongoDB installation
sudo mongo --eval "
use admin
db.createUser({
  user: 'admin',
  pwd: 'SECURE_ADMIN_PASSWORD',
  roles: ['root']
})
"

# Create application database and user
sudo mongo -u admin -p SECURE_ADMIN_PASSWORD --authenticationDatabase admin --eval "
use annaiconnect_production
db.createUser({
  user: 'annaiconnect_user',
  pwd: 'SECURE_APP_PASSWORD',
  roles: ['readWrite']
})
"

# Configure MongoDB for production
sudo tee /etc/mongod.conf << EOF
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1

security:
  authorization: enabled

processManagement:
  fork: true
  pidFilePath: /var/run/mongodb/mongod.pid
  timeZoneInfo: /usr/share/zoneinfo
EOF

# Restart MongoDB
sudo systemctl restart mongod
```

---

## 🔧 Service Configuration

### 1. Backend Service (Systemd)

```bash
# Create systemd service file
sudo tee /etc/systemd/system/annaiconnect-backend.service << EOF
[Unit]
Description=AnnaiCONNECT Backend Service
After=network.target mongodb.service
Requires=mongodb.service

[Service]
Type=exec
User=annaiconnect
Group=annaiconnect
WorkingDirectory=/opt/annaiconnect/backend
Environment=PATH=/opt/annaiconnect/backend/venv/bin
ExecStart=/opt/annaiconnect/backend/venv/bin/gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8001 --access-logfile /var/log/annaiconnect/access.log --error-logfile /var/log/annaiconnect/error.log
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
sudo mkdir -p /var/log/annaiconnect
sudo chown annaiconnect:annaiconnect /var/log/annaiconnect

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable annaiconnect-backend
sudo systemctl start annaiconnect-backend

# Check status
sudo systemctl status annaiconnect-backend
```

### 2. Nginx Configuration

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/annaiconnect << EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Frontend (React)
    location / {
        root /opt/annaiconnect/frontend/build;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        
        # Special rate limiting for login
        location /api/login {
            proxy_pass http://127.0.0.1:8001;
            limit_req zone=login burst=3 nodelay;
        }
    }

    # File uploads (larger body size)
    location /api/students {
        proxy_pass http://127.0.0.1:8001;
        client_max_body_size 50M;
        proxy_request_buffering off;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/annaiconnect /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 3. SSL Certificate Setup

```bash
# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Setup auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## 🗄️ Database Management

### 1. Production Data Setup

```bash
# Run the production deployment endpoint
# First, manually create a temporary admin user or use development credentials
# Then call the endpoint:

curl -X POST "https://yourdomain.com/api/admin/deploy-production" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

This will:
- Clean all test data
- Create production users:
  - Admin: `super admin` / `Admin@annaiconnect`
  - Coordinator: `arulanantham` / `Arul@annaiconnect`
  - Agents: `agent1`, `agent2`, `agent3` / `agent@123`
- Setup production courses (B.Ed: ₹6000, MBA: ₹2500, BNYS: ₹20000)

### 2. Database Backup Strategy

```bash
# Create backup script
sudo tee /opt/annaiconnect/scripts/backup.sh << 'EOF'
#!/bin/bash

# Configuration
DB_NAME="annaiconnect_production"
BACKUP_DIR="/opt/annaiconnect/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
mongodump --db $DB_NAME --out $BACKUP_DIR/mongo_$DATE

# Compress backup
tar -czf $BACKUP_DIR/annaiconnect_backup_$DATE.tar.gz -C $BACKUP_DIR mongo_$DATE

# Clean up uncompressed backup
rm -rf $BACKUP_DIR/mongo_$DATE

# Remove old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Log backup
echo "$(date): Backup completed - annaiconnect_backup_$DATE.tar.gz" >> /var/log/annaiconnect/backup.log
EOF

# Make executable
sudo chmod +x /opt/annaiconnect/scripts/backup.sh

# Setup cron job for daily backups
sudo crontab -e
# Add line: 0 2 * * * /opt/annaiconnect/scripts/backup.sh
```

### 3. Database Indexing

```bash
# Connect to MongoDB and create performance indexes
mongosh -u annaiconnect_user -p SECURE_APP_PASSWORD annaiconnect_production

# Run these commands in MongoDB shell:
db.students.createIndex({ "token_number": 1 }, { unique: true })
db.students.createIndex({ "agent_id": 1 })
db.students.createIndex({ "status": 1 })
db.students.createIndex({ "created_at": -1 })
db.students.createIndex({ "course": 1 })
db.students.createIndex({ "email": 1 })

db.users.createIndex({ "username": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "role": 1 })

db.incentives.createIndex({ "agent_id": 1 })
db.incentives.createIndex({ "student_id": 1 })
db.incentives.createIndex({ "status": 1 })
db.incentives.createIndex({ "created_at": -1 })

db.incentive_rules.createIndex({ "course": 1 })
db.incentive_rules.createIndex({ "active": 1 })
```

---

## 📊 Monitoring & Logging

### 1. Log Management

```bash
# Setup log rotation
sudo tee /etc/logrotate.d/annaiconnect << EOF
/var/log/annaiconnect/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 annaiconnect annaiconnect
    postrotate
        systemctl reload annaiconnect-backend
    endscript
}

/var/log/nginx/access.log /var/log/nginx/error.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    postrotate
        nginx -s reload
    endscript
}
EOF
```

### 2. System Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Create monitoring script
sudo tee /opt/annaiconnect/scripts/monitor.sh << 'EOF'
#!/bin/bash

# Check services
echo "=== Service Status ===" >> /var/log/annaiconnect/monitor.log
systemctl is-active --quiet annaiconnect-backend && echo "Backend: OK" || echo "Backend: FAILED"
systemctl is-active --quiet nginx && echo "Nginx: OK" || echo "Nginx: FAILED"
systemctl is-active --quiet mongod && echo "MongoDB: OK" || echo "MongoDB: FAILED"

# Check disk space
echo "=== Disk Usage ===" >> /var/log/annaiconnect/monitor.log
df -h | grep -E "(/$|/opt)"

# Check memory usage
echo "=== Memory Usage ===" >> /var/log/annaiconnect/monitor.log
free -h

# Check application health
echo "=== Application Health ===" >> /var/log/annaiconnect/monitor.log
curl -s http://localhost:8001/api/health || echo "API Health Check Failed"

echo "--- $(date) ---" >> /var/log/annaiconnect/monitor.log
EOF

# Make executable
sudo chmod +x /opt/annaiconnect/scripts/monitor.sh

# Setup cron job for monitoring
sudo crontab -e
# Add line: */5 * * * * /opt/annaiconnect/scripts/monitor.sh
```

### 3. Application Performance Monitoring

```bash
# Install performance monitoring tools
pip install psutil

# Create performance monitoring script
sudo tee /opt/annaiconnect/scripts/performance.py << 'EOF'
#!/usr/bin/env python3
import psutil
import requests
import json
import time
from datetime import datetime

def check_system_metrics():
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'timestamp': datetime.now().isoformat()
    }

def check_api_response_time():
    try:
        start_time = time.time()
        response = requests.get('http://localhost:8001/api/health', timeout=10)
        response_time = (time.time() - start_time) * 1000
        return {
            'status_code': response.status_code,
            'response_time_ms': response_time,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    system_metrics = check_system_metrics()
    api_metrics = check_api_response_time()
    
    with open('/var/log/annaiconnect/performance.log', 'a') as f:
        f.write(f"SYSTEM: {json.dumps(system_metrics)}\n")
        f.write(f"API: {json.dumps(api_metrics)}\n")
EOF

# Make executable
sudo chmod +x /opt/annaiconnect/scripts/performance.py

# Setup cron job for performance monitoring
sudo crontab -e
# Add line: */1 * * * * /opt/annaiconnect/scripts/performance.py
```

---

## 🔒 Security Hardening

### 1. Application Security

```bash
# Create security configuration
sudo tee /opt/annaiconnect/backend/security.py << 'EOF'
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

def setup_security_middleware(app):
    # HTTPS redirect
    app.add_middleware(HTTPSRedirectMiddleware)
    
    # Trusted hosts
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
EOF
```

### 2. MongoDB Security

```bash
# Update MongoDB configuration for security
sudo tee -a /etc/mongod.conf << EOF

# Security enhancements
security:
  authorization: enabled
  
# Network security
net:
  bindIp: 127.0.0.1
  port: 27017
  
# Logging
systemLog:
  verbosity: 1
  component:
    accessControl:
      verbosity: 2
    command:
      verbosity: 2
EOF

# Restart MongoDB
sudo systemctl restart mongod
```

### 3. System Security

```bash
# Install fail2ban
sudo apt install -y fail2ban

# Configure fail2ban for SSH
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600
EOF

# Start fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Setup automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 🚀 Performance Optimization

### 1. Nginx Optimization

```bash
# Update Nginx configuration for performance
sudo tee /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
    multi_accept on;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Include mime types and site configurations
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Include site configurations
    include /etc/nginx/sites-enabled/*;
}
EOF

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 2. MongoDB Optimization

```bash
# Update MongoDB configuration for performance
sudo tee -a /etc/mongod.conf << EOF

# Performance tuning
operationProfiling:
  slowOpThresholdMs: 100
  mode: slowOp

# Storage engine optimization
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2
      journalCompressor: snappy
      directoryForIndexes: false
    collectionConfig:
      blockCompressor: snappy
    indexConfig:
      prefixCompression: true
EOF

# Restart MongoDB
sudo systemctl restart mongod
```

### 3. Application Optimization

```bash
# Install Redis for caching (optional)
sudo apt install -y redis-server

# Configure Redis
sudo sed -i 's/# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
sudo sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf

# Start Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Update backend to use Redis caching
pip install redis
```

---

## 🔄 Deployment Automation

### 1. Create Deployment Script

```bash
sudo tee /opt/annaiconnect/scripts/deploy.sh << 'EOF'
#!/bin/bash

set -e

echo "Starting AnnaiCONNECT deployment..."

# Configuration
APP_DIR="/opt/annaiconnect"
BACKUP_DIR="/opt/annaiconnect/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Function to backup current deployment
backup_current() {
    echo "Creating backup of current deployment..."
    mkdir -p $BACKUP_DIR/deployments
    tar -czf $BACKUP_DIR/deployments/deployment_backup_$DATE.tar.gz -C $APP_DIR --exclude=backups .
}

# Function to update backend
update_backend() {
    echo "Updating backend..."
    cd $APP_DIR/backend
    source venv/bin/activate
    git pull origin main
    pip install -r requirements.txt
    sudo systemctl restart annaiconnect-backend
}

# Function to update frontend
update_frontend() {
    echo "Updating frontend..."
    cd $APP_DIR/frontend
    git pull origin main
    yarn install --frozen-lockfile
    yarn build
    sudo chown -R www-data:www-data build/
    sudo systemctl reload nginx
}

# Function to run database migrations (if any)
run_migrations() {
    echo "Running database migrations..."
    cd $APP_DIR/backend
    source venv/bin/activate
    # Add migration commands here if needed
}

# Function to verify deployment
verify_deployment() {
    echo "Verifying deployment..."
    
    # Check backend health
    if curl -f http://localhost:8001/api/health > /dev/null 2>&1; then
        echo "✓ Backend health check passed"
    else
        echo "✗ Backend health check failed"
        exit 1
    fi
    
    # Check frontend
    if curl -f http://localhost > /dev/null 2>&1; then
        echo "✓ Frontend health check passed"
    else
        echo "✗ Frontend health check failed"
        exit 1
    fi
    
    # Check services
    if systemctl is-active --quiet annaiconnect-backend; then
        echo "✓ Backend service running"
    else
        echo "✗ Backend service not running"
        exit 1
    fi
    
    if systemctl is-active --quiet nginx; then
        echo "✓ Nginx service running"
    else
        echo "✗ Nginx service not running"
        exit 1
    fi
}

# Main deployment process
main() {
    echo "=== AnnaiCONNECT Deployment Started at $(date) ==="
    
    backup_current
    update_backend
    update_frontend
    run_migrations
    verify_deployment
    
    echo "=== Deployment completed successfully at $(date) ==="
    echo "Deployment log: /var/log/annaiconnect/deploy.log"
}

# Run deployment
main 2>&1 | tee -a /var/log/annaiconnect/deploy.log
EOF

# Make executable
sudo chmod +x /opt/annaiconnect/scripts/deploy.sh
```

### 2. Setup CI/CD (GitHub Actions Example)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/annaiconnect
          sudo -u annaiconnect ./scripts/deploy.sh
```

---

## 📋 Post-Deployment Checklist

### Immediate Verification
- [ ] All services running (backend, nginx, mongodb)
- [ ] SSL certificate working
- [ ] API endpoints responding
- [ ] Frontend loading correctly
- [ ] Database connectivity confirmed
- [ ] Login functionality working
- [ ] File upload working

### Security Verification
- [ ] Firewall rules active
- [ ] SSL/TLS configuration correct
- [ ] Security headers present
- [ ] Rate limiting working
- [ ] Authentication working
- [ ] Authorization working correctly

### Performance Verification
- [ ] Page load times acceptable (<3 seconds)
- [ ] API response times good (<500ms)
- [ ] Database queries optimized
- [ ] Caching working (if implemented)
- [ ] Compression enabled
- [ ] CDN configured (if applicable)

### Monitoring Setup
- [ ] Log rotation configured
- [ ] Backup scripts working
- [ ] Monitoring scripts active
- [ ] Performance tracking enabled
- [ ] Alert notifications configured
- [ ] Health checks running

---

## 🆘 Rollback Procedures

### Quick Rollback Script

```bash
sudo tee /opt/annaiconnect/scripts/rollback.sh << 'EOF'
#!/bin/bash

set -e

BACKUP_DIR="/opt/annaiconnect/backups/deployments"
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -la $BACKUP_DIR/
    exit 1
fi

echo "Rolling back to $BACKUP_FILE..."

# Stop services
sudo systemctl stop annaiconnect-backend
sudo systemctl stop nginx

# Restore backup
cd /opt/annaiconnect
tar -xzf $BACKUP_DIR/$BACKUP_FILE --exclude=backups

# Set permissions
sudo chown -R annaiconnect:annaiconnect /opt/annaiconnect
sudo chown -R www-data:www-data /opt/annaiconnect/frontend/build

# Restart services
sudo systemctl start annaiconnect-backend
sudo systemctl start nginx

echo "Rollback completed. Please verify the application."
EOF

sudo chmod +x /opt/annaiconnect/scripts/rollback.sh
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Review application logs
   - Check system resource usage
   - Verify backup integrity
   - Review security logs

2. **Monthly**:
   - Update system packages
   - Review and rotate logs
   - Performance optimization review
   - Security audit

3. **Quarterly**:
   - Dependency updates
   - Security penetration testing
   - Disaster recovery testing
   - Capacity planning review

### Emergency Contacts

- **System Administrator**: your-admin@company.com
- **Developer Team**: dev-team@company.com
- **Database Administrator**: dba@company.com
- **Security Team**: security@company.com

### Useful Commands

```bash
# Service management
sudo systemctl status annaiconnect-backend
sudo systemctl restart annaiconnect-backend
sudo systemctl reload nginx

# Log monitoring
sudo tail -f /var/log/annaiconnect/error.log
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u annaiconnect-backend -f

# Database operations
mongosh -u annaiconnect_user -p annaiconnect_production
mongodump --db annaiconnect_production --out backup_$(date +%Y%m%d)

# Performance monitoring
htop
iotop
nethogs
```

---

Your AnnaiCONNECT application is now successfully deployed to production! 🎉

For ongoing support and maintenance, please refer to the monitoring and maintenance sections of this guide.