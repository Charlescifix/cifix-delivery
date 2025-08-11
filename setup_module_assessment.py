#!/usr/bin/env python3
"""
Set up the Introduction to Python module assessment
"""
import asyncio
import json
from app.models import engine, ModuleAssessment, Module
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def setup_assessment():
    # Load the assessment questions
    with open('sample_python_assessment.json', 'r') as f:
        assessment_data = json.load(f)
    
    async with AsyncSession(engine) as db:
        try:
            # Find the Introduction to Python module
            module_stmt = select(Module).where(
                Module.title.ilike('%introduction to python%')
            )
            result = await db.execute(module_stmt)
            python_module = result.scalar_one_or_none()
            
            if not python_module:
                print("Python module not found! Creating one...")
                # Create the module if it doesn't exist
                python_module = Module(
                    title="Introduction to Python Programming",
                    week_no=1,
                    video_url="https://www.youtube.com/watch?v=example",  # Replace with actual URL
                    resource_url="https://repl.it/",  # Python playground
                    is_published=True
                )
                db.add(python_module)
                await db.commit()
                await db.refresh(python_module)
                print(f"Created Python module with ID: {python_module.id}")
            else:
                print(f"Found Python module: {python_module.title} (ID: {python_module.id})")
            
            # Check if assessment already exists
            existing_assessment_stmt = select(ModuleAssessment).where(
                ModuleAssessment.module_id == python_module.id
            )
            existing_result = await db.execute(existing_assessment_stmt)
            existing_assessment = existing_result.scalar_one_or_none()
            
            if existing_assessment:
                print(f"Assessment already exists! Updating it...")
                existing_assessment.questions = json.dumps(assessment_data)
                existing_assessment.title = assessment_data['title']
            else:
                # Create the assessment
                assessment = ModuleAssessment(
                    module_id=python_module.id,
                    title=assessment_data['title'],
                    questions=json.dumps(assessment_data),
                    is_active=True
                )
                db.add(assessment)
                print(f"Created new assessment: {assessment_data['title']}")
            
            await db.commit()
            print("✅ Module assessment setup complete!")
            
            # Show summary
            print(f"\n📊 Assessment Summary:")
            print(f"   Module: {python_module.title} (Week {python_module.week_no})")
            print(f"   Questions: {len(assessment_data['questions'])}")
            print(f"   Passing Score: {assessment_data['scoring']['passing_score']}/10")
            print(f"   Max Stars: {max([int(k) if k.isdigit() else int(k.split('-')[1]) for k in assessment_data['scoring']['star_rewards'].keys()])} stars")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error setting up assessment: {e}")

if __name__ == "__main__":
    asyncio.run(setup_assessment())