from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from .base import Base

class ProgressStatus(PyEnum):
    NOT_STARTED = "NOT_STARTED"
    STARTED = "STARTED"
    DONE = "DONE"

class EnrollmentProgress(Base):
    __tablename__ = "enrollment_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    status: Mapped[ProgressStatus] = mapped_column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    student: Mapped["Student"] = relationship(back_populates="progress")
    module: Mapped["Module"] = relationship(back_populates="progress")

class Badge(Base):
    __tablename__ = "badges"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    criteria: Mapped[str] = mapped_column(String, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    student_badges: Mapped[list["StudentBadge"]] = relationship(back_populates="badge")

class StudentBadge(Base):
    __tablename__ = "student_badges"
    
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"), primary_key=True)
    awarded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    student: Mapped["Student"] = relationship(back_populates="badges")
    badge: Mapped["Badge"] = relationship(back_populates="student_badges")