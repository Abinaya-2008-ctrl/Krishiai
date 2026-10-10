"""
Tests for Crop Calendar Service and DAS Progression.
"""
from datetime import date, timedelta
from src.calendar_service import CalendarService

def test_crop_progress_past_sowing():
    # Sown 40 days ago
    past_date = (date.today() - timedelta(days=40)).strftime("%Y-%m-%d")
    progress = CalendarService.calculate_crop_progress(past_date, "Paddy (Rice)")
    
    assert progress["days_after_sowing"] == 40
    assert progress["current_stage"] == "Active Tillering"
    assert progress["estimated_progress_pct"] > 0
    assert "estimate" in progress["note"].lower()

def test_crop_progress_future_sowing():
    future_date = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    progress = CalendarService.calculate_crop_progress(future_date, "Cotton")
    
    assert progress["days_after_sowing"] < 0
    assert "Pre-Sowing" in progress["current_stage"]
    assert progress["estimated_progress_pct"] == 0

def test_invalid_date_format():
    progress = CalendarService.calculate_crop_progress("invalid-date", "Paddy (Rice)")
    assert progress["estimated_progress_pct"] == 0
