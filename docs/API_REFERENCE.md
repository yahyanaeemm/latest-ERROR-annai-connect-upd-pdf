# AnnaiCONNECT API Reference

## Base URL
```
Production: https://your-domain.com/api
Development: http://localhost:8001/api
```

## Authentication
All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Response Format
All API responses follow this structure:
```json
{
  "data": {},           // Response data
  "message": "string",  // Success/error message
  "status": "success|error"
}
```

## Error Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

---

## Authentication Endpoints

### Register User
**POST** `/register`

Creates a new user registration (requires admin approval).

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "agent|coordinator|admin",
  "first_name": "string",
  "last_name": "string",
  "agent_id": "string (required for agents)"
}
```

**Response:**
```json
{
  "message": "Registration submitted successfully. Your account is pending admin approval.",
  "status": "pending",
  "username": "string"
}
```

### Login
**POST** `/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_string",
  "token_type": "bearer",
  "role": "agent|coordinator|admin",
  "user_id": "string"
}
```

### Get Current User
**GET** `/me`

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "role": "string",
  "first_name": "string",
  "last_name": "string",
  "created_at": "datetime"
}
```

---

## Student Management

### Create Student
**POST** `/students`

Create new student application (agents only).

**Headers:**
```
Authorization: Bearer <agent_token>
```

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "course": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "token_number": "AGI2508001",
  "agent_id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "course": "string",
  "status": "pending",
  "created_at": "datetime"
}
```

### Get Students
**GET** `/students`

Get list of students (role-based filtering applied).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `status`: Filter by status (optional)
- `course`: Filter by course (optional)
- `agent_id`: Filter by agent (optional)

**Response:**
```json
[
  {
    "id": "string",
    "token_number": "string",
    "first_name": "string",
    "last_name": "string",
    "course": "string",
    "status": "string",
    "created_at": "datetime"
  }
]
```

### Get Students Paginated
**GET** `/students/paginated`

Get paginated students with advanced filtering (coordinators/admins only).

**Headers:**
```
Authorization: Bearer <coordinator_or_admin_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)
- `status`: Filter by status
- `course`: Filter by course
- `agent_id`: Filter by agent
- `search`: Search term
- `date_from`: Start date filter
- `date_to`: End date filter

**Response:**
```json
{
  "students": [
    {
      "id": "string",
      "token_number": "string",
      "name": "string",
      "course": "string",
      "status": "string",
      "agent_name": "string",
      "created_at": "datetime"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 100,
    "has_next": true,
    "has_previous": false
  }
}
```

### Get Student Details
**GET** `/students/{student_id}/detailed`

Get comprehensive student information (coordinators/admins only).

**Headers:**
```
Authorization: Bearer <coordinator_or_admin_token>
```

**Response:**
```json
{
  "id": "string",
  "token_number": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "course": "string",
  "status": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "coordinator_notes": "string",
  "agent_info": {
    "agent_id": "string",
    "username": "string",
    "first_name": "string",
    "last_name": "string"
  },
  "documents": {}
}
```

### Update Student Status
**PUT** `/students/{student_id}/status`

Update student application status (coordinators/admins only).

**Headers:**
```
Authorization: Bearer <coordinator_or_admin_token>
```

**Request Body:**
```json
{
  "status": "approved|rejected|coordinator_approved",
  "notes": "string",
  "signature_data": "base64_string (optional)",
  "signature_type": "draw|upload (optional)"
}
```

**Response:**
```json
{
  "message": "Student status updated successfully",
  "status": "success"
}
```

### Upload Student Document
**POST** `/students/{student_id}/upload`

Upload document for student application.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `document_type`: String (e.g., "id_proof", "certificates")
- `file`: File (PDF, JPG, PNG only)

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "file_path": "string",
  "document_type": "string"
}
```

### Download Student Receipt
**GET** `/students/{student_id}/receipt`

Download PDF receipt for approved student.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
Binary PDF file with headers:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="receipt_{token_number}.pdf"
```

---

## Admin Management

