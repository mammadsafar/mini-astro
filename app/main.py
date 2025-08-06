from fastapi import FastAPI
from api.v1 import users, astrology, charts, auth
from core.config import settings
from db.init_db import init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Astrology API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(charts.router, prefix="/api/v1/charts", tags=["charts"])
app.include_router(astrology.router, prefix="/api/v1/astro", tags=["astrology"])

@app.get("/")
async def root():
    return {"message": "Welcome to Astrology API"}