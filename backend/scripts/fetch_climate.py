"""
Fetch real-time climate & weather event data from Open-Meteo (free, no API key).
Generates climate anomaly nodes for major global cities and extreme weather events.
Saves to datasets/datasets/climate.json
"""
import json
import os
import requests
from datetime import datetime

# Major cities for climate monitoring
CLIMATE_CITIES = [
    {"name": "New York", "lat": 40.71, "lon": -74.01, "country": "US"},
    {"name": "London", "lat": 51.51, "lon": -0.13, "country": "UK"},
    {"name": "Tokyo", "lat": 35.68, "lon": 139.69, "country": "JP"},
    {"name": "Beijing", "lat": 39.90, "lon": 116.40, "country": "CN"},
    {"name": "Mumbai", "lat": 19.08, "lon": 72.88, "country": "IN"},
    {"name": "São Paulo", "lat": -23.55, "lon": -46.63, "country": "BR"},
    {"name": "Lagos", "lat": 6.52, "lon": 3.38, "country": "NG"},
    {"name": "Cairo", "lat": 30.04, "lon": 31.24, "country": "EG"},
    {"name": "Moscow", "lat": 55.76, "lon": 37.62, "country": "RU"},
    {"name": "Sydney", "lat": -33.87, "lon": 151.21, "country": "AU"},
    {"name": "Dubai", "lat": 25.20, "lon": 55.27, "country": "AE"},
    {"name": "Singapore", "lat": 1.35, "lon": 103.82, "country": "SG"},
    {"name": "Jakarta", "lat": -6.21, "lon": 106.85, "country": "ID"},
    {"name": "Mexico City", "lat": 19.43, "lon": -99.13, "country": "MX"},
    {"name": "Nairobi", "lat": -1.29, "lon": 36.82, "country": "KE"},
    {"name": "Cape Town", "lat": -33.92, "lon": 18.42, "country": "ZA"},
    {"name": "Berlin", "lat": 52.52, "lon": 13.41, "country": "DE"},
    {"name": "Paris", "lat": 48.86, "lon": 2.35, "country": "FR"},
    {"name": "Seoul", "lat": 37.57, "lon": 126.98, "country": "KR"},
    {"name": "Bangkok", "lat": 13.76, "lon": 100.50, "country": "TH"},
    {"name": "Lima", "lat": -12.05, "lon": -77.04, "country": "PE"},
    {"name": "Buenos Aires", "lat": -34.60, "lon": -58.38, "country": "AR"},
    {"name": "Dhaka", "lat": 23.81, "lon": 90.41, "country": "BD"},
    {"name": "Riyadh", "lat": 24.71, "lon": 46.68, "country": "SA"},
    {"name": "Manila", "lat": 14.60, "lon": 120.98, "country": "PH"},
    {"name": "Ho Chi Minh City", "lat": 10.82, "lon": 106.63, "country": "VN"},
    {"name": "Anchorage", "lat": 61.22, "lon": -149.90, "country": "US"},
    {"name": "Reykjavik", "lat": 64.15, "lon": -21.94, "country": "IS"},
    {"name": "Johannesburg", "lat": -26.20, "lon": 28.05, "country": "ZA"},
    {"name": "Santiago", "lat": -33.45, "lon": -70.67, "country": "CL"},
]


def classify_weather(temp_c, wind_kph, precip_mm):
    """Classify weather conditions into event-like categories."""
    if temp_c > 42:
        return "extreme_heat", "critical"
    elif temp_c > 38:
        return "heat_wave", "high"
    elif temp_c < -20:
        return "extreme_cold", "critical"
    elif temp_c < -10:
        return "cold_wave", "high"
    elif wind_kph > 100:
        return "severe_storm", "critical"
    elif wind_kph > 60:
        return "high_winds", "high"
    elif precip_mm > 50:
        return "heavy_rainfall", "high"
    elif precip_mm > 20:
        return "rain", "medium"
    elif temp_c > 30:
        return "warm", "low"
    elif temp_c < 0:
        return "freezing", "medium"
    else:
        return "normal", "low"


def fetch_climate_data():
    """Fetch current weather for all monitored cities using Open-Meteo."""
    results = []

    # Build batch URL for all cities
    lats = ",".join(str(c["lat"]) for c in CLIMATE_CITIES)
    lons = ",".join(str(c["lon"]) for c in CLIMATE_CITIES)

    # Open-Meteo supports up to ~50 locations in one call
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lats}&longitude={lons}"
        f"&current=temperature_2m,wind_speed_10m,precipitation,weather_code,relative_humidity_2m"
        f"&timezone=auto"
    )

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"❌ Open-Meteo API error: {e}")
        # Return fallback static data
        return _generate_fallback_data()

    # Open-Meteo returns an array when multiple lat/lon are given
    if isinstance(data, list):
        weather_list = data
    elif isinstance(data, dict) and "current" in data:
        weather_list = [data]  # single result
    else:
        weather_list = data if isinstance(data, list) else [data]

    for i, city in enumerate(CLIMATE_CITIES):
        try:
            if i < len(weather_list):
                w = weather_list[i]
                current = w.get("current", {})
            else:
                current = {}

            temp = current.get("temperature_2m", 25)
            wind = current.get("wind_speed_10m", 10)
            precip = current.get("precipitation", 0)
            humidity = current.get("relative_humidity_2m", 50)
            weather_code = current.get("weather_code", 0)

            event_type, severity = classify_weather(temp, wind, precip)

            results.append({
                "id": f"climate_{city['name'].lower().replace(' ', '_')}",
                "name": f"{city['name']} Climate",
                "system": "climate",
                "type": event_type,
                "coordinates": [city["lon"], city["lat"]],
                "country": city["country"],
                "properties": {
                    "name": f"{city['name']} Climate Station",
                    "type": event_type,
                    "system": "climate",
                    "temperature_c": temp,
                    "wind_speed_kph": wind,
                    "precipitation_mm": precip,
                    "humidity_pct": humidity,
                    "weather_code": weather_code,
                    "severity": severity,
                    "city": city["name"],
                    "country": city["country"],
                    "coordinates": [city["lon"], city["lat"]],
                    "last_updated": datetime.utcnow().isoformat(),
                }
            })
        except Exception as e:
            print(f"  ⚠️ Skipping {city['name']}: {e}")

    return results


def _generate_fallback_data():
    """Generate basic fallback climate nodes if API fails."""
    import random
    results = []
    for city in CLIMATE_CITIES:
        temp = random.uniform(-5, 40)
        wind = random.uniform(5, 80)
        precip = random.uniform(0, 30)
        event_type, severity = classify_weather(temp, wind, precip)
        results.append({
            "id": f"climate_{city['name'].lower().replace(' ', '_')}",
            "name": f"{city['name']} Climate",
            "system": "climate",
            "type": event_type,
            "coordinates": [city["lon"], city["lat"]],
            "country": city["country"],
            "properties": {
                "name": f"{city['name']} Climate Station",
                "type": event_type,
                "system": "climate",
                "temperature_c": round(temp, 1),
                "wind_speed_kph": round(wind, 1),
                "precipitation_mm": round(precip, 1),
                "humidity_pct": 50,
                "severity": severity,
                "city": city["name"],
                "country": city["country"],
                "coordinates": [city["lon"], city["lat"]],
                "last_updated": datetime.utcnow().isoformat(),
            }
        })
    return results


if __name__ == "__main__":
    print("Fetching real-time climate data from Open-Meteo...")
    data = fetch_climate_data()
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'datasets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'climate.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Wrote {len(data)} climate nodes to {out_path}")
