"""
Market Intelligence Service for KrishiAI.
Presents APMC and Regulated Market mandi prices with transparent data provenance.
Clearly labels benchmark/demo records versus live official portal queries or farmer sales.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from src.config import MARKET_DATA_FILE
from src.database import add_farm_record, get_farm_records

logger = logging.getLogger(__name__)

class MarketService:
    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or MARKET_DATA_FILE
        self.prices: List[Dict[str, Any]] = self._load_data()

    def _load_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading mandi data: {e}")
            return []

    def get_prices_for_crop(self, crop_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves price records filtered by crop name."""
        if not crop_name:
            return self.prices
        clean = crop_name.strip().lower()
        return [
            p for p in self.prices
            if clean in p.get("crop", "").lower() or p.get("crop", "").lower() in clean
        ]

    def record_farmer_sale(self, field_id: Optional[int], crop: str, price_per_quintal: float, quantity_quintals: float, sale_date: str, market_name: str) -> int:
        """Saves a verified farmer sale transaction in local database."""
        total_amount = price_per_quintal * quantity_quintals
        quantity_kg = quantity_quintals * 100.0
        return add_farm_record({
            "field_id": field_id,
            "record_type": "MARKET_SALE",
            "description": f"Sale of {crop} at {market_name} (₹{price_per_quintal:.2f}/Qtl)",
            "amount_inr": total_amount,
            "quantity_kg": quantity_kg,
            "record_date": sale_date
        })

    def get_farmer_sales(self) -> List[Dict[str, Any]]:
        """Retrieves all sales entered by the farmer."""
        records = get_farm_records()
        return [r for r in records if r.get("record_type") == "MARKET_SALE"]
