from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import (auth, children, consultations, dashboard, diet_plan, growth, nutrition,
                    pregnancy, reminders)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Coco NutriCare API",
    description="Backend for Coco NutriCare - nutrition & health support for children and mothers.",
    version="1.0.0",
)

# CORS configuration updated to allow all origins during testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, dashboard, children, growth, nutrition, diet_plan, pregnancy, reminders, consultations):
    app.include_router(r.router, prefix="/api")


@app.get("/", tags=["Health"])
def root():
    return {"app": "Coco NutriCare API", "docs": "/docs"}