from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any
from .base import Base

class ModuleAssessment(Base):
    """Built-in 10 MCQ assessments for each module"""
    __tablename__ = "module_assessments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    questions: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string of questions
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    module: Mapped["Module"] = relationship(back_populates="module_assessment")
    attempts: Mapped[list["ModuleAssessmentAttempt"]] = relationship(back_populates="assessment")

class ModuleAssessmentAttempt(Base):
    """Student attempts at module assessments"""
    __tablename__ = "module_assessment_attempts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("module_assessments.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    
    # Results
    answers: Mapped[str] = mapped_column(Text, nullable=False)  # JSON of student answers
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # Score out of 10
    percentage: Mapped[int] = mapped_column(Integer, nullable=False)  # Percentage score
    stars_earned: Mapped[int] = mapped_column(Integer, default=0)  # Stars based on performance
    time_taken: Mapped[int] = mapped_column(Integer, nullable=True)  # Time in seconds
    
    completed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    assessment: Mapped["ModuleAssessment"] = relationship(back_populates="attempts")
    student: Mapped["Student"] = relationship(back_populates="module_attempts")
    module_progress: Mapped["EnrollmentProgress"] = relationship(
        foreign_keys="ModuleAssessmentAttempt.student_id",
        primaryjoin="and_(ModuleAssessmentAttempt.student_id==EnrollmentProgress.student_id, "
                   "ModuleAssessmentAttempt.assessment_id==ModuleAssessment.id, "
                   "ModuleAssessment.module_id==EnrollmentProgress.module_id)",
        viewonly=True
    )