from weasyprint import HTML, CSS
from jinja2 import Template
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Dict, Any
import json
from ..models import Student, Module, EnrollmentProgress, AssessmentResult, ProgressStatus

class ReportService:
    
    @staticmethod
    def generate_pdf_report(student_data: Dict[str, Any]) -> bytes:
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { text-align: center; margin-bottom: 30px; }
                .section { margin-bottom: 25px; }
                .progress-bar { 
                    width: 100%; 
                    height: 20px; 
                    background-color: #f0f0f0; 
                    border-radius: 10px; 
                    overflow: hidden; 
                }
                .progress-fill { 
                    height: 100%; 
                    background-color: #4CAF50; 
                    transition: width 0.3s ease; 
                }
                .module-item { 
                    padding: 10px; 
                    margin: 5px 0; 
                    border-left: 4px solid #ddd; 
                }
                .module-done { border-left-color: #4CAF50; }
                .module-started { border-left-color: #FFC107; }
                .stats-grid { 
                    display: grid; 
                    grid-template-columns: 1fr 1fr 1fr; 
                    gap: 20px; 
                    margin: 20px 0; 
                }
                .stat-box { 
                    text-align: center; 
                    padding: 15px; 
                    background-color: #f8f9fa; 
                    border-radius: 8px; 
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎓 Learning Progress Report</h1>
                <h2>{{ student.first_name }}</h2>
                <p>Generated on {{ report_date }}</p>
            </div>
            
            <div class="section">
                <h3>📊 Overall Progress</h3>
                <div class="stats-grid">
                    <div class="stat-box">
                        <h4>{{ completed_modules }}</h4>
                        <p>Modules Completed</p>
                    </div>
                    <div class="stat-box">
                        <h4>⭐ {{ total_stars }}</h4>
                        <p>Stars Earned</p>
                    </div>
                    <div class="stat-box">
                        <h4>{{ progress_percentage }}%</h4>
                        <p>Course Progress</p>
                    </div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ progress_percentage }}%"></div>
                </div>
            </div>
            
            {% if latest_assessment %}
            <div class="section">
                <h3>🧪 Latest Assessment</h3>
                <p><strong>Level:</strong> {{ latest_assessment.level }}</p>
                <p><strong>Score:</strong> {{ latest_assessment.raw_score }}/100</p>
                <p><strong>Date:</strong> {{ latest_assessment.completed_at.strftime('%Y-%m-%d') }}</p>
                
                {% if domain_breakdown %}
                <h4>Domain Breakdown:</h4>
                <ul>
                    {% for domain, score in domain_breakdown.items() %}
                    <li><strong>{{ domain.title() }}:</strong> {{ score }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endif %}
            
            <div class="section">
                <h3>📚 Module Progress</h3>
                {% for module in modules %}
                <div class="module-item {% if progress_data.get(module.id) and progress_data[module.id].status.value == 'DONE' %}module-done{% elif progress_data.get(module.id) and progress_data[module.id].status.value == 'STARTED' %}module-started{% endif %}">
                    <strong>Week {{ module.week_no }}: {{ module.title }}</strong>
                    <p>Status: 
                        {% if progress_data.get(module.id) %}
                            {% if progress_data[module.id].status.value == 'DONE' %}
                                ✅ Completed ({{ progress_data[module.id].stars }} stars)
                            {% elif progress_data[module.id].status.value == 'STARTED' %}
                                🟡 In Progress
                            {% else %}
                                ⭕ Not Started
                            {% endif %}
                        {% else %}
                            ⭕ Not Started
                        {% endif %}
                    </p>
                </div>
                {% endfor %}
            </div>
            
            <div class="section" style="margin-top: 40px; text-align: center; color: #666;">
                <p><em>Keep up the great work! 🌟</em></p>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(**student_data)
        
        html_doc = HTML(string=html_content)
        return html_doc.write_pdf()
    
    @staticmethod
    async def get_student_report_data(student: Student, db: AsyncSession) -> Dict[str, Any]:
        # Get all modules
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
        
        # Calculate stats
        total_modules = len(modules)
        completed_modules = sum(1 for m in modules if progress_data.get(m.id) and progress_data[m.id].status == ProgressStatus.DONE)
        total_stars = sum(p.stars for p in progress_data.values())
        progress_percentage = int((completed_modules / total_modules) * 100) if total_modules > 0 else 0
        
        # Parse domain breakdown if available
        domain_breakdown = None
        if latest_assessment and latest_assessment.domain_breakdown:
            try:
                domain_breakdown = json.loads(latest_assessment.domain_breakdown)
            except:
                pass
        
        return {
            "student": student,
            "modules": modules,
            "progress_data": progress_data,
            "latest_assessment": latest_assessment,
            "domain_breakdown": domain_breakdown,
            "total_modules": total_modules,
            "completed_modules": completed_modules,
            "total_stars": total_stars,
            "progress_percentage": progress_percentage,
            "report_date": datetime.now().strftime("%B %d, %Y")
        }