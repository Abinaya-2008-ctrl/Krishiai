"""
Advisory Engine for KrishiAI.
Provides transparent, explainable agricultural advisories based on verified
ICAR, TNAU, and KVK crop production manuals.
Strictly rule-based and transparent, with scientific citations and clear limitations.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from src.config import ADVISORY_RULES_FILE

logger = logging.getLogger(__name__)

class AdvisoryEngine:
    def __init__(self, rules_file: Optional[Path] = None):
        self.rules_file = rules_file or ADVISORY_RULES_FILE
        self.rules: List[Dict[str, Any]] = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        try:
            with open(self.rules_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading advisory rules: {e}")
            return []

    def get_advisories_for_crop_and_stage(
        self,
        crop: str,
        growth_stage: Optional[str] = None,
        weather_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves matching recommendations for the specified crop, stage, and weather.
        Universal best practices applicable to all crops are also included.
        """
        matched = []
        clean_crop = crop.strip().lower() if crop else ""
        clean_stage = growth_stage.strip().lower() if growth_stage else None

        # Check weather trigger flags
        rain_trigger = False
        humidity_trigger = False
        dry_trigger = False

        if weather_conditions:
            precip = weather_conditions.get("precipitation_mm", 0)
            humidity = weather_conditions.get("relative_humidity", 0)
            if precip and precip >= 15.0:
                rain_trigger = True
            if humidity and humidity >= 80:
                humidity_trigger = True
            if precip == 0 and humidity < 50:
                dry_trigger = True

        for rule in self.rules:
            rule_crop = rule.get("crop", "").strip().lower()
            rule_stage = rule.get("growth_stage", "").strip().lower()
            weather_trig = rule.get("weather_trigger")

            # Check crop match (either exact, substring, or universal "all")
            crop_match = (
                rule_crop == "all" or
                rule_crop in clean_crop or
                clean_crop in rule_crop
            )

            if not crop_match:
                continue

            # Check growth stage match
            stage_match = True
            if clean_stage and rule_stage != "any stage":
                stage_match = (clean_stage in rule_stage or rule_stage in clean_stage)

            # Weather trigger relevance
            weather_match = True
            if weather_trig:
                if weather_trig in ["heavy_rain", "rain_forecast"] and not rain_trigger:
                    weather_match = False
                elif weather_trig in ["high_humidity", "warm_humid"] and not humidity_trigger:
                    weather_match = False
                elif weather_trig == "dry_spell" and not dry_trigger:
                    weather_match = False

            if crop_match and (stage_match or weather_match):
                matched.append(rule)

        # Ensure we always return at least universal sustainable practices if specific stage has few
        if len(matched) < 2:
            for rule in self.rules:
                if rule.get("crop") == "All" and rule not in matched:
                    matched.append(rule)

        return matched

    def get_categories(self) -> List[str]:
        """Returns distinct categories of advisories."""
        cats = set(r.get("category", "General") for r in self.rules)
        return sorted(list(cats))
