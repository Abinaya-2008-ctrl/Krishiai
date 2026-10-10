"""
Scheme Matching & Eligibility Verification Engine for KrishiAI.
Evaluates farmer profile against Central and Tamil Nadu government schemes.
Provides honest eligibility analysis, application deadline statuses, and
verified official portal links.
"""
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
import requests

from src.config import SCHEMES_FILE

logger = logging.getLogger(__name__)

# Trusted official domains in India
OFFICIAL_DOMAINS = [
    "gov.in",
    "nic.in",
    "tn.gov.in",
    "tnagrisnet.tn.gov.in",
    "tangedco.gov.in",
    "tnebnet.org",
    "tnocd.net",
    "myscheme.gov.in",
    "pmkisan.gov.in",
    "pmfby.gov.in",
    "agrimachinery.nic.in"
]

class SchemeEngine:
    def __init__(self, data_file: Optional[str] = None):
        self.data_file = data_file or str(SCHEMES_FILE)
        self.schemes: List[Dict[str, Any]] = self._load_schemes()

    def _load_schemes(self) -> List[Dict[str, Any]]:
        """Loads official scheme definitions from JSON repository."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schemes file: {e}")
            return []

    def get_all_schemes(self) -> List[Dict[str, Any]]:
        return self.schemes

    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        for s in self.schemes:
            if s.get("scheme_id") == scheme_id:
                return s
        return None

    def is_trusted_official_url(self, url: str) -> bool:
        """Verifies if the URL domain belongs to recognized government portals."""
        if not url:
            return False
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return any(domain == trusted or domain.endswith("." + trusted) for trusted in OFFICIAL_DOMAINS)
        except Exception:
            return False

    def verify_live_url_reachability(self, url: str, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Attempts a safe HEAD or GET check on the official URL.
        Returns status, response code, and latency or network error.
        Does not crash on timeout or offline state.
        """
        if not url:
            return {"reachable": False, "status_code": None, "error": "URL is empty"}
        try:
            headers = {"User-Agent": "KrishiAI-Advisory-Verifier/1.0 (Agriculture Student Project)"}
            resp = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            if resp.status_code in [200, 301, 302, 307, 308]:
                return {"reachable": True, "status_code": resp.status_code, "error": None}
            # Fallback to GET with stream to avoid large downloads
            resp = requests.get(url, timeout=timeout, headers=headers, stream=True)
            return {"reachable": resp.status_code == 200, "status_code": resp.status_code, "error": None}
        except requests.exceptions.RequestException as e:
            return {"reachable": False, "status_code": None, "error": str(e)}

    def evaluate_eligibility(self, scheme: Dict[str, Any], profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates a farmer's profile against scheme requirements.
        Returns:
            - status: 'POTENTIALLY ELIGIBLE' | 'MORE DETAILS REQUIRED' |
                      'DOES NOT APPEAR TO MEET LISTED CRITERIA' | 'ELIGIBILITY RULES NOT VERIFIED'
            - matched_reasons: List[str]
            - satisfied_criteria: List[str]
            - missing_details: List[str]
            - official_conditions: List[str]
        """
        if not profile:
            return {
                "status": "MORE DETAILS REQUIRED",
                "matched_reasons": ["Complete farmer profile to evaluate eligibility."],
                "satisfied_criteria": [],
                "missing_details": ["Farmer district, land size, crop, and tenancy details are required."],
                "official_conditions": ["Final eligibility is decided exclusively by the issuing government department."]
            }

        matched_reasons = []
        satisfied_criteria = []
        missing_details = []
        disqualifications = []

        # 1. Location / District Check
        state = profile.get("state", "Tamil Nadu")
        district = profile.get("district", "").strip()
        eligible_districts = scheme.get("eligible_districts", ["All"])

        if "All" in eligible_districts or district in eligible_districts:
            matched_reasons.append(f"Location match: Applicable to your district ({district or state}).")
            satisfied_criteria.append("Geographical criteria met.")
        else:
            disqualifications.append(f"District restriction: Only available in {', '.join(eligible_districts)} (your profile: {district}).")

        # 2. Crop Cultivation Check
        crop = profile.get("primary_crop", "").strip()
        eligible_crops = scheme.get("eligible_crops", ["All"])

        if "All" in eligible_crops or crop in eligible_crops:
            if "All" in eligible_crops:
                matched_reasons.append("Universal coverage: Open across all major crop types.")
            else:
                matched_reasons.append(f"Crop match: Specifically targets {crop} cultivation.")
            satisfied_criteria.append("Crop suitability criteria met.")
        else:
            disqualifications.append(f"Crop restriction: Applies to {', '.join(eligible_crops)} (your profile: {crop}).")

        # 3. Land Size & Tenancy Check
        land_criteria = scheme.get("land_criteria", {})
        total_acres = profile.get("total_land_acres")
        max_acres = land_criteria.get("max_acres")
        tenant_allowed = land_criteria.get("tenant_allowed", True)
        land_arrangement = profile.get("land_arrangement", "")

        is_tenant = "tenant" in land_arrangement.lower() or "lease" in land_arrangement.lower() or "sharecropper" in land_arrangement.lower()

        if total_acres is None:
            missing_details.append("Exact landholding size in acres.")
        elif max_acres is not None and total_acres > max_acres:
            disqualifications.append(f"Landholding limit: Scheme requires maximum {max_acres} acres (your entered holding: {total_acres:.2f} acres).")
        else:
            if max_acres is not None:
                satisfied_criteria.append(f"Land size condition met ({total_acres:.2f} acres <= {max_acres} acres limit).")
            else:
                satisfied_criteria.append("No upper ceiling on landholding size.")

        # Tenancy check
        if is_tenant and not tenant_allowed:
            disqualifications.append("Requires registered land ownership (Patta holder). Tenant/leased farmers are excluded by current guidelines.")
        elif is_tenant and tenant_allowed:
            satisfied_criteria.append("Tenant/leased farming permitted with valid Adangal or lease agreement.")
            matched_reasons.append("Supports leased/tenant farming arrangement.")

        # 4. Small / Marginal Category Specifics
        category_criteria = scheme.get("category_criteria", {})
        if category_criteria.get("small_marginal_only", False):
            if total_acres is not None and total_acres <= 5.0:
                satisfied_criteria.append(f"Small/Marginal classification satisfied ({total_acres:.2f} acres <= 5 acres).")
                matched_reasons.append("Special priority/subsidy for Small & Marginal farmers.")
            elif total_acres is not None and total_acres > 5.0:
                disqualifications.append(f"Requires Small/Marginal status (<= 5 acres). Your holding is {total_acres:.2f} acres.")

        if category_criteria.get("women_only", False):
            if profile.get("is_woman_farmer", 0) == 1:
                satisfied_criteria.append("Reserved women farmer benefit criteria satisfied.")
            else:
                disqualifications.append("Exclusively reserved for women farmers.")

        # Missing documentation / details warnings
        if not profile.get("village"):
            missing_details.append("Specific village name or Revenue Village boundary.")
        if not profile.get("soil_type"):
            missing_details.append("Soil test record for input-based subsidies.")

        # Determine Final Honest Status
        if disqualifications:
            status = "DOES NOT APPEAR TO MEET LISTED CRITERIA"
            matched_reasons.extend(disqualifications)
        elif missing_details and len(satisfied_criteria) < 2:
            status = "MORE DETAILS REQUIRED"
        elif scheme.get("data_type") == "DEMO_DATA":
            status = "ELIGIBILITY RULES NOT VERIFIED"
        else:
            status = "POTENTIALLY ELIGIBLE"

        official_conditions = [
            "Official physical verification of Land Chitta/Adangal by the local Village Administrative Officer (VAO) is required.",
            "Funds and equipment quotas are subject to budget sanctions by the respective District Collectorate.",
            "Submitting through KrishiAI does NOT constitute government submission. You must apply directly on the official portal."
        ]

        return {
            "status": status,
            "matched_reasons": matched_reasons,
            "satisfied_criteria": satisfied_criteria,
            "missing_details": missing_details,
            "official_conditions": official_conditions
        }

    def match_schemes_for_farmer(self, profile: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters and sorts schemes according to eligibility and relevance.
        Returns list of schemes with enriched evaluation records.
        """
        results = []
        for s in self.schemes:
            eval_res = self.evaluate_eligibility(s, profile)
            enriched = {
                **s,
                "evaluation": eval_res
            }
            results.append(enriched)

        # Sort order: POTENTIALLY ELIGIBLE first, then MORE DETAILS REQUIRED, then others
        def sort_priority(item):
            stat = item["evaluation"]["status"]
            if stat == "POTENTIALLY ELIGIBLE":
                return 0
            if stat == "MORE DETAILS REQUIRED":
                return 1
            if stat == "DOES NOT APPEAR TO MEET LISTED CRITERIA":
                return 2
            return 3

        results.sort(key=sort_priority)
        return results

    def verify_deadline_status(self, deadline_str: str) -> Tuple[str, str]:
        """
        Parses date strings to check if deadline has passed or is ongoing.
        Returns (status_label, explanation).
        """
        if not deadline_str or "ongoing" in deadline_str.lower() or "year-round" in deadline_str.lower():
            return "OPEN NOW", "Continuous / Year-round enrollment"
        
        try:
            target_date = datetime.strptime(deadline_str.strip(), "%Y-%m-%d").date()
            today = date.today()
            if target_date < today:
                return "DEADLINE PASSED", f"Application period concluded on {deadline_str}"
            else:
                days_left = (target_date - today).days
                return "OPEN NOW", f"{days_left} days remaining until deadline ({deadline_str})"
        except ValueError:
            return "STATUS NOT VERIFIED", f"Custom deadline note: {deadline_str}"
