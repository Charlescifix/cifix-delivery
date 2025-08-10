from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models import Student, Module, EnrollmentProgress, AssessmentResult, ProgressStatus
from ..deps import require_student, get_db
from ..templates_config import templates

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def student_dashboard(
    request: Request,
    student: Student = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    # Get published modules
    modules_stmt = select(Module).where(Module.is_published == True).order_by(Module.week_no)
    modules_result = await db.execute(modules_stmt)
    modules = modules_result.scalars().all()
    
    # Get student progress
    progress_stmt = select(EnrollmentProgress).where(
        EnrollmentProgress.student_id == student.id
    ).options(selectinload(EnrollmentProgress.module))
    progress_result = await db.execute(progress_stmt)
    progress_data = {p.module_id: p for p in progress_result.scalars().all()}
    
    # Get latest assessment
    assessment_stmt = select(AssessmentResult).where(
        AssessmentResult.student_id == student.id
    ).order_by(AssessmentResult.completed_at.desc()).limit(1)
    assessment_result = await db.execute(assessment_stmt)
    latest_assessment = assessment_result.scalar_one_or_none()
    
    # Get all assessment results for star calculation
    all_assessments_stmt = select(AssessmentResult).where(
        AssessmentResult.student_id == student.id
    )
    all_assessments_result = await db.execute(all_assessments_stmt)
    all_assessments = all_assessments_result.scalars().all()
    
    # Calculate progress stats
    total_modules = len(modules)
    completed_modules = sum(1 for m in modules if progress_data.get(m.id) and progress_data[m.id].status == ProgressStatus.DONE)
    module_stars = sum(p.stars for p in progress_data.values())
    assessment_stars = sum(a.stars_earned for a in all_assessments)
    total_stars = module_stars + assessment_stars
    
    # Find current week module
    current_module = modules[0] if modules else None
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "student": student,
        "modules": modules,
        "progress_data": progress_data,
        "latest_assessment": latest_assessment,
        "all_assessments": all_assessments,
        "current_module": current_module,
        "total_modules": total_modules,
        "completed_modules": completed_modules,
        "total_stars": total_stars,
        "module_stars": module_stars,
        "assessment_stars": assessment_stars,
        "progress_status": ProgressStatus
    })

@router.get("/modules/{module_id}", response_class=HTMLResponse)
async def module_detail(
    request: Request,
    module_id: int,
    student: Student = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    # Get module
    module_stmt = select(Module).where(Module.id == module_id, Module.is_published == True)
    module_result = await db.execute(module_stmt)
    module = module_result.scalar_one_or_none()
    
    if not module:
        return RedirectResponse("/dashboard", status_code=302)
    
    # Get or create progress
    progress_stmt = select(EnrollmentProgress).where(
        EnrollmentProgress.student_id == student.id,
        EnrollmentProgress.module_id == module_id
    )
    progress_result = await db.execute(progress_stmt)
    progress = progress_result.scalar_one_or_none()
    
    if not progress:
        progress = EnrollmentProgress(
            student_id=student.id,
            module_id=module_id,
            status=ProgressStatus.NOT_STARTED
        )
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
    
    # Mark as started if not already done
    if progress.status == ProgressStatus.NOT_STARTED:
        progress.status = ProgressStatus.STARTED
        await db.commit()
    
    return templates.TemplateResponse("module_detail.html", {
        "request": request,
        "student": student,
        "module": module,
        "progress": progress,
        "progress_status": ProgressStatus
    })

@router.post("/modules/{module_id}/complete")
async def complete_module(
    module_id: int,
    student: Student = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    # Get or create progress
    progress_stmt = select(EnrollmentProgress).where(
        EnrollmentProgress.student_id == student.id,
        EnrollmentProgress.module_id == module_id
    )
    progress_result = await db.execute(progress_stmt)
    progress = progress_result.scalar_one_or_none()
    
    if progress and progress.status != ProgressStatus.DONE:
        progress.status = ProgressStatus.DONE
        progress.stars = 3  # Award 3 stars for completion
        await db.commit()
    
    return RedirectResponse(f"/modules/{module_id}", status_code=302)

@router.get("/assessment/start")
async def start_assessment(
    request: Request,
    student: Student = Depends(require_student)
):
    # Create return URL for after assessment completion
    return_url = f"{request.url.scheme}://{request.url.netloc}/assessment/complete"
    
    # Redirect to assessment with return URL and student info
    assessment_url = f"https://kid-assessment.streamlit.app?student_id={student.id}&return_url={return_url}&student_name={student.first_name}"
    return RedirectResponse(assessment_url, status_code=302)

@router.get("/assessment/complete")
async def assessment_complete(
    request: Request,
    student: Student = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    # Get latest assessment result
    assessment_stmt = select(AssessmentResult).where(
        AssessmentResult.student_id == student.id
    ).order_by(AssessmentResult.completed_at.desc()).limit(1)
    assessment_result = await db.execute(assessment_stmt)
    latest_assessment = assessment_result.scalar_one_or_none()
    
    return templates.TemplateResponse("assessment_complete.html", {
        "request": request,
        "student": student,
        "assessment": latest_assessment
    })

@router.get("/assessment/results")
async def assessment_results(
    request: Request,
    student: Student = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    # Get all assessment results for student
    assessments_stmt = select(AssessmentResult).where(
        AssessmentResult.student_id == student.id
    ).order_by(AssessmentResult.completed_at.desc())
    assessments_result = await db.execute(assessments_stmt)
    assessments = assessments_result.scalars().all()
    
    return templates.TemplateResponse("assessment_results.html", {
        "request": request,
        "student": student,
        "assessments": assessments
    })