### Get Enhanced Dashboard
**GET** `/admin/dashboard-enhanced`

Get comprehensive admin dashboard statistics.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "admissions": {
    "total": 150,
    "pending": 5,
    "verified": 10,
    "coordinator_approved": 8,
    "approved": 120,
    "rejected": 7
  },
  "agents": {
    "total": 12,
    "active": 10
  },
  "incentives": {
    "total_records": 120,
    "paid_records": 80,
    "unpaid_records": 40,
    "paid_amount": 480000.0,
    "pending_amount": 200000.0,
    "total_amount": 680000.0
  }
}
```

### Get Pending Approvals
**GET** `/admin/pending-approvals`

Get students awaiting admin final approval.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
[
  {
    "id": "string",
    "token_number": "string",
    "first_name": "string",
    "last_name": "string",
    "course": "string",
    "agent_name": "string",
    "coordinator_approved_at": "datetime"
  }
]
```

### Approve Student (Final)
**PUT** `/admin/approve-student/{student_id}`

Give final admin approval to student.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "notes": "string"
}
```

**Response:**
```json
{
  "message": "Student approved and incentive created",
  "student_id": "string",
  "incentive_id": "string"
}
```

### Reject Student
**PUT** `/admin/reject-student/{student_id}`

Reject student application (admin).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "notes": "string"
}
```

**Response:**
```json
{
  "message": "Student application rejected",
  "student_id": "string"
}
```

### Export Excel Report
**GET** `/admin/export/excel`

Export comprehensive Excel report with filters.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `agent_id`: Filter by specific agent
- `course`: Filter by course
- `status`: Filter by status

**Response:**
Binary Excel file with headers:
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="admission_report_{date}.xlsx"
```

### Production Deployment
**POST** `/admin/deploy-production`

Complete production deployment (cleanup + setup).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "message": "Production deployment completed successfully!",
  "cleanup_summary": {
    "deleted_records": {
      "users": 10,
      "students": 50,
      "incentives": 30
    },
    "uploads_cleared": true
  },
  "production_setup": {
    "created_users": [
      "admin: super admin",
      "coordinator: arulanantham",
      "agent: agent1"
    ],
    "created_courses": [
      "B.Ed: ₹6000",
      "MBA: ₹2500",
      "BNYS: ₹20000"
    ]
  },
  "next_steps": [
    "Login with new admin credentials: super admin / Admin@annaiconnect"
  ],
  "status": "success"
}
```

---

## Course Management

### Get Courses
**GET** `/incentive-rules`

Get list of active courses with incentive amounts.

**Response:**
```json
[
  {
    "id": "string",
    "course": "B.Ed",
    "amount": 6000.0,
    "active": true,
    "created_at": "datetime"
  }
]
```

### Create Course
**POST** `/admin/courses`

Create new course with incentive amount (admins only).

**Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `course`: String (course name)
- `amount`: Number (incentive amount)

**Response:**
```json
{
  "message": "Course created successfully",
  "course_id": "string"
}
```

### Update Course
**PUT** `/admin/courses/{course_id}`

Update existing course information.

**Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `course`: String (course name)
- `amount`: Number (incentive amount)

**Response:**
```json
{
  "message": "Course updated successfully",
  "course_id": "string"
}
```

### Delete Course
**DELETE** `/admin/courses/{course_id}`

