from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import shutil
from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: str  # "agent", "coordinator", "admin"
    agent_id: Optional[str] = None  # For agents only
    created_at: datetime = Field(default_factory=datetime.utcnow)
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str
    agent_id: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: str

class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_number: str
    agent_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    course: str
    documents: Dict[str, str] = {}  # document_type: file_path
    status: str = "pending"  # pending, verified, approved, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    coordinator_notes: Optional[str] = None
    signature_data: Optional[str] = None  # base64 encoded signature
    signature_type: Optional[str] = None  # "draw" or "upload"
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    course: str

class IncentiveRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course: str
    amount: float
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Incentive(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    student_id: str
    course: str
    amount: float
    status: str = "unpaid"  # paid, unpaid
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user_doc = await db.users.find_one({"id": user_id})
    if user_doc is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user_doc)

def generate_token_number():
    """Generate unique token number for student"""
    return f"TOK{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

# Authentication routes
@api_router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
        agent_id=user_data.agent_id,
        hashed_password=hashed_password
    )
    
    await db.users.insert_one(user.dict())
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token, token_type="bearer", role=user.role, user_id=user.id)

@api_router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    user_doc = await db.users.find_one({"username": user_data.username})
    if not user_doc or not verify_password(user_data.password, user_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user_doc["id"]})
    return Token(
        access_token=access_token, 
        token_type="bearer", 
        role=user_doc["role"],
        user_id=user_doc["id"]
    )

@api_router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Student routes
@api_router.post("/students", response_model=Student)
async def create_student(
    student_data: StudentCreate, 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "agent":
        raise HTTPException(status_code=403, detail="Only agents can create student records")
    
    token_number = generate_token_number()
    student = Student(
        token_number=token_number,
        agent_id=current_user.agent_id or current_user.id,
        **student_data.dict()
    )
    
    await db.students.insert_one(student.dict())
    return student

@api_router.post("/students/{student_id}/upload")
async def upload_document(
    student_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["agent", "coordinator", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Validate file type
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.pdf', '.png')):
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and PDF files are allowed")
    
    # Create student directory
    student_dir = UPLOAD_DIR / student_id
    student_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = student_dir / f"{document_type}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update student record
    await db.students.update_one(
        {"id": student_id},
        {"$set": {f"documents.{document_type}": str(file_path)}}
    )
    
    return {"message": "Document uploaded successfully", "file_path": str(file_path)}

@api_router.get("/students", response_model=List[Student])
async def get_students(current_user: User = Depends(get_current_user)):
    query = {}
    if current_user.role == "agent":
        query["agent_id"] = current_user.agent_id or current_user.id
    
    students = await db.students.find(query).to_list(1000)
    return [Student(**student) for student in students]

@api_router.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str, current_user: User = Depends(get_current_user)):
    student_doc = await db.students.find_one({"id": student_id})
    if not student_doc:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = Student(**student_doc)
    
    # Check permissions
    if current_user.role == "agent" and student.agent_id != (current_user.agent_id or current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return student

@api_router.put("/students/{student_id}/status")
async def update_student_status(
    student_id: str,
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    signature_data: Optional[str] = Form(None),
    signature_type: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["coordinator", "admin"]:
        raise HTTPException(status_code=403, detail="Only coordinators and admins can update status")
    
    update_data = {"status": status, "updated_at": datetime.utcnow()}
    if notes:
        update_data["coordinator_notes"] = notes
    if signature_data:
        update_data["signature_data"] = signature_data
        update_data["signature_type"] = signature_type or "draw"
    
    result = await db.students.update_one(
        {"id": student_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Create incentive if approved
    if status == "approved":
        student_doc = await db.students.find_one({"id": student_id})
        if student_doc:
            # Get incentive rule for course
            incentive_rule = await db.incentive_rules.find_one({"course": student_doc["course"], "active": True})
            if incentive_rule:
                incentive = Incentive(
                    agent_id=student_doc["agent_id"],
                    student_id=student_id,
                    course=student_doc["course"],
                    amount=incentive_rule["amount"]
                )
                await db.incentives.insert_one(incentive.dict())
    
    return {"message": "Status updated successfully"}

# Incentive routes
@api_router.get("/incentives")
async def get_incentives(current_user: User = Depends(get_current_user)):
    query = {}
    if current_user.role == "agent":
        query["agent_id"] = current_user.agent_id or current_user.id
    
    incentives = await db.incentives.find(query).to_list(1000)
    total_earned = sum(i["amount"] for i in incentives if i["status"] == "paid")
    total_pending = sum(i["amount"] for i in incentives if i["status"] == "unpaid")
    
    return {
        "incentives": [Incentive(**incentive) for incentive in incentives],
        "total_earned": total_earned,
        "total_pending": total_pending
    }

# Admin routes
@api_router.get("/admin/dashboard")
async def get_admin_dashboard(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_admissions = await db.students.count_documents({})
    active_agents = await db.users.count_documents({"role": "agent"})
    
    # Status breakdown
    pending = await db.students.count_documents({"status": "pending"})
    approved = await db.students.count_documents({"status": "approved"})
    rejected = await db.students.count_documents({"status": "rejected"})
    
    # Incentive stats
    total_incentives_paid = await db.incentives.aggregate([
        {"$match": {"status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    total_incentives_unpaid = await db.incentives.aggregate([
        {"$match": {"status": "unpaid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    return {
        "total_admissions": total_admissions,
        "active_agents": active_agents,
        "status_breakdown": {
            "pending": pending,
            "approved": approved,
            "rejected": rejected
        },
        "incentives_paid": total_incentives_paid[0]["total"] if total_incentives_paid else 0,
        "incentives_unpaid": total_incentives_unpaid[0]["total"] if total_incentives_unpaid else 0
    }

# Initialize incentive rules
@api_router.post("/admin/incentive-rules")
async def create_incentive_rule(
    course: str = Form(...),
    amount: float = Form(...),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    rule = IncentiveRule(course=course, amount=amount)
    await db.incentive_rules.insert_one(rule.dict())
    return rule

@api_router.get("/incentive-rules")
async def get_incentive_rules():
    rules = await db.incentive_rules.find().to_list(1000)
    return [IncentiveRule(**rule) for rule in rules]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()