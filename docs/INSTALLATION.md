# AnnaiCONNECT Installation Guide

## 📋 Prerequisites

Before installing AnnaiCONNECT, ensure your system meets the following requirements:

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 10GB free space
- **Network**: Internet connection for dependency installation

### Software Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **MongoDB**: 5.0 or higher
- **Yarn**: 1.22 or higher (package manager)
- **Git**: For version control

---

## 🔧 Environment Setup

### 1. Install Python 3.11+

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

#### macOS:
```bash
# Using Homebrew
brew install python@3.11
```

#### Windows:
Download from [python.org](https://www.python.org/downloads/) and install.

### 2. Install Node.js 18+

#### Ubuntu/Debian:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### macOS:
```bash
# Using Homebrew
brew install node@18
```

#### Windows:
Download from [nodejs.org](https://nodejs.org/) and install.

### 3. Install MongoDB

#### Ubuntu/Debian:
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### macOS:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community@5.0
brew services start mongodb/brew/mongodb-community
```

#### Windows:
Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community) and follow the installation wizard.

### 4. Install Yarn

```bash
npm install -g yarn
```

### 5. Verify Installations

```bash
python3 --version    # Should show 3.11+
node --version       # Should show 18+
npm --version        # Should show 8+
yarn --version       # Should show 1.22+
mongosh --version    # Should show MongoDB shell version
```

---

## 📦 Application Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd annaiconnect
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd backend
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Create Environment File
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=annaiconnect_development
SECRET_KEY=your-secret-key-here-minimum-32-characters
ALGORITHM=HS256
```

### 3. Frontend Setup

```bash
cd ../frontend
yarn install
```

#### Create Environment File
```bash
cp .env.example .env
```

Edit `.env` file:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
```

### 4. Database Setup

#### Start MongoDB (if not already running)
```bash
# Linux:
sudo systemctl start mongod

# macOS:
brew services start mongodb/brew/mongodb-community

# Windows:
net start MongoDB
```

#### Create Database and Collections
```bash
# Connect to MongoDB
mongosh

# Create database
use annaiconnect_development

# The application will automatically create collections on first run
```

---

## 🚀 Running the Application

### Development Mode

#### Option 1: Using Separate Terminals

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn start
```

#### Option 2: Using Process Manager (Recommended)

Create `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [
    {
      name: 'annaiconnect-backend',
      script: 'uvicorn',
      args: 'server:app --host 0.0.0.0 --port 8001 --reload',
      cwd: './backend',
      interpreter: './backend/venv/bin/python'
    },
    {
      name: 'annaiconnect-frontend',
      script: 'yarn',
      args: 'start',
      cwd: './frontend'
    }
  ]
};
```

Install PM2 and run:
```bash
npm install -g pm2
pm2 start ecosystem.config.js
```

### Production Mode

#### Backend Production Setup
```bash
cd backend
source venv/bin/activate

# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

#### Frontend Production Setup
```bash
cd frontend
yarn build

# Serve static files
npm install -g serve
serve -s build -l 3000
```

---

## 🔐 Production Environment Configuration

### 1. Environment Variables

#### Backend Production (.env)
```env
MONGO_URL=mongodb://production-server:27017
DB_NAME=annaiconnect_production
SECRET_KEY=secure-production-key-minimum-32-characters-very-secure
ALGORITHM=HS256
```

#### Frontend Production (.env)
```env
REACT_APP_BACKEND_URL=https://api.yourdomain.com
WDS_SOCKET_PORT=443
```

### 2. MongoDB Production Setup

#### Create Production Database
```bash
mongosh
use annaiconnect_production
db.createUser({
  user: "annaiconnect_user",
  pwd: "secure_password_here",
  roles: ["readWrite"]
})
```

#### Update connection string
```env
MONGO_URL=mongodb://annaiconnect_user:secure_password_here@localhost:27017/annaiconnect_production
```

### 3. SSL/TLS Configuration

#### Backend with SSL
```bash
# Generate SSL certificates (using Let's Encrypt)
sudo apt install certbot
sudo certbot certonly --standalone -d api.yourdomain.com

# Run with SSL
uvicorn server:app --host 0.0.0.0 --port 8001 --ssl-keyfile=/etc/letsencrypt/live/api.yourdomain.com/privkey.pem --ssl-certfile=/etc/letsencrypt/live/api.yourdomain.com/fullchain.pem
```

#### Frontend with SSL (using Nginx)
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🐳 Docker Installation (Optional)

### 1. Create Dockerfile for Backend

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 2. Create Dockerfile for Frontend

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
RUN yarn build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
```

### 3. Create Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:5.0
    container_name: annaiconnect-mongo
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: secure_password
      MONGO_INITDB_DATABASE: annaiconnect_production
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

  backend:
    build: ./backend
    container_name: annaiconnect-backend
    restart: unless-stopped
    environment:
      MONGO_URL: mongodb://admin:secure_password@mongodb:27017/annaiconnect_production?authSource=admin
      DB_NAME: annaiconnect_production
      SECRET_KEY: your-secure-secret-key-here
    depends_on:
      - mongodb
    ports:
      - "8001:8001"

  frontend:
    build: ./frontend
    container_name: annaiconnect-frontend
    restart: unless-stopped
    environment:
      REACT_APP_BACKEND_URL: http://localhost:8001
    depends_on:
      - backend
    ports:
      - "3000:3000"

volumes:
  mongodb_data:
```

### 4. Run with Docker

```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ✅ Post-Installation Setup

### 1. Initial Data Setup

#### Run Production Deployment
```bash
# Start the application
# Login as temporary admin (create manually or use development credentials)
# Call the production deployment endpoint:

curl -X POST "http://localhost:8001/api/admin/deploy-production" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

This will:
- Clean all test data
- Create production users
- Setup production courses

### 2. Verify Installation

#### Backend Health Check
```bash
curl http://localhost:8001/api/health
```

#### Frontend Check
Open browser and navigate to `http://localhost:3000`

#### Database Check
```bash
mongosh
use annaiconnect_production
db.users.find().pretty()
```

### 3. Login with Production Credentials

- **Admin**: `super admin` / `Admin@annaiconnect`
- **Coordinator**: `arulanantham` / `Arul@annaiconnect`
- **Agents**: `agent1`, `agent2`, `agent3` / `agent@123`

---

## 🔧 Troubleshooting Installation

### Common Issues

#### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8001
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>
```

#### MongoDB Connection Issues
```bash
# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

#### Python Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Node.js/Yarn Issues
```bash
# Clear cache
npm cache clean --force
yarn cache clean

# Remove node_modules and reinstall
rm -rf node_modules yarn.lock
yarn install
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER /path/to/annaiconnect
chmod +x scripts/*
```

### Performance Optimization

#### MongoDB Index Creation
```javascript
// Connect to MongoDB and create indexes
mongosh

use annaiconnect_production

// Create indexes for better performance
db.students.createIndex({ "token_number": 1 })
db.students.createIndex({ "agent_id": 1 })
db.students.createIndex({ "status": 1 })
db.students.createIndex({ "created_at": -1 })
db.students.createIndex({ "course": 1 })

db.users.createIndex({ "username": 1 })
db.users.createIndex({ "email": 1 })
db.users.createIndex({ "role": 1 })

db.incentives.createIndex({ "agent_id": 1 })
db.incentives.createIndex({ "status": 1 })
db.incentives.createIndex({ "created_at": -1 })
```

#### System Resource Optimization
```bash
# Increase MongoDB connection limits
echo "* soft nofile 64000" >> /etc/security/limits.conf
echo "* hard nofile 64000" >> /etc/security/limits.conf

# Optimize MongoDB configuration
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
sysctl -p
```

---

## 📊 Monitoring & Logging

### 1. Setup Log Rotation

Create `/etc/logrotate.d/annaiconnect`:
```
/var/log/annaiconnect/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    postrotate
        systemctl restart annaiconnect-backend
    endscript
}
```

### 2. Setup System Service

Create `/etc/systemd/system/annaiconnect-backend.service`:
```ini
[Unit]
Description=AnnaiCONNECT Backend Service
After=network.target mongodb.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/annaiconnect/backend
Environment=PATH=/opt/annaiconnect/backend/venv/bin
ExecStart=/opt/annaiconnect/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable annaiconnect-backend
sudo systemctl start annaiconnect-backend
```

---

## 🔄 Maintenance

### Regular Tasks

#### 1. Backup Database
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --db annaiconnect_production --out /backups/mongo_$DATE
tar -czf /backups/annaiconnect_backup_$DATE.tar.gz /backups/mongo_$DATE
rm -rf /backups/mongo_$DATE
```

#### 2. Update Dependencies
```bash
# Backend updates
cd backend
source venv/bin/activate
pip list --outdated
pip install --upgrade package_name

# Frontend updates
cd frontend
yarn outdated
yarn upgrade package_name
```

#### 3. Security Updates
```bash
# System updates
sudo apt update && sudo apt upgrade

# Python security updates
pip install --upgrade pip
pip audit

# Node.js security updates
yarn audit
yarn audit fix
```

---

## 📞 Support

If you encounter issues during installation:

1. **Check Prerequisites**: Ensure all required software is installed and up-to-date
2. **Review Logs**: Check application logs for specific error messages
3. **Verify Configuration**: Double-check environment variables and configuration files
4. **Test Dependencies**: Verify each component works independently
5. **Consult Documentation**: Review the troubleshooting section

For additional support, please contact the development team with:
- Operating system and version
- Error messages and logs
- Steps already attempted
- System configuration details

---

Installation complete! Your AnnaiCONNECT system is now ready for use.