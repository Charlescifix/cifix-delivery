from sqlalchemy import String, Integer, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from .base import Base

class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False)
    domain_breakdown: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    stars_earned: Mapped[int] = mapped_column(Integer, default=3)  # Stars awarded for completing assessment
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)  # Personalized recommendation
    completed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    student: Mapped["Student"] = relationship(back_populates="assessments")