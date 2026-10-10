"""
Tests for Advisory Engine: Rule Matching, Scientific Sources, and Weather Triggers.
"""
import pytest
from src.advisory_engine import AdvisoryEngine

@pytest.fixture
def adv_engine():
    return AdvisoryEngine()

def test_paddy_advisories_loaded(adv_engine):
    paddy_adv = adv_engine.get_advisories_for_crop_and_stage("Paddy (Rice)")
    assert len(paddy_adv) >= 3
    for a in paddy_adv:
        assert "recommendation" in a
        assert "supporting_source" in a
        assert "limitations_disclaimer" in a
        assert a["advisory_type"] == "EXPLAINABLE_RULE_BASED"

def test_growth_stage_filtering(adv_engine):
    nursery_rules = adv_engine.get_advisories_for_crop_and_stage("Paddy (Rice)", growth_stage="Nursery")
    assert any("Nursery" in r.get("growth_stage", "") for r in nursery_rules)

def test_weather_trigger_heavy_rain(adv_engine):
    # Simulated high precipitation weather event
    severe_weather = {"precipitation_mm": 45.0, "relative_humidity": 92}
    adv_list = adv_engine.get_advisories_for_crop_and_stage("All", weather_conditions=severe_weather)
    
    # Should include weather precautions for rainfall
    assert any("rain" in a.get("recommendation", "").lower() or "drainage" in a.get("recommendation", "").lower() for a in adv_list)

def test_universal_practices_included_for_rare_crop(adv_engine):
    # If a rare crop has no specific stage rules, universal practices are still provided
    adv_list = adv_engine.get_advisories_for_crop_and_stage("Rare Millets")
    assert len(adv_list) >= 2
    assert any(a.get("crop") == "All" for a in adv_list)
