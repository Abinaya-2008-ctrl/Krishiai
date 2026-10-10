"""
Tests for KrishiAI SQLite Database Layer.
"""
import pytest
from pathlib import Path
from src.database import (
    init_db,
    save_or_update_profile,
    get_farmer_profile,
    add_field,
    get_all_fields,
    get_field_by_id,
    update_field,
    delete_field,
    add_calendar_task,
    get_tasks_for_field,
    toggle_task_completion,
    delete_calendar_task,
    save_scheme,
    get_saved_schemes,
    update_saved_scheme_status,
    remove_saved_scheme,
    add_farm_record,
    get_farm_records,
    clear_all_data
)

@pytest.fixture
def test_db(tmp_path: Path):
    db_file = tmp_path / "test_krishiai.db"
    init_db(db_file)
    return db_file

def test_farmer_profile_crud(test_db):
    # Verify initially empty
    assert get_farmer_profile(test_db) is None

    # Insert Profile
    sample_profile = {
        "farmer_name": "Murugan S",
        "preferred_language": "en",
        "state": "Tamil Nadu",
        "district": "Thanjavur",
        "village": "Papanasam",
        "primary_crop": "Paddy (Rice)",
        "total_land_acres": 2.5,
        "land_arrangement": "Owner-Cultivator",
        "irrigation_type": "Canal / River Water",
        "current_season": "Kuruvai (Jun - Sep)",
        "soil_type": "Alluvial",
        "is_woman_farmer": 0
    }
    save_or_update_profile(sample_profile, test_db)
    
    saved = get_farmer_profile(test_db)
    assert saved is not None
    assert saved["farmer_name"] == "Murugan S"
    assert saved["district"] == "Thanjavur"
    assert saved["total_land_acres"] == 2.5

    # Update Profile
    sample_profile["farmer_name"] = "Murugan Selvam"
    sample_profile["total_land_acres"] = 3.0
    save_or_update_profile(sample_profile, test_db)

    updated = get_farmer_profile(test_db)
    assert updated["farmer_name"] == "Murugan Selvam"
    assert updated["total_land_acres"] == 3.0

def test_fields_crud_and_cascade(test_db):
    field_id = add_field({
        "field_name": "North Canal Plot",
        "crop": "Paddy (Rice)",
        "variety": "CR 1009",
        "area_acres": 1.5,
        "sowing_date": "2026-08-01",
        "irrigation_type": "Canal / River Water",
        "soil_type": "Clay Loam",
        "notes": "Kuruvai crop"
    }, test_db)

    assert field_id is not None
    field = get_field_by_id(field_id, test_db)
    assert field["field_name"] == "North Canal Plot"
    assert field["area_acres"] == 1.5

    # Add task linked to field
    task_id = add_calendar_task({
        "field_id": field_id,
        "crop": "Paddy (Rice)",
        "task_name": "Weeding",
        "growth_stage": "Tillering",
        "scheduled_date": "2026-08-25"
    }, test_db)

    tasks = get_tasks_for_field(field_id, test_db)
    assert len(tasks) == 1
    assert tasks[0]["task_name"] == "Weeding"

    # Toggle task
    toggle_task_completion(task_id, True, test_db)
    updated_tasks = get_tasks_for_field(field_id, test_db)
    assert updated_tasks[0]["is_completed"] == 1

    # Delete Field (Cascade removes tasks)
    deleted = delete_field(field_id, test_db)
    assert deleted is True
    assert get_field_by_id(field_id, test_db) is None
    assert len(get_tasks_for_field(field_id, test_db)) == 0

def test_saved_schemes_and_status(test_db):
    scheme_obj = {
        "scheme_id": "TN-PMKSY-01",
        "scheme_name": "Micro Irrigation Drip Subsidy",
        "department": "Horticulture Dept",
        "application_status": "Planned",
        "documents_checklist": {"Patta": True, "Adangal": False},
        "reminder_date": "2026-11-01",
        "farmer_notes": "Application planned for Monday"
    }
    save_scheme(scheme_obj, test_db)
    
    saved_list = get_saved_schemes(test_db)
    assert len(saved_list) == 1
    assert saved_list[0]["scheme_id"] == "TN-PMKSY-01"
    assert saved_list[0]["documents_checklist"]["Patta"] is True

    # Update Status
    update_saved_scheme_status("TN-PMKSY-01", "Applied / Submitted", "Ack ID #998", {"Patta": True, "Adangal": True}, test_db)
    updated = get_saved_schemes(test_db)[0]
    assert updated["application_status"] == "Applied / Submitted"
    assert updated["farmer_notes"] == "Ack ID #998"
    assert updated["documents_checklist"]["Adangal"] is True

    # Remove Scheme
    remove_saved_scheme("TN-PMKSY-01", test_db)
    assert len(get_saved_schemes(test_db)) == 0

def test_farm_records_and_purge(test_db):
    add_farm_record({
        "field_id": None,
        "record_type": "INPUT_COST",
        "description": "Seeds",
        "amount_inr": 1200.0,
        "quantity_kg": 20.0,
        "record_date": "2026-09-01"
    }, test_db)

    records = get_farm_records(test_db)
    assert len(records) == 1
    assert records[0]["amount_inr"] == 1200.0

    # Purge
    clear_all_data(test_db)
    assert len(get_farm_records(test_db)) == 0
