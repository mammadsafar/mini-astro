from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
from pytz import timezone
from itertools import combinations
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json
import uuid

from kerykeion import AstrologicalSubject, KerykeionChartSVG, Report
from kerykeion.relationship_score.relationship_score import RelationshipScore
from kerykeion.relationship_score.relationship_score_factory import RelationshipScoreFactory
from kerykeion.aspects import SynastryAspects, NatalAspects
from kerykeion.enums import Planets, Aspects, Signs
from kerykeion.composite_subject_factory import CompositeSubjectFactory

# ----- Setup FastAPI -----
app = FastAPI(title="Astrology API", description="Full-featured astrology API based on kerykeion library", version="1.0.0")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # یا فقط دامنه‌هایی که قراره به API وصل شن، مثلاً ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],
)

# ----- Setup SQLAlchemy -----
SQLALCHEMY_DATABASE_URL = "sqlite:///./astrology.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- User Model -----
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    hour = Column(Integer)
    minute = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)
    city = Column(String)
    tz_str = Column(String)

    @property
    def birthdate(self):
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    @property
    def birthtime(self):
        return f"{self.hour:02d}:{self.minute:02d}"

Base.metadata.create_all(bind=engine)

# ----- Pydantic Schemas -----
class UserCreate(BaseModel):
    name: str
    birthdate: str
    birthtime: str
    lat: float
    lng: float
    city: str
    tz_str: str

class UserOut(UserCreate):
    id: int
    model_config = {
        "from_attributes": True
    }


# ----- Astrology Logic -----
PLANETS = [
    "sun", "moon", "mercury", "venus", "mars",
    "jupiter", "saturn", "uranus", "neptune", "pluto",
    "true_node", "mean_node", "chiron", "mean_lilith",
    "true_south_node", "mean_south_node"
]

HOUSES = [
    "first_house", "second_house", "third_house", "fourth_house",
    "fifth_house", "sixth_house", "seventh_house", "eighth_house",
    "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"
]

ELEMENTS = {
    "fire": {"Ari", "Leo", "Sag"},
    "earth": {"Tau", "Vir", "Cap"},
    "air": {"Gem", "Lib", "Aqu"},
    "water": {"Can", "Sco", "Pis"}
}

ASPECTS = {
    "Conjunction": 0, "Opposition": 180,
    "Trine": 120, "Square": 90, "Sextile": 60
}


class AstroInput(BaseModel):
    name: str = Field(..., example="Alice")
    year: int = Field(..., example=1990)
    month: int = Field(..., example=5)
    day: int = Field(..., example=15)
    hour: int = Field(..., example=14)
    minute: int = Field(..., example=30)
    lat: float = Field(..., example=35.6892)
    lng: float = Field(..., example=51.3890)
    city: str = Field(..., example="Tehran")
    tz_str: str = Field(..., example="Asia/Tehran")

class AstroPairInput(BaseModel):
    person1: AstroInput
    person2: AstroInput

def create_subject(data: AstroInput) -> AstrologicalSubject:
    d = data.dict()
    d["minute"] = d.pop("minute")
    return AstrologicalSubject(**d)

def calculate_dms(abs_pos: float):
    degree = int(abs_pos)
    minutes = int((abs_pos - degree) * 60)
    seconds = int(((abs_pos - degree) * 60 - minutes) * 60)
    return degree, minutes, seconds

def sort_planet_data(planet: dict) -> dict:
    degree, minutes, seconds = calculate_dms(planet['abs_pos'])
    return {**planet, "degree": degree, "minutes": minutes, "seconds": seconds}

def extract_aspects(data: dict) -> list:
    planets = data["planets_names_list"]
    aspects_found = []
    for p1, p2 in combinations(planets, 2):
        pos1 = data[p1.lower()]["abs_pos"]
        pos2 = data[p2.lower()]["abs_pos"]
        angle = abs(pos1 - pos2)
        angle = min(angle, 360 - angle)
        for name, exact in ASPECTS.items():
            if abs(angle - exact) <= 5:
                aspects_found.append({"planet1": p1, "planet2": p2, "aspect": name, "angle": round(angle, 2)})
    return aspects_found

