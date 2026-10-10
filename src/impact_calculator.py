"""
Impact Calculator for KrishiAI.
Aggregates authentic farm metrics strictly from local SQLite records.
Strictly avoids inflated claims or speculative benefits.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from src.database import (
    get_all_fields,
    get_tasks_for_field,
    get_saved_schemes,
    get_farm_records,
    get_connection
)

class ImpactCalculator:
    @staticmethod
    def calculate_farm_summary(db_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Computes accurate summary metrics based on actual farmer records.
        """
        # 1. Fields
        fields = get_all_fields(db_path)
        field_count = len(fields)
        total_acres = sum(f.get("area_acres", 0.0) for f in fields)

        # 2. Tasks
        tasks = get_tasks_for_field(None, db_path)
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("is_completed") == 1)
        completion_pct = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

        # 3. Advisories viewed
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM advisory_views;")
        advisories_count = cursor.fetchone()[0]
        conn.close()

        # 4. Schemes saved and personal application status
        schemes = get_saved_schemes(db_path)
        schemes_saved_count = len(schemes)
        submitted_by_farmer = sum(1 for s in schemes if s.get("application_status") in ["Applied / Submitted", "Approved"])
        planned_schemes = sum(1 for s in schemes if s.get("application_status") == "Planned")

        # 5. Farm Economics (Farmer-entered records)
        records = get_farm_records(db_path)
        total_input_costs = sum(r.get("amount_inr", 0.0) for r in records if r.get("record_type") == "INPUT_COST")
        total_harvest_kg = sum(r.get("quantity_kg", 0.0) for r in records if r.get("record_type") == "HARVEST_YIELD")
        total_sales_revenue = sum(r.get("amount_inr", 0.0) for r in records if r.get("record_type") == "MARKET_SALE")
        net_cashflow = total_sales_revenue - total_input_costs if (total_sales_revenue > 0 or total_input_costs > 0) else None

        return {
            "fields_count": field_count,
            "total_acres": round(total_acres, 2),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "task_completion_rate_pct": completion_pct,
            "advisories_viewed": advisories_count,
            "schemes_saved": schemes_saved_count,
            "applications_self_reported_submitted": submitted_by_farmer,
            "applications_planned": planned_schemes,
            "total_input_costs_inr": total_input_costs,
            "total_harvest_kg": total_harvest_kg,
            "total_sales_revenue_inr": total_sales_revenue,
            "net_cashflow_inr": net_cashflow,
            "disclaimer": "All metrics are computed exclusively from your locally stored records. No hypothetical or simulated benefits are included."
        }
