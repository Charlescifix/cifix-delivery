from fastapi import APIRouter, Request, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Student, AssessmentResult
from ..schemas.assessment import AssessmentWebhookPayload
from ..deps import get_db
from ..config import settings
import json
import hmac
import hashlib

router = APIRouter()

def generate_recommendation(raw_score: float, level: str, domains: dict) -> str:
    """Generate personalized learning recommendations based on assessment results"""
    
    # Base recommendations based on overall performance
    if raw_score >= 80:
        base_rec = "Excellent work! You're showing strong skills across multiple areas. "
        next_steps = "Continue challenging yourself with advanced topics and consider helping classmates who might need support."
    elif raw_score >= 65:
        base_rec = "Good job! You're making solid progress in your learning journey. "
        next_steps = "Focus on strengthening areas where you scored lower to build a well-rounded foundation."
    elif raw_score >= 50:
        base_rec = "You're on the right track! There are areas where you can improve. "
        next_steps = "Spend extra time practicing the concepts that were challenging in this assessment."
    else:
        base_rec = "Keep working hard! Learning takes time and practice. "
        next_steps = "Consider reviewing the basics and don't hesitate to ask for help when needed."
    
    # Find the strongest and weakest domains
    if domains:
        sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
        strongest = sorted_domains[0] if sorted_domains else None
        weakest = sorted_domains[-1] if len(sorted_domains) > 1 else None
        
        strength_note = ""
        if strongest and strongest[1] > 70:
            domain_name = strongest[0].replace('_', ' ').title()
            strength_note = f" Your strongest area is {domain_name} - great work there!"
        
        improvement_note = ""
        if weakest and weakest[1] < 60:
            domain_name = weakest[0].replace('_', ' ').title()
            improvement_note = f" Focus on improving your {domain_name} skills through extra practice."
        
        return base_rec + strength_note + improvement_note + " " + next_steps
    
    return base_rec + next_steps

@router.post("/assessment/webhook")
async def assessment_webhook(
    payload: AssessmentWebhookPayload,
    request: Request,
    x_hub_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # Verify webhook signature (optional but recommended)
    if x_hub_signature:
        request_body = await request.body()
        expected_signature = hmac.new(
            settings.WEBHOOK_SECRET.encode('utf-8'),
            request_body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(f"sha256={expected_signature}", x_hub_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Verify student exists
    student_stmt = select(Student).where(Student.id == payload.student_id)
    student_result = await db.execute(student_stmt)
    student = student_result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Generate personalized recommendation based on assessment results
    recommendation = generate_recommendation(payload.raw_score, payload.level, payload.domains)
    
    # Create assessment result
    assessment = AssessmentResult(
        student_id=payload.student_id,
        raw_score=payload.raw_score,
        level=payload.level,
        domain_breakdown=json.dumps(payload.domains),
        stars_earned=3,  # Award 3 stars for completing assessment
        recommendation=recommendation
    )
    
    db.add(assessment)
    await db.commit()
    
    return {"status": "success", "message": "Assessment result saved"}

@router.post("/assessment/import-csv")
async def import_assessments_csv(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # This endpoint would handle CSV import if needed
    # Implementation would depend on how you want to structure the CSV
    pass