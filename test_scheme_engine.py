"""
Tests for Scheme Engine: Eligibility, Matching, Deadlines, and Official Links.
"""
import pytest
from src.scheme_engine import SchemeEngine

@pytest.fixture
def engine():
    return SchemeEngine()

def test_schemes_loaded(engine):
    schemes = engine.get_all_schemes()
    assert len(schemes) >= 5
    for s in schemes:
        assert "scheme_id" in s
        assert "scheme_name" in s
        assert "department" in s
        assert "official_info_url" in s

def test_missing_profile_handling(engine):
    # Null profile should return MORE DETAILS REQUIRED
    sample_scheme = engine.get_all_schemes()[0]
    res = engine.evaluate_eligibility(sample_scheme, None)
    assert res["status"] == "MORE DETAILS REQUIRED"
    assert len(res["missing_details"]) > 0

def test_marginal_farmer_pm_kisan_eligibility(engine):
    profile = {
        "farmer_name": "Ramu",
        "state": "Tamil Nadu",
        "district": "Thanjavur",
        "primary_crop": "Paddy (Rice)",
        "total_land_acres": 1.5,
        "land_arrangement": "Owner-Cultivator",
        "irrigation_type": "Canal / River Water",
        "is_woman_farmer": 0
    }
    pm_kisan = engine.get_scheme_by_id("TN-SCHEME-001")
    assert pm_kisan is not None
    eval_res = engine.evaluate_eligibility(pm_kisan, profile)
    assert eval_res["status"] == "POTENTIALLY ELIGIBLE"
    assert any("Geographical criteria met" in sc for sc in eval_res["satisfied_criteria"])

def test_tenant_farmer_exclusion_on_strict_ownership_scheme(engine):
    # Tenant farmer applying for scheme requiring land ownership patta (e.g. Mechanization or PM-KISAN)
    tenant_profile = {
        "farmer_name": "Suresh",
        "state": "Tamil Nadu",
        "district": "Madurai",
        "primary_crop": "Paddy (Rice)",
        "total_land_acres": 2.0,
        "land_arrangement": "Tenant Farmer (Leased)",
        "irrigation_type": "Borewell / Tube Well",
        "is_woman_farmer": 0
    }
    pm_kisan = engine.get_scheme_by_id("TN-SCHEME-001")
    eval_res = engine.evaluate_eligibility(pm_kisan, tenant_profile)
    assert eval_res["status"] == "DOES NOT APPEAR TO MEET LISTED CRITERIA"
    assert any("Requires registered land ownership" in r for r in eval_res["matched_reasons"])

def test_land_size_ceiling_exceeded(engine):
    # Large farmer (15 acres) applying for KAVIADP (which has max 5.0 acres)
    large_profile = {
        "farmer_name": "Sundaram",
        "state": "Tamil Nadu",
        "district": "Coimbatore",
        "primary_crop": "Coconut",
        "total_land_acres": 15.0,
        "land_arrangement": "Owner-Cultivator",
        "irrigation_type": "Drip Irrigation (Micro)",
        "is_woman_farmer": 0
    }
    kaviadp = engine.get_scheme_by_id("TN-SCHEME-003")
    eval_res = engine.evaluate_eligibility(kaviadp, large_profile)
    assert eval_res["status"] == "DOES NOT APPEAR TO MEET LISTED CRITERIA"
    assert any("Landholding limit" in r for r in eval_res["matched_reasons"])

def test_district_restriction_kuruvai_package(engine):
    # Kuruvai scheme is only for Cauvery delta districts
    non_delta_profile = {
        "farmer_name": "Kumar",
        "state": "Tamil Nadu",
        "district": "Nilgiris",
        "primary_crop": "Paddy (Rice)",
        "total_land_acres": 1.0,
        "land_arrangement": "Owner-Cultivator"
    }
    kuruvai_scheme = engine.get_scheme_by_id("TN-SCHEME-007")
    eval_res = engine.evaluate_eligibility(kuruvai_scheme, non_delta_profile)
    assert eval_res["status"] == "DOES NOT APPEAR TO MEET LISTED CRITERIA"
    assert any("District restriction" in r for r in eval_res["matched_reasons"])

def test_deadline_status_parsing(engine):
    # Test ongoing
    status, note = engine.verify_deadline_status("Ongoing (Year-round enrollment)")
    assert status == "OPEN NOW"

    # Test expired date
    status, note = engine.verify_deadline_status("2020-01-01")
    assert status == "DEADLINE PASSED"

    # Test future date
    status, note = engine.verify_deadline_status("2099-12-31")
    assert status == "OPEN NOW"
    assert "remaining" in note

    # Test unannounced / invalid string
    status, note = engine.verify_deadline_status("To be announced by Collectorate")
    assert status == "STATUS NOT VERIFIED"

def test_official_domain_validation(engine):
    assert engine.is_trusted_official_url("https://pmkisan.gov.in/RegistrationFormNew.aspx") is True
    assert engine.is_trusted_official_url("https://www.tnagrisnet.tn.gov.in/esevai/") is True
    assert engine.is_trusted_official_url("https://agrimachinery.nic.in/") is True
    assert engine.is_trusted_official_url("https://fake-subsidy-claims.com/apply") is False
    assert engine.is_trusted_official_url("") is False

def test_url_reachability_safe_handling(engine):
    # Should safely report error without raising uncaught exception
    res = engine.verify_live_url_reachability("http://non-existent-government-test-url-12345.gov.in")
    assert res["reachable"] is False
    assert res["error"] is not None
