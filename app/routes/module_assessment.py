from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import json
import time
from datetime import datetime

from ..models import (
    Student, Module, ModuleAssessment, ModuleAssessmentAttempt, 
    EnrollmentProgress, ProgressStatus
)
from ..deps import require_student, get_db
from ..templates_config import templates

router = APIRouter()

@router.get("/modules/{module_id}/assessment", response_class=HTMLResponse)
async def show_module_assessment(
    request: Request,
    module_id: int,
    student: Student = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    # Get module and assessment
    module_stmt = select(Module).options(
        selectinload(Module.module_assessment)
    ).where(Module.id == module_id)
    module_result = await db.execute(module_stmt)
    module = module_result.scalar_one_or_none()
    
    if not module or not module.is_published:
        raise HTTPException(status_code=404, detail="Module not found")
    
    if not module.module_assessment or not module.module_assessment.is_active:
        raise HTTPException(status_code=404, detail="Assessment not available")
    
    # Check if student has already completed this assessment
    attempt_stmt = select(ModuleAssessmentAttempt).where(
        ModuleAssessmentAttempt.assessment_id == module.module_assessment.id,
        ModuleAssessmentAttempt.student_id == student.id
    ).order_by(ModuleAssessmentAttempt.completed_at.desc())
    attempt_result = await db.execute(attempt_stmt)
    latest_attempt = attempt_result.scalar_one_or_none()
    
    # Parse assessment questions
    assessment_data = json.loads(module.module_assessment.questions)
    
    return templates.TemplateResponse("module_assessment.html", {
        "request": request,
        "student": student,
        "module": module,
        "assessment": module.module_assessment,
        "assessment_data": assessment_data,
        "latest_attempt": latest_attempt,
        "can_retake": True  # Allow retakes for learning
    })

@router.post("/modules/{module_id}/assessment")
async def submit_module_assessment(
    request: Request,
    module_id: int,
    student: Student = Depends(require_student),
    db: AsyncSession = Depends(get_db),
    start_time: int = Form(...),
    **form_data
):
    # Get assessment
    assessment_stmt = select(ModuleAssessment).where(
        ModuleAssessment.module_id == module_id,
        ModuleAssessment.is_active == True
    )
    assessment_result = await db.execute(assessment_stmt)
    assessment = assessment_result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Parse questions and calculate score
    assessment_data = json.loads(assessment.questions)
    questions = assessment_data['questions']
    
    # Extract answers from form data
    answers = {}
    for i in range(1, len(questions) + 1):
        answer_key = f"question_{i}"
        if answer_key in form_data:
            answers[str(i)] = int(form_data[answer_key])
    
    # Calculate score
    correct_count = 0
    for question in questions:
        q_id = str(question['id'])
        if q_id in answers and answers[q_id] == question['correct_answer']:
            correct_count += 1
    
    score = correct_count
    percentage = int((correct_count / len(questions)) * 100)
    
    # Calculate stars based on scoring rules
    scoring = assessment_data['scoring']
    stars_earned = 1  # Minimum 1 star for attempting
    
    for score_range, stars in scoring['star_rewards'].items():
        if '-' in score_range:
            min_score, max_score = map(int, score_range.split('-'))
            if min_score <= score <= max_score:
                stars_earned = stars
                break
        else:
            if score >= int(score_range):
                stars_earned = stars
                break
    
    # Calculate time taken
    end_time = int(time.time())
    time_taken = max(0, end_time - start_time)  # Prevent negative time
    
    # Save attempt
    attempt = ModuleAssessmentAttempt(
        assessment_id=assessment.id,
        student_id=student.id,
        answers=json.dumps(answers),
        score=score,
        percentage=percentage,
        stars_earned=stars_earned,
        time_taken=time_taken
    )
    db.add(attempt)
    
    # Update module progress if this is first completion or better score
    progress_stmt = select(EnrollmentProgress).where(
        EnrollmentProgress.student_id == student.id,
        EnrollmentProgress.module_id == module_id
    )
    progress_result = await db.execute(progress_stmt)
    progress = progress_result.scalar_one_or_none()
    
    if not progress:
        # Create progress entry
        progress = EnrollmentProgress(
            student_id=student.id,
            module_id=module_id,
            status=ProgressStatus.DONE,
            stars=stars_earned
        )
        db.add(progress)
    else:
        # Update if better performance or first completion
        if progress.status != ProgressStatus.DONE or stars_earned > progress.stars:
            progress.status = ProgressStatus.DONE
            progress.stars = max(progress.stars, stars_earned)
    
    await db.commit()
    
    return RedirectResponse(
        f"/modules/{module_id}/assessment/results/{attempt.id}", 
        status_code=302
    )

@router.get("/modules/{module_id}/assessment/results/{attempt_id}", response_class=HTMLResponse)
async def show_assessment_results(
    request: Request,
    module_id: int,
    attempt_id: int,
    student: Student = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    # Get attempt with related data
    attempt_stmt = select(ModuleAssessmentAttempt).options(
        selectinload(ModuleAssessmentAttempt.assessment),
        selectinload(ModuleAssessmentAttempt.student)
    ).where(
        ModuleAssessmentAttempt.id == attempt_id,
        ModuleAssessmentAttempt.student_id == student.id
    )
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Assessment results not found")
    
    # Get module
    module_stmt = select(Module).where(Module.id == module_id)
    module_result = await db.execute(module_stmt)
    module = module_result.scalar_one_or_none()
    
    # Parse assessment data and student answers
    assessment_data = json.loads(attempt.assessment.questions)
    student_answers = json.loads(attempt.answers)
    
    # Add result info to questions
    questions_with_results = []
    for question in assessment_data['questions']:
        q_id = str(question['id'])
        student_answer = student_answers.get(q_id)
        is_correct = student_answer == question['correct_answer'] if student_answer is not None else False
        
        questions_with_results.append({
            **question,
            'student_answer': student_answer,
            'is_correct': is_correct
        })
    
    return templates.TemplateResponse("assessment_results.html", {
        "request": request,
        "student": student,
        "module": module,
        "attempt": attempt,
        "questions": questions_with_results,
        "total_questions": len(assessment_data['questions']),
        "passing_score": assessment_data['scoring']['passing_score']
    })