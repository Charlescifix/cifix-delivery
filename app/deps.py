from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from itsdangerous import URLSafeTimedSerializer
from typing import Optional
from .models import async_session, Student
from .config import settings

async def get_db():
    async with async_session() as session:
        yield session

def get_serializer():
    return URLSafeTimedSerializer(settings.SECRET_KEY)

def get_session_data(request: Request) -> Optional[dict]:
    serializer = get_serializer()
    cookie_value = request.cookies.get(settings.SESSION_COOKIE_NAME)
    
    if not cookie_value:
        return None
    
    try:
        return serializer.loads(cookie_value, max_age=settings.SESSION_MAX_AGE)
    except:
        return None

async def get_current_student(
    request: Request, 
    db: AsyncSession = Depends(get_db)
) -> Optional[Student]:
    session_data = get_session_data(request)
    if not session_data or session_data.get("type") != "student":
        return None
    
    student_id = session_data.get("student_id")
    if not student_id:
        return None
    
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def require_student(
    request: Request, 
    db: AsyncSession = Depends(get_db)
) -> Student:
    student = await get_current_student(request, db)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return student

def get_parent_session(request: Request) -> Optional[dict]:
    session_data = get_session_data(request)
    if not session_data or session_data.get("type") != "parent":
        return None
    return session_data

def require_parent(request: Request) -> dict:
    session_data = get_parent_session(request)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return session_data

def get_admin_session(request: Request) -> Optional[dict]:
    session_data = get_session_data(request)
    if not session_data or session_data.get("type") != "admin":
        return None
    return session_data

def require_admin(request: Request) -> dict:
    session_data = get_admin_session(request)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    return session_data