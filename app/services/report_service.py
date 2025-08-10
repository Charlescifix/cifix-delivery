from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Dict, Any
import json
import io
from ..models import Student, Module, EnrollmentProgress, AssessmentResult, ProgressStatus

class ReportService:
    
    @staticmethod
    def generate_pdf_report(student_data: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.darkgreen,
            spaceAfter=20
        )
        
        # Title
        story.append(Paragraph("🎓 Learning Progress Report", title_style))
        story.append(Paragraph(f"<b>{student_data['student'].first_name}</b>", styles['Heading2']))
        story.append(Paragraph(f"Generated on {student_data['report_date']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Overall Progress Section
        story.append(Paragraph("📊 Overall Progress", subtitle_style))
        
        # Stats table
        stats_data = [
            ['Modules Completed', 'Stars Earned', 'Course Progress'],
            [
                str(student_data['completed_modules']),
                f"⭐ {student_data['total_stars']}",
                f"{student_data['progress_percentage']}%"
            ]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Assessment Section (if available)
        if student_data.get('latest_assessment'):
            story.append(Paragraph("🧪 Latest Assessment", subtitle_style))
            assessment = student_data['latest_assessment']
            
            assessment_info = f"""
            <b>Level:</b> {assessment.level}<br/>
            <b>Score:</b> {assessment.raw_score}/100<br/>
            <b>Date:</b> {assessment.completed_at.strftime('%Y-%m-%d')}
            """
            story.append(Paragraph(assessment_info, styles['Normal']))
            
            # Domain breakdown
            if student_data.get('domain_breakdown'):
                story.append(Paragraph("<b>Domain Breakdown:</b>", styles['Normal']))
                for domain, score in student_data['domain_breakdown'].items():
                    story.append(Paragraph(f"• <b>{domain.title()}:</b> {score}", styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # Module Progress Section
        story.append(Paragraph("📚 Module Progress", subtitle_style))
        
        # Module progress table
        module_data = [['Week', 'Module Title', 'Status', 'Stars']]
        
        for module in student_data['modules']:
            progress = student_data['progress_data'].get(module.id)
            if progress:
                if progress.status == ProgressStatus.DONE:
                    status = "✅ Completed"
                    stars = str(progress.stars)
                elif progress.status == ProgressStatus.STARTED:
                    status = "🟡 In Progress"
                    stars = "0"
                else:
                    status = "⭕ Not Started"
                    stars = "0"
            else:
                status = "⭕ Not Started"
                stars = "0"
            
            module_data.append([
                f"Week {module.week_no}",
                module.title,
                status,
                stars
            ])
        
        module_table = Table(module_data, colWidths=[1*inch, 3*inch, 1.5*inch, 0.5*inch])
        module_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(module_table)
        story.append(Spacer(1, 40))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("<i>Keep up the great work! 🌟</i>", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
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