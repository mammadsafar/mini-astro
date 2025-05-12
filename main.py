from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from kerykeion import AstrologicalSubject, Report, KerykeionChartSVG
from datetime import datetime
from pytz import timezone


import json
from itertools import combinations
import uuid

app = FastAPI()

class AstroInput(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int
    minut: int
    lat: float
    lng: float
    city: str
    tz_str: str

def extract_aspects(astrology_data):
    planets = astrology_data["planets_names_list"]
    aspects = {"Conjunction": 0, "Opposition": 180, "Trine": 120, "Square": 90, "Sextile": 60}
    extracted_aspects = []
    for p1, p2 in combinations(planets, 2):
        pos1 = astrology_data[p1.lower()]["abs_pos"]
        pos2 = astrology_data[p2.lower()]["abs_pos"]
        angle = abs(pos1 - pos2)
        angle = min(angle, 360 - angle)
        for aspect, exact_angle in aspects.items():
            if abs(angle - exact_angle) <= 5:
                extracted_aspects.append({"planet1": p1, "planet2": p2, "aspect": aspect, "angle": round(angle, 2)})
    return extracted_aspects

def calculate_dms(abs_pos):
    degree = int(abs_pos)
    minutes = int((abs_pos - degree) * 60)
    seconds = int(((abs_pos - degree) * 60 - minutes) * 60)
    return degree, minutes, seconds

def sort_planet_data(planet):
    degree, minutes, seconds = calculate_dms(planet['abs_pos'])
    return {**planet, "degree": degree, "minutes": minutes, "seconds": seconds}

def calculate_element_percentage(json_data):
    elements = {"fire": {"Ari", "Leo", "Sag"}, "earth": {"Tau", "Vir", "Cap"}, "air": {"Gem", "Lib", "Aqu"}, "water": {"Can", "Sco", "Pis"}}
    element_counts = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    total_planets = len(json_data["planets_names_list"])
    for planet in json_data["planets_names_list"][:10]:
        zodiac_sign = json_data[planet.lower()]["sign"]
        for element, signs in elements.items():
            if zodiac_sign in signs:
                element_counts[element] += 1
                break
    return {key: round((count / total_planets) * 100, 2) for key, count in element_counts.items()}

@app.post("/astro")
def get_astrological_chart(data: AstroInput):
    subject = AstrologicalSubject(data.name, data.year, data.month, data.day, data.hour, data.minut, data.city, lng=data.lng, lat=data.lat, online=False, tz_str=data.tz_str)
    astrology_data = json.loads(subject.json(dump=True))
    element_percentages = calculate_element_percentage(astrology_data)
    astro_chart = {
        "Planet": {planet: sort_planet_data(astrology_data[planet]) for planet in astrology_data if planet in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "true_node", "mean_node", "chiron", "mean_lilith", "true_south_node", "mean_south_node"]},
        "Houses": {house: astrology_data[house] for house in ["first_house", "second_house", "third_house", "fourth_house", "fifth_house", "sixth_house", "seventh_house", "eighth_house", "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"]},
        "Elements": element_percentages,
        "Aspects": extract_aspects(astrology_data)
    }
    return {"Text":str(astro_chart)}

@app.get("/astro/today")
def get_astrological_chart():
        # تنظیم تاریخ و زمان اکنون در منطقه زمانی نیویورک
    ny_tz = timezone("America/New_York")
    now_ny = datetime.now(ny_tz)

    # مختصات نیویورک
    city = "New York"
    lat = 40.7128
    lng = -74.0060
    tz_str = "America/New_York"

    # ساخت نمونه AstrologicalSubject
    subject = AstrologicalSubject(
        'New York',
        now_ny.year,
        now_ny.month,
        now_ny.day,
        now_ny.hour,
        now_ny.minute,
        city,
        lng=lng,
        lat=lat,
        online=False,
        tz_str=tz_str
    )
    # subject = AstrologicalSubject(data.name, data.year, data.month, data.day, data.hour, data.minut, data.city, lng=data.lng, lat=data.lat, online=False, tz_str=data.tz_str)
    astrology_data = json.loads(subject.json(dump=True))
    element_percentages = calculate_element_percentage(astrology_data)
    astro_chart = {
        "Planet": {planet: sort_planet_data(astrology_data[planet]) for planet in astrology_data if planet in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "true_node", "mean_node", "chiron", "mean_lilith", "true_south_node", "mean_south_node"]},
        "Houses": {house: astrology_data[house] for house in ["first_house", "second_house", "third_house", "fourth_house", "fifth_house", "sixth_house", "seventh_house", "eighth_house", "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"]},
        "Elements": element_percentages,
        "Aspects": extract_aspects(astrology_data)
    }
    return astro_chart
    # return {"Text":"yes"}

@app.post("/astro/chart")
def generate_chart_svg(data: AstroInput):
    subject = AstrologicalSubject(
        data.name, data.year, data.month, data.day, data.hour, data.minut,
        data.city, lng=data.lng, lat=data.lat, online=False, tz_str=data.tz_str
    )

    unique_id = str(uuid.uuid4())
    svg_filename = f"svg/{data.name} - Natal Chart.svg"
    png_filename = f"chart_{unique_id}.png"

    svg_chart = KerykeionChartSVG(subject, new_output_directory="svg", chart_type="Natal")
    svg_chart.makeSVG()  # ایجاد فایل SVG

    # روش ۱: استفاده از Wand (ImageMagick) برای تبدیل (بهتر از cairosvg)
    # with Image(filename=svg_filename) as img:
    #     img.format = "png"
    #     img.save(filename=png_filename)

    # روش ۲: cairosvg (در صورتی که Wand جواب نداد)
    # cairosvg.svg2png(url=svg_filename, write_to=png_filename)

    def iterfile():
        with open(svg_filename, "rb") as file:
            yield from file

    return StreamingResponse(iterfile(), media_type="image/svg+xml")

 # ایجاد فایل SVG در مسیر جاری