def calculate_element_percentage(data: dict) -> dict:
    counts = {key: 0 for key in ELEMENTS}
    planets = data["planets_names_list"][:10]
    for planet in planets:
        sign = data[planet.lower()]["sign"]
        for element, signs in ELEMENTS.items():
            if sign in signs:
                counts[element] += 1
                break
    total = len(planets)
    return {k: round((v / total) * 100, 2) for k, v in counts.items()}

def build_chart(data: dict) -> dict:
    return {
        "Planet": {p: sort_planet_data(data[p]) for p in PLANETS if p in data},
        "Houses": {h: data[h] for h in HOUSES if h in data},
        "Elements": calculate_element_percentage(data),
        "Aspects": extract_aspects(data)
    }

# ----- CRUD Endpoints -----
@app.post("/users/", response_model=UserOut, summary="Create New User (JSON)", description="Creat new User chart.")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = {
        "name": user.name,
        "year": int(user.birthdate.split('-')[0]),
        "month": int(user.birthdate.split('-')[1]),
        "day": int(user.birthdate.split('-')[2]),
        "hour": int(user.birthtime.split(':')[0]),
        "minute": int(user.birthtime.split(':')[1]),
        "lat": user.lat,
        "lng": user.lng,
        "city": user.city,
        "tz_str": user.tz_str,
    }
    db_user = User(**new_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = {
        "name":user_data.name,
        "year": user_data.birthdate.split('-')[0],
        "month":user_data.birthdate.split('-')[1],
        "day":user_data.birthdate.split('-')[2],
        "hour":user_data.birthtime.split(':')[0],
        "minute":user_data.birthtime.split(':')[1],
        "lat":user_data.lat,
        "lng":user_data.lng,
        "city":user_data.city,
        "tz_str":user_data.tz_str,
    }
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in new_user.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

@app.post("/astro/chart-json", summary="Generate Natal Chart (JSON)", description="Returns detailed natal chart as JSON including planets, houses, elements, and aspects.")
def get_astrological_chart(data: AstroInput):
    print(data)
    subject = create_subject(data)
    astro_data = json.loads(subject.json(dump=True))
    return {"chart": build_chart(astro_data)}

@app.post("/astro/chart-svg", summary="Generate Natal Chart SVG", description="Returns natal chart as an SVG image.")
def generate_chart_svg(data: AstroInput):
    subject = create_subject(data)
    filename = f"svg/{data.name} - Natal Chart.svg"
    chart = KerykeionChartSVG(subject, new_output_directory="svg", chart_type="Natal")
    chart.makeSVG()

    def iterfile():
        with open(filename, "rb") as f:
            yield from f

    return StreamingResponse(iterfile(), media_type="image/svg+xml")

@app.post("/astro/report", summary="Full Natal Report", description="Returns a full natural language report based on the natal chart.")
def get_full_report(data: AstroInput):
    subject = create_subject(data)
    report = Report(subject)
    return {"report": report.get_full_report()}

@app.post("/astro/synastry", summary="Synastry Aspects", description="Returns relationship aspects between two birth charts.")
def get_synastry_aspects(data: AstroPairInput):
    s1 = create_subject(data.person1)
    s2 = create_subject(data.person2)
    synastry = SynastryAspects(s1, s2)
    return {"aspects": synastry.all_aspects}

@app.post("/astro/relationship-score", summary="Relationship Score", description="Returns a compatibility score and explanation for a pair of charts.")
def get_relationship_score(data: AstroPairInput):
    s1 = create_subject(data.person1)
    s2 = create_subject(data.person2)
    score = RelationshipScoreFactory(s1, s2).get_relationship_score()
    return {"score": score}

@app.post("/astro/composite", summary="Composite Chart", description="Returns composite chart (combined energy) for two birth charts.")
def get_composite_chart(data: AstroPairInput):
    s1 = create_subject(data.person1)
    s2 = create_subject(data.person2)
    composite = CompositeSubjectFactory(s1, s2).get_midpoint_composite_subject_model()
    return composite
