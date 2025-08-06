from sqlalchemy.orm import Session
from models.chart import Chart
from schemas.chart import AstroInput, AstroPairInput
from kerykeion import AstrologicalSubject, KerykeionChartSVG, Report
from kerykeion.relationship_score.relationship_score_factory import RelationshipScoreFactory
from kerykeion.aspects import SynastryAspects
from kerykeion.composite_subject_factory import CompositeSubjectFactory
from datetime import datetime
from itertools import combinations
import json
import uuid
from typing import Dict, Any

# ----- Astrology Constants -----
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

def create_subject(data: AstroInput) -> AstrologicalSubject:
    """Create an AstrologicalSubject from input data"""
    d = data.dict()
    d["minute"] = d.pop("minute")
    return AstrologicalSubject(**d)

def calculate_dms(abs_pos: float):
    """Calculate degrees, minutes, seconds from absolute position"""
    degree = int(abs_pos)
    minutes = int((abs_pos - degree) * 60)
    seconds = int(((abs_pos - degree) * 60 - minutes) * 60)
    return degree, minutes, seconds

def sort_planet_data(planet: dict) -> dict:
    """Add degree, minutes, seconds to planet data"""
    degree, minutes, seconds = calculate_dms(planet['abs_pos'])
    return {**planet, "degree": degree, "minutes": minutes, "seconds": seconds}

def extract_aspects(data: dict) -> list:
    """Extract aspects between planets"""
    planets = data["planets_names_list"]
    aspects_found = []
    for p1, p2 in combinations(planets, 2):
        pos1 = data[p1.lower()]["abs_pos"]
        pos2 = data[p2.lower()]["abs_pos"]
        angle = abs(pos1 - pos2)
        angle = min(angle, 360 - angle)
        for name, exact in ASPECTS.items():
            if abs(angle - exact) <= 5:
                aspects_found.append({
                    "planet1": p1, 
                    "planet2": p2, 
                    "aspect": name, 
                    "angle": round(angle, 2)
                })
    return aspects_found

def calculate_element_percentage(data: dict) -> dict:
    """Calculate element distribution percentages"""
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
    """Build complete chart data"""
    return {
        "Planet": {p: sort_planet_data(data[p]) for p in PLANETS if p in data},
        "Houses": {h: data[h] for h in HOUSES if h in data},
        "Elements": calculate_element_percentage(data),
        "Aspects": extract_aspects(data)
    }

def simplify_astrology_data(raw_data):
    """Simplify astrology data for frontend consumption"""
    from copy import deepcopy

    data = raw_data["chart"]
    planets = data["Planet"]
    houses = data["Houses"]
    aspects = data["Aspects"]
    elements = data["Elements"]

    # تبدیل نام‌های کوتاه صور فلکی به کامل
    sign_full = {
        "Ari": "Aries", "Tau": "Taurus", "Gem": "Gemini", "Can": "Cancer",
        "Leo": "Leo", "Vir": "Virgo", "Lib": "Libra", "Sco": "Scorpio",
        "Sag": "Sagittarius", "Cap": "Capricorn", "Aqu": "Aquarius", "Pis": "Pisces"
    }

    # ساخت دیکشنری خانه‌ها
    house_info_by_name = {
        h_data["name"]: {
            "number": i+1,
            "sign": sign_full.get(h_data["sign"], h_data["sign"]),
            "element": h_data["element"],
            "quality": h_data["quality"]
        }
        for i, h_data in enumerate(houses.values())
    }

    # ترکیب اطلاعات سیارات و خانه‌ها
    simplified_planets = []
    for pid, p in planets.items():
        house_data = house_info_by_name.get(p["house"], {})
        simplified_planets.append({
            "id": pid,
            "name": p["name"],
            "sign": sign_full.get(p["sign"], p["sign"]),
            "element": p["element"],
            "quality": p["quality"],
            "retrograde": p["retrograde"],
            "degree": {
                "full": round(p["abs_pos"], 4),
                "deg": p["degree"],
                "min": p["minutes"],
                "sec": p["seconds"]
            },
            "house": house_data
        })

    # ساده‌سازی جنبه‌ها
    simplified_aspects = [
        {
            "between": [a["planet1"], a["planet2"]],
            "aspect": a["aspect"],
            "angle": a["angle"]
        }
        for a in aspects
    ]

    return {
        "planets": simplified_planets,
        "aspects": simplified_aspects,
        "elementsSummary": deepcopy(elements)
    }

def generate_natal_chart(data: AstroInput) -> Dict[str, Any]:
    """Generate natal chart data"""
    subject = create_subject(data)
    astro_data = json.loads(subject.json(dump=True))
    return {"chart": build_chart(astro_data)}

def generate_chart_svg(data: AstroInput) -> str:
    """Generate SVG chart and return filename"""
    subject = create_subject(data)
    filename = f"svg/{data.name} - Natal Chart.svg"
    chart = KerykeionChartSVG(subject, new_output_directory="svg", chart_type="Natal")
    chart.makeSVG()
    return filename

def generate_full_report(data: AstroInput) -> str:
    """Generate full natal report"""
    subject = create_subject(data)
    report = Report(subject)
    return report.get_full_report()

def generate_synastry_aspects(data: AstroPairInput) -> list:
    """Generate synastry aspects between two charts"""
    s1 = create_subject(data.person1)
    s2 = create_subject(data.person2)
    synastry = SynastryAspects(s1, s2)
    return synastry.all_aspects

def generate_relationship_score(data: AstroPairInput) -> Dict[str, Any]:
    """Generate relationship compatibility score"""
    s1 = create_subject(data.person1)
    s2 = create_subject(data.person2)
    score = RelationshipScoreFactory(s1, s2).get_relationship_score()
    return {"score": score}

def generate_composite_chart(data: AstroPairInput) -> Dict[str, Any]:
    """Generate composite chart"""
    s1 = create_subject(data.person1)
    s2 = create_subject(data.person2)
    composite = CompositeSubjectFactory(s1, s2).get_midpoint_composite_subject_model()
    return composite

def save_chart_to_db(db: Session, user_id: uuid.UUID, chart_data: Dict[str, Any], 
                     label: str, birth_date: datetime, birth_time: datetime, 
                     birth_place: str) -> Chart:
    """Save chart data to database"""
    chart = Chart(
        user_id=user_id,
        label=label,
        birth_date=birth_date.date(),
        birth_time=birth_time.time(),
        birth_place=birth_place,
        chart_json=chart_data
    )
    db.add(chart)
    db.commit()
    db.refresh(chart)
    return chart

def get_user_charts(db: Session, user_id: uuid.UUID) -> list[Chart]:
    """Get all charts for a user"""
    return db.query(Chart).filter(Chart.user_id == user_id).all()

def get_chart_by_id(db: Session, chart_id: uuid.UUID) -> Chart:
    """Get chart by ID"""
    return db.query(Chart).filter(Chart.id == chart_id).first()
