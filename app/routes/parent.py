from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Student
from ..deps import get_db, get_serializer, require_parent, get_parent_session
from ..services.report_service import ReportService
from ..config import settings
from fastapi.responses import Response as FastAPIResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/parent", response_class=HTMLResponse)
async def parent_login_page(request: Request):
    session = get_parent_session(request)
    if session:
        return RedirectResponse("/parent/report", status_code=302)
    
    return templates.TemplateResponse("parent_login.html", {"request": request})

@router.post("/parent/login")
async def parent_login(
    request: Request,
    response: Response,
    parent_email: str = Form(...),
    access_code: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Find student with matching access code and parent email
    stmt = select(Student).where(
        Student.access_code == access_code,
        Student.parent_email == parent_email
    )
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    
    if not student:
        return templates.TemplateResponse("parent_login.html", {
            "request": request, 
            "error": "Invalid credentials"
        })
    
    # Create parent session
    serializer = get_serializer()
    session_data = {
        "type": "parent", 
        "student_id": student.id,
        "parent_email": parent_email
    }
    cookie_value = serializer.dumps(session_data)
    
    response = RedirectResponse("/parent/report", status_code=302)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=cookie_value,
        max_age=settings.SESSION_MAX_AGE,
        httponly=True,
        secure=False  # Set to True in production
    )
    
    return response

@router.get("/parent/report", response_class=HTMLResponse)
async def parent_report(
    request: Request,
    session: dict = Depends(require_parent),
    db: AsyncSession = Depends(get_db)
):
    student_id = session["student_id"]
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    
    if not student:
        return RedirectResponse("/parent", status_code=302)
    
    report_data = await ReportService.get_student_report_data(student, db)
    
    return templates.TemplateResponse("parent_report.html", {
        "request": request,
        **report_data
    })

@router.get("/parent/report.pdf")
async def parent_report_pdf(
    session: dict = Depends(require_parent),
    db: AsyncSession = Depends(get_db)
):
    student_id = session["student_id"]
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    
    if not student:
        return RedirectResponse("/parent", status_code=302)
    
    report_data = await ReportService.get_student_report_data(student, db)
    pdf_content = ReportService.generate_pdf_report(report_data)
    
    filename = f"{student.first_name}_progress_report.pdf"
    
    return FastAPIResponse(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )