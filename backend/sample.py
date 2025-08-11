from kerykeion import AstrologicalSubject

import json
from pydantic import BaseModel, Field


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

def create_subject(data: AstroInput) -> AstrologicalSubject:
    d = data.dict()
    return simplify_astrology_data(AstrologicalSubject(**d))

def simplify_astrology_data(raw_data):
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

    # ساخت دیکشنری خانه‌ها با key خانه مثل "Fourth_House"
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

def get_astrological_chart(data: AstroInput):
    subject = create_subject(data)