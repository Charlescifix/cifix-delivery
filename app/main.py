from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from .routes import public, student, parent, admin, assessment
from .models import engine, Base
from .templates_config import templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="CIFIX Kids Hub",
    description="A kid-friendly learning hub with assessments and progress tracking",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(public.router, tags=["Public"])
app.include_router(student.router, tags=["Student"])
app.include_router(parent.router, tags=["Parent"])
app.include_router(admin.router, tags=["Admin"])
app.include_router(assessment.router, tags=["Assessment"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "CIFIX Kids Hub is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)