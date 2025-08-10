from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List
from .base import Base

class Student(Base):
    __tablename__ = "students"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    parent_email: Mapped[str] = mapped_column(String(255), nullable=False)
    access_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    class_label: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    progress: Mapped[List["EnrollmentProgress"]] = relationship(back_populates="student")
    assessments: Mapped[List["AssessmentResult"]] = relationship(back_populates="student")
    badges: Mapped[List["StudentBadge"]] = relationship(back_populates="student")