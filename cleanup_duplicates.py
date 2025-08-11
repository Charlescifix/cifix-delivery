#!/usr/bin/env python3
"""
Clean up duplicate records in the database
"""
import asyncio
import asyncpg
from app.config import settings

async def cleanup_duplicates():
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        conn = await asyncpg.connect(db_url)
        
        # Find duplicates
        duplicates = await conn.fetch("""
            SELECT parent_email, array_agg(id ORDER BY id) as ids
            FROM students 
            GROUP BY parent_email 
            HAVING COUNT(*) > 1
        """)
        
        for dup in duplicates:
            email = dup['parent_email']
            ids = dup['ids']
            print(f"Email: {email} has {len(ids)} records: {ids}")
            
            # Keep the first record, delete the rest
            keep_id = ids[0]
            delete_ids = ids[1:]
            
            print(f"  Keeping ID {keep_id}, deleting IDs {delete_ids}")
            
            # Delete enrollment progress for duplicate students
            for del_id in delete_ids:
                await conn.execute("DELETE FROM enrollment_progress WHERE student_id = $1", del_id)
                await conn.execute("DELETE FROM assessment_results WHERE student_id = $1", del_id) 
                await conn.execute("DELETE FROM student_badges WHERE student_id = $1", del_id)
            
            # Delete duplicate student records
            await conn.execute("DELETE FROM students WHERE id = ANY($1)", delete_ids)
            
            print(f"  Cleaned up {len(delete_ids)} duplicate records")
        
        # Verify cleanup
        remaining_dups = await conn.fetch("""
            SELECT parent_email, COUNT(*) as count 
            FROM students 
            GROUP BY parent_email 
            HAVING COUNT(*) > 1
        """)
        
        if remaining_dups:
            print(f"Still have {len(remaining_dups)} duplicates remaining")
        else:
            print("All duplicates cleaned up successfully!")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error cleaning up duplicates: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())