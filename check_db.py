#!/usr/bin/env python3
"""
Database inspection script for Cifix Hub
"""
import asyncio
import asyncpg
from app.config import settings

async def check_database():
    # Extract connection details from DATABASE_URL
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        # Connect to the database
        print(f"Connecting to: {db_url.split('@')[1]}")  # Hide password
        conn = await asyncpg.connect(db_url)
        
        # List all tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Check students table
        if any(t['table_name'] == 'students' for t in tables):
            students = await conn.fetch("SELECT id, first_name, parent_email, access_code FROM students LIMIT 10")
            print(f"\nStudents table ({len(students)} records shown):")
            for student in students:
                print(f"  ID: {student['id']}, Name: {student['first_name']}, Email: {student['parent_email']}, Code: {student['access_code']}")
            
            # Check for duplicates
            duplicates = await conn.fetch("""
                SELECT parent_email, COUNT(*) as count 
                FROM students 
                GROUP BY parent_email 
                HAVING COUNT(*) > 1
            """)
            
            if duplicates:
                print(f"\nWARNING: Found {len(duplicates)} duplicate email addresses:")
                for dup in duplicates:
                    print(f"  - {dup['parent_email']}: {dup['count']} records")
            else:
                print("\nNo duplicate email addresses found")
        
        # Check modules table
        if any(t['table_name'] == 'modules' for t in tables):
            modules = await conn.fetch("SELECT id, title, week_no, is_published FROM modules")
            print(f"\nModules table ({len(modules)} records):")
            for module in modules:
                status = "Published" if module['is_published'] else "Draft"
                print(f"  Week {module['week_no']}: {module['title']} - {status}")
        
        await conn.close()
        print("\nDatabase connection successful")
        
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_database())