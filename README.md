# AnnaiCONNECT - Admission Management System

## 📋 Overview

AnnaiCONNECT is a comprehensive student admissions management platform that streamlines the entire admission process from student registration to final approval. The system supports a 3-tier approval workflow with role-based access control, automated incentive management, and comprehensive reporting capabilities.

## 🏗️ Architecture

- **Frontend**: React 19 with Tailwind CSS and Shadcn UI components
- **Backend**: FastAPI with async/await support
- **Database**: MongoDB with Motor async driver
- **Authentication**: JWT tokens with role-based access control
- **File Storage**: Local filesystem with async file handling

## ✨ Key Features

### Multi-Role System
- **Agents**: Create student applications, upload documents, track incentives
- **Coordinators**: Review applications, approve/reject with e-signatures, manage documents
- **Admins**: Final approval, user management, system configuration, reports

### Core Functionality
- **3-Tier Approval Process**: Agent → Coordinator → Admin
- **E-Signature Integration**: Digital signature pad and image upload
- **Document Management**: PDF, JPG, PNG file uploads with download capabilities
- **Automated Token Generation**: Systematic AGI token format (AGI2508001, etc.)
- **PDF Receipt Generation**: Automated receipt creation with signatures
- **Excel Export**: Comprehensive reporting with filters
- **Incentive Management**: Automated calculation and tracking
- **Leaderboard System**: Overall, weekly, monthly, and custom date range rankings

### Modern UI/UX
- **Responsive Design**: Mobile, tablet, and desktop optimized
- **Modern Theme System**: Professional gradient styling
- **Pagination & Filtering**: Advanced search and filter capabilities
- **Real-time Updates**: Live data synchronization

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 5.0+
- Yarn package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd annaiconnect
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure environment variables
```

3. **Frontend Setup**
```bash
cd ../frontend
yarn install
cp .env.example .env  # Configure environment variables
```

4. **Database Setup**
```bash
# Start MongoDB service
sudo systemctl start mongod  # Linux
brew services start mongodb  # macOS
```

### Running the Application

#### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

#### Production Mode

**Using Supervisor (Recommended):**
```bash
sudo supervisorctl restart all
```

**Manual Production Setup:**
```bash
# Backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend
cd frontend
yarn build
serve -s build -l 3000
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=annaiconnect_production
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

#### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
```

### Production Environment Variables

#### Backend Production
```env
MONGO_URL=mongodb://production-host:27017
DB_NAME=annaiconnect_production
SECRET_KEY=secure-production-key-32-chars-min
ALGORITHM=HS256
```

#### Frontend Production
```env
REACT_APP_BACKEND_URL=https://your-production-api.com
WDS_SOCKET_PORT=443
```

## 🔑 Production Deployment

### Automated Production Setup

AnnaiCONNECT includes a one-click production deployment system:

```bash
# Login as admin and call the deployment endpoint
curl -X POST "http://localhost:8001/api/admin/deploy-production" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

This will:
1. **Clean all test data** from database
2. **Create production users**:
   - Admin: `super admin` / `Admin@annaiconnect`
   - Coordinator: `arulanantham` / `Arul@annaiconnect`
   - Agent1: `agent1` / `agent@123`
   - Agent2: `agent2` / `agent@123`
   - Agent3: `agent3` / `agent@123`
3. **Setup production courses**:
   - B.Ed: ₹6,000 incentive
   - MBA: ₹2,500 incentive
   - BNYS: ₹20,000 incentive

### Manual Production Steps

1. **Database Backup**
```bash
mongodump --db annaiconnect_production --out backup-$(date +%Y%m%d)
```

2. **Deploy Code**
```bash
git pull origin main
cd backend && pip install -r requirements.txt
cd ../frontend && yarn install && yarn build
```

3. **Update Environment Variables**
```bash
# Update production URLs and secrets
vi backend/.env
vi frontend/.env
```

4. **Restart Services**
```bash
sudo supervisorctl restart all
```

5. **Run Production Setup**
```bash
# Call the deployment API or manual setup
curl -X POST "https://your-api.com/api/admin/deploy-production"
```

## 📊 User Roles & Permissions

### Agent Role
- Create student applications
- Upload documents (ID, certificates, etc.)
- View own students and their status
- Track personal incentives and performance
- Download receipts for approved students
- Update profile information

### Coordinator Role
- Review all student applications
- Approve/reject applications with e-signatures
- View and download student documents
- Access paginated student dashboard with filters
- Generate coordinator approval receipts
- Manage student document verification

### Admin Role
- Final approval of coordinator-approved students
- Complete user management (create, approve, deactivate)
- Course and incentive rule management
- System configuration and signature management
- Generate comprehensive reports and exports
- Access leaderboard and performance analytics
- Database backup and system maintenance
- Admin-generated PDF receipts

## 🔗 API Documentation

### Authentication Endpoints

#### POST /api/register
Register new user (requires admin approval)
```json
{
  "username": "string",
  "email": "string", 
  "password": "string",
  "role": "agent|coordinator|admin",
  "first_name": "string",
  "last_name": "string",
  "agent_id": "string (agents only)"
}
```

#### POST /api/login
User authentication
```json
{
  "username": "string",
  "password": "string"
}
```

#### GET /api/me
Get current user information
- Headers: `Authorization: Bearer <token>`

### Student Management

#### POST /api/students
Create new student application (agents only)
```json
{
  "first_name": "string",
  "last_name": "string", 
  "email": "string",
  "phone": "string",
  "course": "string"
}
```

