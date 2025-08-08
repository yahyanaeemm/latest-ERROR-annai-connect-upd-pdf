#!/usr/bin/env python3
"""
Automated Backup System for Admission Management System
Handles MongoDB backup, file backup, and restore operations
"""
import os
import sys
import asyncio
import shutil
import zipfile
import subprocess
from datetime import datetime
from pathlib import Path
import json

# Add backend path for imports
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

class BackupManager:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.backup_dir = Path('/app/backups')
        self.uploads_dir = Path('/app/backend/uploads')
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
    async def create_full_backup(self):
        """Create complete system backup including database and files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"admission_system_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        print(f"🔄 Starting full backup: {backup_name}")
        
        # 1. Backup MongoDB
        await self.backup_mongodb(backup_path)
        
        # 2. Backup uploaded files
        await self.backup_files(backup_path)
        
        # 3. Backup system configuration
        await self.backup_config(backup_path)
        
        # 4. Create backup manifest
        await self.create_manifest(backup_path)
        
        # 5. Compress backup
        zip_path = await self.compress_backup(backup_path)
        
        print(f"✅ Backup completed: {zip_path}")
        return zip_path
    
    async def backup_mongodb(self, backup_path):
        """Backup MongoDB collections"""
        print("📀 Backing up MongoDB...")
        
        client = AsyncIOMotorClient(self.mongo_url)
        db = client[self.db_name]
        
        # Collections to backup
        collections = ['users', 'pending_users', 'students', 'incentive_rules', 'incentives']
        
        mongo_backup_dir = backup_path / 'mongodb'
        mongo_backup_dir.mkdir(exist_ok=True)
        
        for collection_name in collections:
            try:
                collection = db[collection_name]
                documents = await collection.find({}).to_list(length=None)
                
                # Convert datetime objects to ISO strings for JSON serialization
                for doc in documents:
                    for key, value in doc.items():
                        if isinstance(value, datetime):
                            doc[key] = value.isoformat()
                
                backup_file = mongo_backup_dir / f"{collection_name}.json"
                with open(backup_file, 'w') as f:
                    json.dump(documents, f, indent=2, default=str)
                
                print(f"   ✓ Backed up {len(documents)} documents from {collection_name}")
            
            except Exception as e:
                print(f"   ⚠️ Error backing up {collection_name}: {e}")
        
        client.close()
        
    async def backup_files(self, backup_path):
        """Backup uploaded files"""
        print("📁 Backing up uploaded files...")
        
        if self.uploads_dir.exists():
            files_backup_dir = backup_path / 'uploads'
            shutil.copytree(self.uploads_dir, files_backup_dir)
            
            # Count files
            file_count = sum(1 for _ in files_backup_dir.rglob('*') if _.is_file())
            print(f"   ✓ Backed up {file_count} files")
        else:
            print("   ℹ️ No uploads directory found")
    
    async def backup_config(self, backup_path):
        """Backup system configuration files"""
        print("⚙️ Backing up configuration...")
        
        config_backup_dir = backup_path / 'config'
        config_backup_dir.mkdir(exist_ok=True)
        
        # Backup important config files (without sensitive data)
        config_files = [
            ('/app/backend/requirements.txt', 'requirements.txt'),
            ('/app/frontend/package.json', 'package.json'),
            ('/app/init_data.py', 'init_data.py')
        ]
        
        for source_path, filename in config_files:
            if Path(source_path).exists():
                shutil.copy2(source_path, config_backup_dir / filename)
        
        print("   ✓ Configuration files backed up")
    
    async def create_manifest(self, backup_path):
        """Create backup manifest with metadata"""
        manifest = {
            'backup_created': datetime.now().isoformat(),
            'system_version': '1.0',
            'mongo_url': self.mongo_url.replace(self.mongo_url.split('@')[0].split('//')[1], '***') if '@' in self.mongo_url else self.mongo_url,
            'db_name': self.db_name,
            'backup_type': 'full_system',
            'files_included': True,
            'database_included': True,
            'config_included': True
        }
        
        with open(backup_path / 'backup_manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
    
    async def compress_backup(self, backup_path):
        """Compress backup directory"""
        zip_path = f"{backup_path}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_path)
                    zipf.write(file_path, arcname)
        
        # Remove uncompressed directory
        shutil.rmtree(backup_path)
        
        return zip_path
    
    async def restore_from_backup(self, backup_zip_path):
        """Restore system from backup"""
        backup_zip_path = Path(backup_zip_path)
        
        if not backup_zip_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_zip_path}")
        
        print(f"🔄 Starting restore from: {backup_zip_path.name}")
        
        # Extract backup
        extract_dir = self.backup_dir / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with zipfile.ZipFile(backup_zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        # Restore MongoDB
        await self.restore_mongodb(extract_dir)
        
        # Restore files
        await self.restore_files(extract_dir)
        
        print("✅ Restore completed successfully")
    
    async def restore_mongodb(self, extract_dir):
        """Restore MongoDB from backup"""
        print("📀 Restoring MongoDB...")
        
        mongo_backup_dir = extract_dir / 'mongodb'
        if not mongo_backup_dir.exists():
            print("   ⚠️ No MongoDB backup found")
            return
        
        client = AsyncIOMotorClient(self.mongo_url)
        db = client[self.db_name]
        
        for json_file in mongo_backup_dir.glob('*.json'):
            collection_name = json_file.stem
            
            with open(json_file, 'r') as f:
                documents = json.load(f)
            
            if documents:
                # Convert ISO strings back to datetime objects
                for doc in documents:
                    for key, value in doc.items():
                        if isinstance(value, str) and key.endswith(('_at', 'created_at', 'updated_at')):
                            try:
                                doc[key] = datetime.fromisoformat(value)
                            except:
                                pass
                
                # Clear existing collection and insert backup data
                await db[collection_name].delete_many({})
                await db[collection_name].insert_many(documents)
                
                print(f"   ✓ Restored {len(documents)} documents to {collection_name}")
        
        client.close()
    
    async def restore_files(self, extract_dir):
        """Restore uploaded files from backup"""
        print("📁 Restoring uploaded files...")
        
        backup_uploads_dir = extract_dir / 'uploads'
        if backup_uploads_dir.exists():
            # Remove current uploads
            if self.uploads_dir.exists():
                shutil.rmtree(self.uploads_dir)
            
            # Restore from backup
            shutil.copytree(backup_uploads_dir, self.uploads_dir)
            
            file_count = sum(1 for _ in self.uploads_dir.rglob('*') if _.is_file())
            print(f"   ✓ Restored {file_count} files")
    
    async def list_backups(self):
        """List available backups"""
        backups = []
        for backup_file in self.backup_dir.glob('admission_system_backup_*.zip'):
            stat = backup_file.stat()
            backups.append({
                'filename': backup_file.name,
                'path': str(backup_file),
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    async def cleanup_old_backups(self, keep_count=10):
        """Keep only the most recent backups"""
        backups = await self.list_backups()
        
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                Path(backup['path']).unlink()
                print(f"   🗑️ Deleted old backup: {backup['filename']}")

async def main():
    """CLI interface for backup operations"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_system.py create")
        print("  python backup_system.py list")
        print("  python backup_system.py restore <backup_file>")
        print("  python backup_system.py cleanup")
        return
    
    backup_manager = BackupManager()
    command = sys.argv[1]
    
    if command == 'create':
        backup_path = await backup_manager.create_full_backup()
        print(f"\n📦 Backup created at: {backup_path}")
        
    elif command == 'list':
        backups = await backup_manager.list_backups()
        print("\n📋 Available backups:")
        for backup in backups:
            print(f"  {backup['filename']} ({backup['size_mb']} MB) - {backup['created']}")
        
    elif command == 'restore' and len(sys.argv) > 2:
        backup_file = sys.argv[2]
        await backup_manager.restore_from_backup(backup_file)
        
    elif command == 'cleanup':
        await backup_manager.cleanup_old_backups()
        print("✅ Cleanup completed")
        
    else:
        print("❌ Invalid command")

if __name__ == "__main__":
    asyncio.run(main())