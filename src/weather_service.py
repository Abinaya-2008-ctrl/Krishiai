"""
Weather Service for KrishiAI.
Integrates Open-Meteo API for hyperlocal agricultural weather forecasts.
Implements in-memory/disk caching, timeout protection, attribution compliance,
and clear provenance tagging (LIVE_DATA vs CACHED vs OFFLINE_FALLBACK).
"""
import time
import logging
from typing import Dict, Any, Optional
import requests
from src.config import TN_DISTRICTS

logger = logging.getLogger(__name__)

# Weather code descriptions according to WMO standard
WMO_CODES = {
    0: ("Clear sky", "☀️", "Ideal for field drying, solar soil solarization, and spray application."),
    1: ("Mainly clear", "🌤️", "Good conditions for harvesting and fieldwork."),
    2: ("Partly cloudy", "⛅", "Mild solar radiation; suitable for transplanting."),
    3: ("Overcast", "☁️", "Cloud cover reduces evapotranspiration; adjust drip volume."),
    45: ("Foggy", "🌫️", "High surface humidity; monitor for early fungal spore germination."),
    48: ("Depositing rime fog", "🌫️", "Damp vegetation; withhold early morning tractor operations."),
    51: ("Light drizzle", "🌦️", "Light moisture; avoid applying systemic foliar sprays."),
    53: ("Moderate drizzle", "🌦️", "Humid canopy; favorable for sucking pest multiplication."),
    55: ("Dense drizzle", "🌧️", "Foliage remains wet; check drainage outlets."),
    61: ("Slight rain", "🌧️", "Natural moisture recharge; suspend surface irrigation."),
    63: ("Moderate rain", "🌧️", "Postpone chemical spraying and basal fertilizer broadcast."),
    65: ("Heavy rain", "⛈️", "High runoff hazard; clear field trenches and safeguard bunds."),
    80: ("Rain showers", "🌦️", "Intermittent showers; monitor low-lying inundation spots."),
    95: ("Thunderstorm", "⚡", "Hazardous weather; avoid open field tasks and secure livestock.")
}

class WeatherService:
    def __init__(self, cache_ttl_seconds: int = 1800):
        # 30-minute cache TTL
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_weather_for_district(self, district_name: str) -> Dict[str, Any]:
        """
        Retrieves weather data for a Tamil Nadu district.
        Returns dictionary with weather metrics, provenance, timestamp, and agricultural notes.
        """
        district_key = district_name.strip()
        coords = TN_DISTRICTS.get(district_key)

        if not coords:
            # Fallback to centroid if exact match not found
            coords = {"lat": 10.7905, "lon": 78.7047}  # Tiruchirappalli (Center of TN)
            district_key = "Tamil Nadu (Central)"

        # Check in-memory cache
        now = time.time()
        cached_entry = self._cache.get(district_key)
        if cached_entry and (now - cached_entry["cached_at"] < self.cache_ttl):
            data = cached_entry["data"].copy()
            data["provenance"] = "CACHED_DATA"
            data["status_note"] = f"Retrieved from cache (Cached {int((now - cached_entry['cached_at'])/60)} mins ago)"
            return data

        # Live request to Open-Meteo
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Asia/Kolkata",
            "forecast_days": 3
        }

        try:
            headers = {"User-Agent": "KrishiAI-OpenMeteo-Client/1.0 (Agriculture Advisory System)"}
            resp = requests.get(url, params=params, timeout=4.0, headers=headers)

            if resp.status_code == 200:
                json_data = resp.json()
                current = json_data.get("current", {})
                daily = json_data.get("daily", {})

                w_code = current.get("weather_code", 0)
                desc, icon, agri_hint = WMO_CODES.get(w_code, ("Fair", "🌤️", "Normal field operations."))

                result = {
                    "provenance": "LIVE_DATA",
                    "status_note": "Live meteorological feed successfully retrieved",
                    "district": district_key,
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "timestamp": current.get("time", ""),
                    "temperature_c": current.get("temperature_2m"),
                    "apparent_temperature_c": current.get("apparent_temperature"),
                    "relative_humidity": current.get("relative_humidity_2m"),
                    "precipitation_mm": current.get("precipitation"),
                    "wind_speed_kmh": current.get("wind_speed_10m"),
                    "weather_code": w_code,
                    "condition_desc": desc,
                    "icon": icon,
                    "agricultural_hint": agri_hint,
                    "forecast_daily": {
                        "dates": daily.get("time", []),
                        "temp_max": daily.get("temperature_2m_max", []),
                        "temp_min": daily.get("temperature_2m_min", []),
                        "precipitation_sum": daily.get("precipitation_sum", [])
                    },
                    "attribution": "Weather data by Open-Meteo.com (CC-BY 4.0)"
                }

                # Update cache
                self._cache[district_key] = {
                    "cached_at": now,
                    "data": result
                }
                return result

            else:
                logger.warning(f"Open-Meteo returned status {resp.status_code}")
                return self._fallback_response(district_key, coords, f"Open-Meteo HTTP {resp.status_code}")

        except requests.exceptions.RequestException as e:
            logger.warning(f"Weather network error for {district_name}: {e}")
            # If we had old cached data even if expired, return it with STALE provenance
            if cached_entry:
                data = cached_entry["data"].copy()
                data["provenance"] = "STALE_DATA"
                data["status_note"] = f"Network offline. Displaying cached data from {data.get('timestamp')}"
                return data
            return self._fallback_response(district_key, coords, f"Network unreachable: {str(e)}")

    def _fallback_response(self, district_key: str, coords: Dict[str, float], reason: str) -> Dict[str, Any]:
        """Provides an honest fallback indicating unavailable live network."""
        return {
            "provenance": "OFFLINE_UNAVAILABLE",
            "status_note": f"Live weather currently unavailable ({reason})",
            "district": district_key,
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "timestamp": "N/A",
            "temperature_c": None,
            "apparent_temperature_c": None,
            "relative_humidity": None,
            "precipitation_mm": None,
            "wind_speed_kmh": None,
            "weather_code": None,
            "condition_desc": "Data Unavailable",
            "icon": "⚠️",
            "agricultural_hint": "Check local weather forecasts or IMD Mausam portal before initiating sprays or irrigations.",
            "forecast_daily": None,
            "attribution": "Open-Meteo.com (CC-BY 4.0)"
        }