#### GET /api/students
Get students list (role-based filtering)
- Query params: `status`, `course`, `agent_id`

#### GET /api/students/paginated
Get paginated students with filters (coordinators/admins)
- Query params: `page`, `limit`, `status`, `course`, `agent_id`, `search`, `date_from`, `date_to`

#### PUT /api/students/{id}/status
Update student status (coordinators/admins)
```json
{
  "status": "approved|rejected|coordinator_approved",
  "notes": "string",
  "signature_data": "base64_string (optional)",
  "signature_type": "draw|upload (optional)"
}
```

#### POST /api/students/{id}/upload
Upload student documents
- Form data: `document_type`, `file`

#### GET /api/students/{id}/receipt
Download PDF receipt (approved students only)

### Admin Management

#### GET /api/admin/dashboard-enhanced
Get comprehensive admin dashboard data
```json
{
  "admissions": {
    "total": "number",
    "pending": "number", 
    "approved": "number",
    "rejected": "number"
  },
  "agents": {"total": "number", "active": "number"},
  "incentives": {"total_amount": "number", "paid_amount": "number"}
}
```

#### GET /api/admin/pending-approvals
Get students awaiting admin final approval

#### PUT /api/admin/approve-student/{id}
Final admin approval
```json
{
  "notes": "string"
}
```

#### GET /api/admin/export/excel
Export comprehensive Excel report
- Query params: `start_date`, `end_date`, `agent_id`, `course`, `status`

#### POST /api/admin/deploy-production
Complete production deployment (cleanup + setup)

### Course Management

#### GET /api/incentive-rules
Get active courses and incentive amounts

#### POST /api/admin/courses
Create new course (admins only)
```json
{
  "course": "string",
  "amount": "number"
}
```

#### PUT /api/admin/courses/{id}
Update course information

#### DELETE /api/admin/courses/{id}
Soft delete course (sets active=false)

### Leaderboard & Analytics

#### GET /api/leaderboard/overall
Get overall agent performance rankings

#### GET /api/leaderboard/weekly
Get current week performance

#### GET /api/leaderboard/monthly
Get current month performance

#### GET /api/leaderboard/date-range
Get custom date range performance
- Query params: `start_date`, `end_date`

### Profile Management

#### GET /api/profile
Get current user profile (agents)

#### PUT /api/profile
Update profile information
```json
{
  "phone": "string",
  "address": "string",
  "experience_level": "beginner|intermediate|expert",
  "specializations": ["string"],
  "monthly_target": "number",
  "bio": "string"
}
```

#### POST /api/profile/upload-photo
Upload profile photo
- Form data: `file`

## 🛠️ Development

### Code Structure

```
/app
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   ├── App.css       # Global styles
│   │   └── components/   # Reusable UI components
│   ├── package.json      # Node.js dependencies
│   └── .env             # Frontend environment variables
├── scripts/             # Utility scripts
└── docs/               # Documentation
```

### Testing

#### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

#### Frontend Testing
```bash
cd frontend
yarn test
```

#### Integration Testing
```bash
python backend_test.py
```

### Code Quality

#### Backend
```bash
cd backend
black server.py           # Code formatting
isort server.py          # Import sorting
flake8 server.py         # Linting
mypy server.py           # Type checking
```

#### Frontend
```bash
cd frontend
yarn lint                # ESLint
yarn format              # Prettier
```

## 🔍 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Install dependencies
pip install -r requirements.txt

# Check MongoDB connection
mongosh mongodb://localhost:27017
```

#### Frontend build fails
```bash
# Clear cache
yarn cache clean

# Reinstall dependencies
rm -rf node_modules yarn.lock
yarn install

# Check Node version
node --version  # Should be 18+
```

#### Database connection issues
```bash
# Check MongoDB status
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod

# Check connection string in .env
cat backend/.env
```

#### Permission errors
```bash
# Check file permissions
chmod +x scripts/*

# Check directory ownership
sudo chown -R $USER:$USER /app
```

### Performance Optimization

#### Backend
- Use connection pooling for MongoDB
- Implement Redis caching for frequent queries
- Add database indexing for search fields
- Use async/await for all I/O operations

#### Frontend
- Implement React.memo for expensive components
- Use lazy loading for routes
- Optimize bundle size with code splitting
- Add service worker for caching

## 📞 Support

### Documentation
- API Documentation: `/docs` endpoint when running
- User Guide: See `/docs/user-guide.md`
- Developer Guide: See `/docs/developer-guide.md`

### Logging
- Backend logs: `/var/log/supervisor/backend.*.log`
- Frontend logs: Browser developer console
- System logs: `/var/log/supervisor/`

### Monitoring
- Health check: `GET /api/health`
- System status: Admin dashboard
- Performance metrics: Leaderboard analytics

## 🔄 Updates & Maintenance

### Regular Maintenance
1. **Database Backup**: Weekly automated backups
2. **Log Rotation**: Configure logrotate for system logs
3. **Security Updates**: Monthly dependency updates
4. **Performance Monitoring**: Monitor API response times

### Version Updates
```bash
# Backend updates
pip install --upgrade -r requirements.txt

# Frontend updates  
yarn upgrade

# Database migrations (if needed)
python scripts/migrate.py
```

## 📄 License

This project is proprietary software. All rights reserved.

---

For technical support or questions, please contact the development team.