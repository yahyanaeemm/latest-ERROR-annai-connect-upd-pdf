#!/usr/bin/env python3
"""
Quick validation test for 3-tier approval workflow
"""
import asyncio
import aiohttp
import json

BASE_URL = "https://pdf-receipt-hub.preview.emergentagent.com"

async def test_complete_workflow():
    async with aiohttp.ClientSession() as session:
        # 1. Login as agent
        print("1. Logging in as agent...")
        async with session.post(f"{BASE_URL}/api/login", 
                              json={"username": "agent1", "password": "agent123"}) as resp:
            agent_token = (await resp.json())["access_token"]
        
        # 2. Submit student
        print("2. Submitting student...")
        student_data = {
            "first_name": "Complete",
            "last_name": "WorkflowTest", 
            "email": "workflow.test@example.com",
            "phone": "1234567890",
            "course": "BSc"
        }
        async with session.post(f"{BASE_URL}/api/students", 
                              json=student_data,
                              headers={"Authorization": f"Bearer {agent_token}"}) as resp:
            student = await resp.json()
            student_id = student["id"]
            print(f"   Student created: {student_id}")
        
        # 3. Login as coordinator  
        print("3. Logging in as coordinator...")
        async with session.post(f"{BASE_URL}/api/login",
                              json={"username": "coordinator", "password": "coord123"}) as resp:
            coord_token = (await resp.json())["access_token"]
        
        # 4. Coordinator approval
        print("4. Coordinator approval...")
        update_data = aiohttp.FormData()
        update_data.add_field('status', 'approved')
        update_data.add_field('notes', 'Coordinator approval for complete workflow test')
        update_data.add_field('signature_data', 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
        
        async with session.put(f"{BASE_URL}/api/students/{student_id}/status",
                             data=update_data,
                             headers={"Authorization": f"Bearer {coord_token}"}) as resp:
            result = await resp.json()
            print(f"   Coordinator result: {result}")
        
        # 5. Login as admin
        print("5. Logging in as admin...")
        async with session.post(f"{BASE_URL}/api/login",
                              json={"username": "admin", "password": "admin123"}) as resp:
            admin_token = (await resp.json())["access_token"]
        
        # 6. Check pending approvals
        print("6. Checking pending admin approvals...")
        async with session.get(f"{BASE_URL}/api/admin/pending-approvals",
                             headers={"Authorization": f"Bearer {admin_token}"}) as resp:
            pending = await resp.json()
            print(f"   Found {len(pending)} pending approvals")
            
            # Find our student
            our_student = None
            for student in pending:
                if student["id"] == student_id:
                    our_student = student
                    break
            
            if our_student:
                print(f"   Our student status: {our_student['status']}")
            else:
                print("   Our student not found in pending - checking status...")
                async with session.get(f"{BASE_URL}/api/students",
                                     headers={"Authorization": f"Bearer {admin_token}"}) as resp:
                    all_students = await resp.json()
                    for s in all_students:
                        if s["id"] == student_id:
                            print(f"   Student status: {s['status']}")
                            break
        
        # 7. Admin final approval
        print("7. Admin final approval...")
        approve_data = aiohttp.FormData()
        approve_data.add_field('notes', 'Admin final approval - complete workflow test')
        
        async with session.put(f"{BASE_URL}/api/admin/approve-student/{student_id}",
                             data=approve_data,
                             headers={"Authorization": f"Bearer {admin_token}"}) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"   Admin approval result: {result}")
            else:
                error = await resp.text()
                print(f"   Admin approval error ({resp.status}): {error}")
        
        # 8. Test receipt generation
        print("8. Testing receipt generation...")
        async with session.get(f"{BASE_URL}/api/students/{student_id}/receipt",
                             headers={"Authorization": f"Bearer {admin_token}"}) as resp:
            if resp.status == 200:
                print("   ✅ Receipt generated successfully!")
            else:
                error = await resp.text()
                print(f"   Receipt error ({resp.status}): {error}")
        
        # 9. Test backup creation
        print("9. Testing backup creation...")
        async with session.post(f"{BASE_URL}/api/admin/backup",
                              headers={"Authorization": f"Bearer {admin_token}"}) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"   ✅ Backup test: {result}")
            else:
                error = await resp.text()
                print(f"   Backup error ({resp.status}): {error}")
        
        print("Complete workflow test finished!")

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())