Soft delete course (sets active=false).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "message": "Course deleted successfully",
  "course_id": "string"
}
```

---

## Leaderboard & Analytics

### Overall Leaderboard
**GET** `/leaderboard/overall`

Get overall agent performance rankings.

**Response:**
```json
[
  {
    "agent_id": "string",
    "username": "string",
    "full_name": "string",
    "total_admissions": 25,
    "total_incentive": 125000.0,
    "rank": 1,
    "is_top_3": true,
    "badge": "gold"
  }
]
```

### Weekly Leaderboard
**GET** `/leaderboard/weekly`

Get current week performance rankings.

**Response:**
```json
{
  "period": {
    "start_date": "2025-08-04",
    "end_date": "2025-08-10",
    "type": "weekly"
  },
  "leaderboard": [
    {
      "agent_id": "string",
      "username": "string",
      "full_name": "string",
      "total_admissions": 8,
      "total_incentive": 48000.0,
      "rank": 1,
      "is_top_3": true,
      "badge": "gold"
    }
  ]
}
```

### Monthly Leaderboard
**GET** `/leaderboard/monthly`

Get current month performance rankings.

**Response:**
```json
{
  "period": {
    "start_date": "2025-08-01",
    "end_date": "2025-08-31",
    "type": "monthly"
  },
  "leaderboard": [
    {
      "agent_id": "string",
      "username": "string",
      "full_name": "string",
      "total_admissions": 20,
      "total_incentive": 120000.0,
      "rank": 1,
      "is_top_3": true,
      "badge": "gold"
    }
  ]
}
```

### Custom Date Range Leaderboard
**GET** `/leaderboard/date-range`

Get performance rankings for custom date range.

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Response:**
```json
{
  "period": {
    "start_date": "2025-07-01",
    "end_date": "2025-07-31",
    "type": "custom"
  },
  "leaderboard": [
    {
      "agent_id": "string",
      "username": "string",
      "full_name": "string",
      "total_admissions": 15,
      "total_incentive": 90000.0,
      "rank": 1,
      "is_top_3": true,
      "badge": "gold"
    }
  ]
}
```

---

## Profile Management

### Get Profile
**GET** `/profile`

Get current user profile information (agents only).

**Headers:**
```
Authorization: Bearer <agent_token>
```

**Response:**
```json
{
  "basic_info": {
    "first_name": "string",
    "last_name": "string",
    "username": "string",
    "email": "string",
    "phone": "string",
    "address": "string",
    "agent_id": "string",
    "joining_date": "datetime"
  },
  "professional_info": {
    "experience_level": "string",
    "specializations": ["string"],
    "monthly_target": 10,
    "quarterly_target": 30,
    "bio": "string"
  },
  "performance_metrics": {
    "total_students": 25,
    "approved_students": 20,
    "pending_students": 3,
    "rejected_students": 2,
    "total_earned": 120000.0,
    "pending_incentives": 18000.0
  },
  "top_courses": [
    {
      "course": "B.Ed",
      "count": 15,
      "percentage": 60.0
    }
  ]
}
```

### Update Profile
**PUT** `/profile`

Update profile information (agents only).

**Headers:**
```
Authorization: Bearer <agent_token>
```

**Request Body:**
```json
{
  "phone": "string",
  "address": "string",
  "experience_level": "beginner|intermediate|expert",
  "specializations": ["string"],
  "monthly_target": 10,
  "quarterly_target": 30,
  "bio": "string"
}
```

**Response:**
```json
{
  "message": "Profile updated successfully",
  "status": "success"
}
```

### Upload Profile Photo
**POST** `/profile/upload-photo`

Upload profile photo (agents only).

**Headers:**
```
Authorization: Bearer <agent_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Image file (JPG, PNG only)

**Response:**
```json
{
  "message": "Profile photo uploaded successfully",
  "photo_url": "string"
}
```

---

## Error Responses

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Authentication Error (401)
```json
{
  "detail": "Invalid authentication credentials"
}
```

### Permission Error (403)
```json
{
  "detail": "Admin access required"
}
```

### Not Found Error (404)
```json
{
  "detail": "Student not found"
}
```

### Internal Server Error (500)
```json
{
  "detail": "Internal server error message"
}
```

---

## Rate Limiting

API endpoints have the following rate limits:
- Authentication endpoints: 5 requests per minute
- Student creation: 10 requests per minute
- File uploads: 5 requests per minute
- General endpoints: 100 requests per minute

## WebSocket Support

Real-time updates are available via WebSocket connection:
```
ws://localhost:8001/ws/{user_id}
```

Events:
- `student_status_updated`
- `new_student_created`
- `incentive_created`
- `leaderboard_updated`

---

For additional support or questions about the API, please refer to the main documentation or contact the development team.