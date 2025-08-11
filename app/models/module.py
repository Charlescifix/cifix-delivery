from sqlalchemy import String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List
from .base import Base

class Module(Base):
    __tablename__ = "modules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    week_no: Mapped[int] = mapped_column(Integer, nullable=False)
    video_url: Mapped[str] = mapped_column(Text, nullable=True)
    resource_url: Mapped[str] = mapped_column(Text, nullable=True)
    meet_url: Mapped[str] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    progress: Mapped[List["EnrollmentProgress"]] = relationship(back_populates="module")
    module_assessment: Mapped["ModuleAssessment"] = relationship(back_populates="module", uselist=False)