#!/usr/bin/env python3
"""
Initialize demo data for the admission system
"""
import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def init_data():
    print("Initializing demo data...")
    
    # Clear existing data
    await db.users.delete_many({})
    await db.incentive_rules.delete_many({})
    
    # Create demo users
    users = [
        {
            "id": "admin-001",
            "username": "admin",
            "email": "admin@college.edu",
            "role": "admin",
            "agent_id": None,
            "first_name": "Admin",
            "last_name": "User",
            "hashed_password": get_password_hash("admin123"),
        },
        {
            "id": "coord-001", 
            "username": "coordinator",
            "email": "coordinator@college.edu",
            "role": "coordinator",
            "agent_id": None,
            "first_name": "Admission",
            "last_name": "Coordinator",
            "hashed_password": get_password_hash("coord123"),
        },
        {
            "id": "agent-001",
            "username": "agent1",
            "email": "agent1@college.edu", 
            "role": "agent",
            "agent_id": "AGT001",
            "first_name": "Rajesh",
            "last_name": "Kumar",
            "hashed_password": get_password_hash("agent123"),
        },
        {
            "id": "agent-002",
            "username": "agent2",
            "email": "agent2@college.edu",
            "role": "agent", 
            "agent_id": "AGT002",
            "first_name": "Priya",
            "last_name": "Sharma",
            "hashed_password": get_password_hash("agent123"),
        }
    ]
    
    await db.users.insert_many(users)
    print("✓ Created demo users:")
    print("  - admin/admin123 (Admin)")
    print("  - coordinator/coord123 (Coordinator)")
    print("  - agent1/agent123 (Agent)")
    print("  - agent2/agent123 (Agent)")
    
    # Create incentive rules
    incentive_rules = [
        {"id": "rule-001", "course": "BSc", "amount": 3000.0},
        {"id": "rule-002", "course": "BNYS", "amount": 5000.0},
        {"id": "rule-003", "course": "BCA", "amount": 4000.0},
        {"id": "rule-004", "course": "BA", "amount": 2500.0},
        {"id": "rule-005", "course": "BCom", "amount": 3500.0},
    ]
    
    await db.incentive_rules.insert_many(incentive_rules)
    print("✓ Created incentive rules:")
    for rule in incentive_rules:
        print(f"  - {rule['course']}: ₹{rule['amount']}")
    
    print("\nDemo data initialization complete!")
    client.close()

if __name__ == "__main__":
    asyncio.run(init_data())