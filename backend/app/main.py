from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .routers import auth, checkins, analytics
from .seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="EnergyMe API",
    description="Energy & Focus Tracker — discover your optimal productivity patterns",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(checkins.router)
app.include_router(analytics.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "EnergyMe API", "docs": "/docs"}


@app.post("/api/demo/seed", tags=["Demo"])
def load_demo_data(db: Session = Depends(get_db)):
    """Load 14 days of realistic demo data. Use credentials: demo@energymap.com / demo123"""
    result = seed_demo_data(db)
    return result
