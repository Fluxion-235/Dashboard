import httpx
from datetime import datetime

WMO_CODES = {
    0:("Clear sky","sunny"), 1:("Mainly clear","sunny"), 2:("Partly cloudy","cloudy"),
    3:("Overcast","cloudy"), 45:("Foggy","fog"), 48:("Icy fog","fog"),
    51:("Light drizzle","rain"), 53:("Moderate drizzle","rain"), 55:("Dense drizzle","rain"),
    61:("Slight rain","rain"), 63:("Moderate rain","rain"), 65:("Heavy rain","rain"),
    71:("Slight snow","snow"), 73:("Moderate snow","snow"), 75:("Heavy snow","snow"),
    80:("Rain showers","rain"), 81:("Moderate showers","rain"), 82:("Violent showers","rain"),
    95:("Thunderstorm","thunder"), 96:("Thunderstorm + hail","thunder"), 99:("Heavy thunderstorm","thunder"),
}

async def fetch_weather(lat: float, lon: float, city: str) -> dict:
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation_probability,"
        f"weathercode,windspeed_10m,apparent_temperature,uv_index"
        f"&hourly=precipitation_probability,temperature_2m,weathercode"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min,"
        f"precipitation_probability_max,sunrise,sunset,uv_index_max"
        f"&timezone=auto&forecast_days=7"
    )
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    cur = data["current"]
    code = cur.get("weathercode", 0)
    desc, icon_type = WMO_CODES.get(code, ("Unknown", "cloudy"))

    daily = data["daily"]
    forecast = []
    for i in range(7):
        d_code = daily["weathercode"][i]
        d_desc, d_icon = WMO_CODES.get(d_code, ("Unknown", "cloudy"))
        forecast.append({
            "date": daily["time"][i],
            "description": d_desc,
            "icon_type": d_icon,
            "max_temp": daily["temperature_2m_max"][i],
            "min_temp": daily["temperature_2m_min"][i],
            "rain_chance": daily["precipitation_probability_max"][i],
            "sunrise": daily["sunrise"][i],
            "sunset": daily["sunset"][i],
            "uv_index_max": daily.get("uv_index_max", [None]*7)[i],
        })

    return {
        "city": city, "lat": lat, "lon": lon,
        "temperature": cur["temperature_2m"],
        "feels_like": cur["apparent_temperature"],
        "humidity": cur["relative_humidity_2m"],
        "wind_speed": cur["windspeed_10m"],
        "rain_chance": cur["precipitation_probability"],
        "uv_index": cur.get("uv_index", 0),
        "description": desc,
        "icon_type": icon_type,
        "forecast": forecast,
        "hourly_rain": data["hourly"]["precipitation_probability"][:24],
        "hourly_temp": data["hourly"]["temperature_2m"][:24],
        "hourly_times": data["hourly"]["time"][:24],
        "fetched_at": datetime.now().isoformat(),
    }


async def fetch_aqi(lat: float, lon: float) -> dict:
    """Air quality via Open-Meteo Air Quality API — free, no key."""
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        f"&current=us_aqi,pm10,pm2_5,ozone,nitrogen_dioxide"
    )
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        d = r.json()["current"]

    aqi = d.get("us_aqi", 0)
    return {
        "aqi": round(aqi) if aqi else None,
        "pm25": round(d.get("pm2_5", 0), 1),
        "pm10": round(d.get("pm10", 0), 1),
        "o3":   round(d.get("ozone", 0), 1),
        "no2":  round(d.get("nitrogen_dioxide", 0), 1),
    }
