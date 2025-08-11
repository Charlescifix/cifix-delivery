from fastapi import APIRouter, Request, Form, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Student
from ..deps import get_db, get_serializer, get_current_student
from ..config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: AsyncSession = Depends(get_db)):
    current_student = await get_current_student(request, db)
    if current_student:
        return RedirectResponse("/dashboard", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_student(
    request: Request,
    response: Response,
    first_name: str = Form(...),
    access_code: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Student).where(Student.access_code == access_code)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    
    if not student:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid access code"
        })
    
    if student.first_name.lower() != first_name.lower():
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Name doesn't match"
        })
    
    serializer = get_serializer()
    session_data = {"type": "student", "student_id": student.id}
    cookie_value = serializer.dumps(session_data)
    
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=cookie_value,
        max_age=settings.SESSION_MAX_AGE,
        httponly=True,
        secure=False  # Set to True in production with HTTPS
    )
    
    return response

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_student(
    request: Request,
    response: Response,
    first_name: str = Form(...),
    age: int = Form(...),
    parent_email: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    import random
    import string
    import re
    
    # Input validation
    errors = []
    
    # Validate first name
    first_name = first_name.strip()
    if not first_name or len(first_name) < 2:
        errors.append("First name must be at least 2 characters long")
    elif not re.match(r"^[a-zA-Z\s]+$", first_name):
        errors.append("First name can only contain letters and spaces")
    
    # Validate age
    if age < 3 or age > 18:
        errors.append("Age must be between 3 and 18")
    
    # Validate email format
    parent_email = parent_email.strip().lower()
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, parent_email):
        errors.append("Please enter a valid email address")
    
    # Check for duplicate email
    if not errors:
        email_stmt = select(Student).where(Student.parent_email == parent_email)
        email_result = await db.execute(email_stmt)
        existing_emails = email_result.scalars().all()
        if existing_emails:
            errors.append("A student with this parent email is already registered")
    
    # Check for duplicate name + age combination (same child)
    if not errors:
        name_age_stmt = select(Student).where(
            Student.first_name.ilike(first_name),
            Student.age == age
        )
        name_age_result = await db.execute(name_age_stmt)
        existing_students = name_age_result.scalars().all()
        if existing_students:
            errors.append("A student with this name and age is already registered")
    
    # If validation errors, return with errors
    if errors:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": errors,
            "first_name": first_name,
            "age": age,
            "parent_email": parent_email
        })
    
    # Generate unique access code
    while True:
        access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        stmt = select(Student).where(Student.access_code == access_code)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            break
    
    # Create new student
    try:
        student = Student(
            first_name=first_name.title(),  # Proper case
            age=age,
            parent_email=parent_email,
            access_code=access_code
        )
        db.add(student)
        await db.commit()
        await db.refresh(student)
        
        # Show success page with access code
        return templates.TemplateResponse("register_success.html", {
            "request": request,
            "student": student,
            "access_code": access_code
        })
        
    except Exception as e:
        await db.rollback()
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "error": "Registration failed due to database error. Please try again.",
            "first_name": first_name,
            "age": age,
            "parent_email": parent_email
        })