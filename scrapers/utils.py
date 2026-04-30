import httpx

async def geocode_city(city_name: str) -> list:
    """Search for a city name using Open-Meteo Geocoding API."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=5&language=en&format=json"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
        return data.get("results", [])

async def reverse_geocode(lat: float, lon: float) -> str:
    """Reverse geocode using Nominatim (OpenStreetMap) to get a city name."""
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {"User-Agent": "LiveDash/1.0"}

    async with httpx.AsyncClient(timeout=10, headers=headers) as client:
        r = await client.get(url)
        if r.status_code == 200:
            data = r.json()
            address = data.get("address", {})
            return address.get("city") or address.get("town") or address.get("village") or address.get("county") or "Unknown Location"
    return "Unknown Location"

async def get_ip_location() -> dict:
    """Get approximate location based on IP."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("https://ipapi.co/json/")
            if r.status_code == 200:
                data = r.json()
                return {
                    "lat": data.get("latitude"),
                    "lon": data.get("longitude"),
                    "city": data.get("city")
                }
    except Exception:
        pass
    return None
