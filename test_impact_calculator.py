"""
Tests for Impact Calculator: Farm Summary and Honest Calculations.
"""
from pathlib import Path
from src.database import (
    init_db, add_field, add_calendar_task,
    toggle_task_completion, save_scheme,
    update_saved_scheme_status, add_farm_record
)
from src.impact_calculator import ImpactCalculator

def test_impact_calculator_empty_db(tmp_path: Path):
    db_file = tmp_path / "empty.db"
    init_db(db_file)
    summary = ImpactCalculator.calculate_farm_summary(db_file)

    assert summary["fields_count"] == 0
    assert summary["total_acres"] == 0.0
    assert summary["total_tasks"] == 0
    assert summary["task_completion_rate_pct"] == 0
    assert summary["schemes_saved"] == 0
    assert summary["net_cashflow_inr"] is None

def test_impact_calculator_with_records(tmp_path: Path):
    db_file = tmp_path / "farm.db"
    init_db(db_file)

    # 1. Add fields
    add_field({
        "field_name": "Field A",
        "crop": "Paddy (Rice)",
        "variety": "ADT-45",
        "area_acres": 2.5,
        "sowing_date": "2026-08-01",
        "irrigation_type": "Canal",
        "soil_type": "Clay",
        "notes": ""
    }, db_file)

    # 2. Add tasks (1 completed, 1 pending)
    t1 = add_calendar_task({
        "field_id": 1,
        "crop": "Paddy (Rice)",
        "task_name": "Nursery",
        "growth_stage": "Nursery",
        "scheduled_date": "2026-08-05"
    }, db_file)
    add_calendar_task({
        "field_id": 1,
        "crop": "Paddy (Rice)",
        "task_name": "Tillering top-dress",
        "growth_stage": "Tillering",
        "scheduled_date": "2026-09-01"
    }, db_file)
    toggle_task_completion(t1, True, db_file)

    # 3. Add scheme and mark as submitted
    save_scheme({
        "scheme_id": "PM-KISAN",
        "scheme_name": "PM-KISAN",
        "department": "Agriculture"
    }, db_file)
    update_saved_scheme_status("PM-KISAN", "Applied / Submitted", "Ack 123", {}, db_file)

    # 4. Add farm expense & sale
    add_farm_record({
        "field_id": 1,
        "record_type": "INPUT_COST",
        "description": "Seeds",
        "amount_inr": 2000.0,
        "quantity_kg": 50.0,
        "record_date": "2026-08-01"
    }, db_file)
    add_farm_record({
        "field_id": 1,
        "record_type": "MARKET_SALE",
        "description": "Harvest sale",
        "amount_inr": 15000.0,
        "quantity_kg": 600.0,
        "record_date": "2026-10-01"
    }, db_file)

    summary = ImpactCalculator.calculate_farm_summary(db_file)
    assert summary["fields_count"] == 1
    assert summary["total_acres"] == 2.5
    assert summary["total_tasks"] == 2
    assert summary["completed_tasks"] == 1
    assert summary["task_completion_rate_pct"] == 50
    assert summary["schemes_saved"] == 1
    assert summary["applications_self_reported_submitted"] == 1
    assert summary["total_input_costs_inr"] == 2000.0
    assert summary["total_sales_revenue_inr"] == 15000.0
    assert summary["net_cashflow_inr"] == 13000.0
