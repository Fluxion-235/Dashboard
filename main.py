import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from scrapers.weather import fetch_weather, fetch_aqi
from scrapers.news import fetch_all_news
from scrapers.utils import geocode_city, get_ip_location, reverse_geocode

app = FastAPI(title="LiveDash API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/api/weather")
async def weather(lat: float = 7.2096, lon: float = 79.8378, city: str = "Negombo"):
    return await fetch_weather(lat, lon, city)

@app.get("/api/aqi")
async def aqi(lat: float = 7.2096, lon: float = 79.8378):
    return await fetch_aqi(lat, lon)

@app.get("/api/news")
async def news(category: str = "all"):
    return await fetch_all_news(category)

@app.get("/api/geocode")
async def geocode(q: str):
    return await geocode_city(q)

@app.get("/api/detect-location")
async def detect_location():
    loc = await get_ip_location()
    return loc

@app.get("/api/reverse-geocode")
async def rev_geocode(lat: float, lon: float):
    city = await reverse_geocode(lat, lon)
    return {"city": city}

@app.get("/api/all")
async def all_data(lat: float = 7.2096, lon: float = 79.8378, city: str = "Negombo"):
    w, n, a = await asyncio.gather(
        fetch_weather(lat, lon, city),
        fetch_all_news("all"),
        fetch_aqi(lat, lon),
    )
    return {"weather": w, "news": n, "aqi": a}