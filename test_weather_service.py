"""
Tests for Weather Service and Open-Meteo Integration.
"""
from src.weather_service import WeatherService

def test_weather_service_district_lookup():
    ws = WeatherService()
    res = ws.get_weather_for_district("Thanjavur")
    
    assert res is not None
    assert "provenance" in res
    assert res["district"] in ["Thanjavur", "Tamil Nadu (Central)"]
    assert "attribution" in res
    assert "Open-Meteo" in res["attribution"]

def test_weather_cache_reuse():
    ws = WeatherService(cache_ttl_seconds=300)
    # First call loads either LIVE or OFFLINE
    res1 = ws.get_weather_for_district("Coimbatore")
    
    # If first call succeeded live, second call should come from cache
    if res1["provenance"] == "LIVE_DATA":
        res2 = ws.get_weather_for_district("Coimbatore")
        assert res2["provenance"] == "CACHED_DATA"

def test_weather_invalid_district_fallback():
    ws = WeatherService()
    res = ws.get_weather_for_district("NonExistentDistrict123")
    assert res is not None
    assert "provenance" in res
