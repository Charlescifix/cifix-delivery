#!/usr/bin/env python3
"""
Database reset utility for Cifix Hub
This script will drop all data and recreate tables
"""
import asyncio
from app.models import engine, Base
from app.config import settings

async def reset_database():
    print(f"Resetting database: {settings.DATABASE_URL}")
    print("⚠️  This will DELETE ALL DATA in the database!")
    
    confirm = input("Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("Operation cancelled")
        return
    
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        
        print("Creating fresh tables...")
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ Database reset complete! All tables are now empty.")

if __name__ == "__main__":
    asyncio.run(reset_database())