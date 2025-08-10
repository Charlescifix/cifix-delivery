from fastapi import APIRouter, Request, Form, Response, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from ..models import Student, Module, AssessmentResult, EnrollmentProgress
from ..deps import get_db, get_serializer, require_admin, get_admin_session
from ..config import settings
from fastapi.responses import Response as FastAPIResponse
import csv
import io
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    session = get_admin_session(request)
    if session:
        return RedirectResponse("/admin/dashboard", status_code=302)
    
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page_alt(request: Request):
    return await admin_login_page(request)

@router.post("/admin/login")
async def admin_login(
    request: Request,
    response: Response,
    password: str = Form(...)
):
    if password != settings.ADMIN_PASS:
        return templates.TemplateResponse("admin/login.html", {
            "request": request, 
            "error": "Invalid password"
        })
    
    serializer = get_serializer()
    session_data = {"type": "admin", "logged_in_at": datetime.now().isoformat()}
    cookie_value = serializer.dumps(session_data)
    
    response = RedirectResponse("/admin/dashboard", status_code=302)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=cookie_value,
        max_age=settings.SESSION_MAX_AGE,
        httponly=True,
        secure=False
    )
    
    return response

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    session: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Get basic stats
    students_count = await db.scalar(select(func.count(Student.id)))
    modules_count = await db.scalar(select(func.count(Module.id)))
    assessments_count = await db.scalar(select(func.count(AssessmentResult.id)))
    
    # Get recent students
    recent_students_stmt = select(Student).order_by(Student.created_at.desc()).limit(5)
    recent_students_result = await db.execute(recent_students_stmt)
    recent_students = recent_students_result.scalars().all()
    
    # Get all modules
    modules_stmt = select(Module).order_by(Module.week_no)
    modules_result = await db.execute(modules_stmt)
    modules = modules_result.scalars().all()
    
    return templates.TemplateResponse("admin/index.html", {
        "request": request,
        "students_count": students_count,
        "modules_count": modules_count,
        "assessments_count": assessments_count,
        "recent_students": recent_students,
        "modules": modules
    })

@router.get("/admin/modules", response_class=HTMLResponse)
async def admin_modules(
    request: Request,
    session: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    modules_stmt = select(Module).order_by(Module.week_no)
    modules_result = await db.execute(modules_stmt)
    modules = modules_result.scalars().all()
    
    return templates.TemplateResponse("admin/modules.html", {
        "request": request,
        "modules": modules
    })

@router.post("/admin/modules")
async def create_module(
    title: str = Form(...),
    week_no: int = Form(...),
    video_url: str = Form(""),
    resource_url: str = Form(""),
    meet_url: str = Form(""),
    is_published: bool = Form(False),
    session: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    module = Module(
        title=title,
        week_no=week_no,
        video_url=video_url if video_url else None,
        resource_url=resource_url if resource_url else None,
        meet_url=meet_url if meet_url else None,
        is_published=is_published
    )
    
    db.add(module)
    await db.commit()
    
    return RedirectResponse("/admin/modules", status_code=302)

@router.get("/admin/students", response_class=HTMLResponse)
async def admin_students(
    request: Request,
    session: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    students_stmt = select(Student).order_by(Student.created_at.desc())
    students_result = await db.execute(students_stmt)
    students = students_result.scalars().all()
    
    return templates.TemplateResponse("admin/students.html", {
        "request": request,
        "students": students
    })

@router.post("/admin/students")
async def create_student(
    first_name: str = Form(...),
    age: int = Form(...),
    parent_email: str = Form(...),
    access_code: str = Form(...),
    class_label: str = Form(""),
    session: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Check if access code already exists
    existing_stmt = select(Student).where(Student.access_code == access_code)
    existing_result = await db.execute(existing_stmt)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Access code already exists")
    
    student = Student(
        first_name=first_name,
        age=age,
        parent_email=parent_email,
        access_code=access_code,
        class_label=class_label if class_label else None
    )
    
    db.add(student)
    await db.commit()
    
    return RedirectResponse("/admin/students", status_code=302)

@router.get("/admin/assessments.csv")
async def export_assessments_csv(
    session: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Get all assessments with student info
    assessments_stmt = select(AssessmentResult).options(
        selectinload(AssessmentResult.student)
    ).order_by(AssessmentResult.completed_at.desc())
    assessments_result = await db.execute(assessments_stmt)
    assessments = assessments_result.scalars().all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Student ID", "First Name", "Parent Email", "Access Code",
        "Raw Score", "Level", "Completed At", "Domain Breakdown"
    ])
    
    # Write data
    for assessment in assessments:
        writer.writerow([
            assessment.student_id,
            assessment.student.first_name,
            assessment.student.parent_email,
            assessment.student.access_code,
            assessment.raw_score,
            assessment.level,
            assessment.completed_at.strftime("%Y-%m-%d %H:%M:%S"),
            assessment.domain_breakdown or ""
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return FastAPIResponse(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=assessments_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )