"""
Crop Calendar and Planner Service for KrishiAI.
Calculates crop growth milestones based on sowing date and Days After Sowing (DAS).
Provides milestone generation, custom reminder scheduling, and SQLite persistence.
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from src.database import (
    add_calendar_task,
    get_tasks_for_field,
    toggle_task_completion,
    delete_calendar_task
)

# Standard Days After Sowing (DAS) Milestones from TNAU / ICAR Guides
CROP_STAGE_TEMPLATES = {
    "Paddy (Rice)": [
        {"stage": "Nursery & Sowing", "das_start": 0, "das_end": 22, "task": "Seed treatment with bio-control agents and nursery bed preparation."},
        {"stage": "Transplanting", "das_start": 23, "das_end": 30, "task": "Transplant 2-3 seedlings per hill at 20x10 cm spacing. Apply basal NPK."},
        {"stage": "Active Tillering", "das_start": 31, "das_end": 50, "task": "Cono-weeder operation and 1st top dressing of Nitrogen. Practice AWD irrigation."},
        {"stage": "Panicle Initiation", "das_start": 51, "das_end": 75, "task": "Apply 2nd top dressing of N and K. Maintain 2-3 cm thin water layer."},
        {"stage": "Flowering & Grain Filling", "das_start": 76, "das_end": 95, "task": "Monitor for earhead bug and leaf folder. Spray pulse wonder or 1% DAP if needed."},
        {"stage": "Ripening & Harvest", "das_start": 96, "das_end": 120, "task": "Drain field 10 days before harvest. Harvest when 80-85% grains turn golden yellow."}
    ],
    "Cotton": [
        {"stage": "Sowing & Emergence", "das_start": 0, "das_end": 15, "task": "Dibble certified seeds with companion pulse crop. Check early seedling emergence."},
        {"stage": "Vegetative Growth", "das_start": 16, "das_end": 45, "task": "Thinning to single plant per hill, weeding, and earthing up. Basal top dress."},
        {"stage": "Square Formation", "das_start": 46, "das_end": 75, "task": "Install pheromone traps for pink bollworm. Apply 2nd split nitrogen."},
        {"stage": "Flowering & Boll Setting", "das_start": 76, "das_end": 115, "task": "Spray NAA or micronutrient mix to prevent square drop. Scout for sucking pests."},
        {"stage": "Boll Opening & Picking", "das_start": 116, "das_end": 150, "task": "First picking of mature clean bolls in morning hours. Store away from moisture."}
    ],
    "Groundnut": [
        {"stage": "Sowing & Germination", "das_start": 0, "das_end": 15, "task": "Treat seed kernels with Trichoderma. Sow on ridges or flat beds with moisture."},
        {"stage": "Vegetative & Flowering", "das_start": 16, "das_end": 35, "task": "Hand weeding and shallow inter-cultivation before flower commencement."},
        {"stage": "Pegging Stage", "das_start": 36, "das_end": 55, "task": "Apply Gypsum @ 200 kg/acre and light earthing up. Do not disturb soil after peg entry."},
        {"stage": "Pod Filling", "das_start": 56, "das_end": 85, "task": "Ensure adequate soil moisture in root zone during pod formation."},
        {"stage": "Maturity & Pulling", "das_start": 86, "das_end": 105, "task": "Check pod inner shell color (brown/black indicates maturity). Pull and dry plants."}
    ],
    "Tomato": [
        {"stage": "Nursery & Transplanting", "das_start": 0, "das_end": 25, "task": "Raise sturdy seedlings under shade net and transplant to ridges with basal manure."},
        {"stage": "Vegetative & Staking", "das_start": 26, "das_end": 45, "task": "Erect bamboo/trellis stakes. Pinch out early side suckers."},
        {"stage": "Flowering & Fruit Set", "das_start": 46, "das_end": 65, "task": "Monitor for whiteflies and leaf miner. Apply balanced potassium drip fertigation."},
        {"stage": "Fruit Harvesting", "das_start": 66, "das_end": 95, "task": "Harvest fruits at breaker or pink stage for distant markets."}
    ],
    "Banana": [
        {"stage": "Planting & Early Sprouting", "das_start": 0, "das_end": 60, "task": "Plant disease-free suckers/tissue culture plantlets with neem cake in pits."},
        {"stage": "Vegetative Pseudostem Growth", "das_start": 61, "das_end": 180, "task": "Apply monthly fertilizer splits. Desucker unwanted side shoots."},
        {"stage": "Shooting / Inflorescence", "das_start": 181, "das_end": 240, "task": "Denavel (remove male flower bud). Provide sturdy double pole propping."},
        {"stage": "Bunch Maturation & Harvest", "das_start": 241, "das_end": 330, "task": "Sleeve bunches with polypropylene covers. Harvest at 75-80% roundness."}
    ]
}

class CalendarService:
    @staticmethod
    def calculate_crop_progress(sowing_date_str: str, crop_name: str) -> Dict[str, Any]:
        """
        Determines current growth stage, days elapsed since sowing,
        and estimated completion percentage.
        """
        try:
            sowing_date = datetime.strptime(sowing_date_str, "%Y-%m-%d").date()
        except Exception:
            return {
                "days_after_sowing": 0,
                "current_stage": "Date format error",
                "estimated_progress_pct": 0,
                "note": "Invalid sowing date format"
            }

        today = date.today()
        das = (today - sowing_date).days

        if das < 0:
            return {
                "days_after_sowing": das,
                "current_stage": "Pre-Sowing / Planned",
                "estimated_progress_pct": 0,
                "note": f"Sowing planned in {abs(das)} days"
            }

        stages = CROP_STAGE_TEMPLATES.get(crop_name)
        if not stages:
            # Generic stage estimation
            return {
                "days_after_sowing": das,
                "current_stage": "Cultivation in Progress",
                "estimated_progress_pct": min(100, int((das / 120) * 100)),
                "note": "Standard 120-day growth estimate (Cultivar specific stages depend on local conditions)"
            }

        max_das = stages[-1]["das_end"]
        current_stage_name = "Harvest Completed / Post-Maturity"
        for st in stages:
            if st["das_start"] <= das <= st["das_end"]:
                current_stage_name = st["stage"]
                break

        progress_pct = min(100, max(0, int((das / max_das) * 100)))

        return {
            "days_after_sowing": das,
            "current_stage": current_stage_name,
            "estimated_progress_pct": progress_pct,
            "total_estimated_days": max_das,
            "note": "Estimated growth milestone based on TNAU/ICAR crop biology. Real duration varies by temperature and cultivar."
        }

    @staticmethod
    def generate_default_tasks_for_field(field_id: int, crop_name: str, sowing_date_str: str) -> int:
        """
        Generates and saves recommended milestone tasks into the SQLite database.
        Returns count of tasks created.
        """
        try:
            sowing_date = datetime.strptime(sowing_date_str, "%Y-%m-%d").date()
        except Exception:
            return 0

        stages = CROP_STAGE_TEMPLATES.get(crop_name)
        if not stages:
            return 0

        created_count = 0
        for st in stages:
            task_date = sowing_date + timedelta(days=st["das_start"])
            task_data = {
                "field_id": field_id,
                "crop": crop_name,
                "task_name": st["task"],
                "growth_stage": st["stage"],
                "scheduled_date": task_date.strftime("%Y-%m-%d"),
                "is_completed": 0,
                "is_custom": 0,
                "notes": f"Suggested milestone for {st['stage']} (DAS {st['das_start']}-{st['das_end']})"
            }
            add_calendar_task(task_data)
            created_count += 1

        return created_count
