"""
Configuration module for KrishiAI.
Defines constants for Tamil Nadu districts, geocodes, crop varieties,
seasons, irrigation modes, and database settings.
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "krishiai.db"
SCHEMES_FILE = DATA_DIR / "schemes.json"
ADVISORY_RULES_FILE = DATA_DIR / "advisory_rules.json"
MARKET_DATA_FILE = DATA_DIR / "sample_mandi_data.json"

# Districts of Tamil Nadu with representative coordinates for Hyperlocal Weather
TN_DISTRICTS = {
    "Ariyalur": {"lat": 11.1401, "lon": 79.0786},
    "Chengalpattu": {"lat": 12.6841, "lon": 79.9836},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558},
    "Cuddalore": {"lat": 11.7480, "lon": 79.7714},
    "Dharmapuri": {"lat": 12.1211, "lon": 78.1582},
    "Dindigul": {"lat": 10.3673, "lon": 77.9803},
    "Erode": {"lat": 11.3410, "lon": 77.7172},
    "Kallakurichi": {"lat": 11.7383, "lon": 78.9639},
    "Kancheepuram": {"lat": 12.8342, "lon": 79.7036},
    "Kanniyakumari": {"lat": 8.0883, "lon": 77.5385},
    "Karur": {"lat": 10.9601, "lon": 78.0766},
    "Krishnagiri": {"lat": 12.5186, "lon": 78.2137},
    "Madurai": {"lat": 9.9252, "lon": 78.1198},
    "Mayiladuthurai": {"lat": 11.1075, "lon": 79.6524},
    "Nagapattinam": {"lat": 10.7672, "lon": 79.8449},
    "Namakkal": {"lat": 11.2189, "lon": 78.1674},
    "Nilgiris": {"lat": 11.4102, "lon": 76.6950},
    "Perambalur": {"lat": 11.2342, "lon": 78.8821},
    "Pudukkottai": {"lat": 10.3797, "lon": 78.8208},
    "Ramanathapuram": {"lat": 9.3639, "lon": 78.8395},
    "Ranipet": {"lat": 12.9229, "lon": 79.3326},
    "Salem": {"lat": 11.6643, "lon": 78.1460},
    "Sivaganga": {"lat": 9.8433, "lon": 78.4809},
    "Tenkasi": {"lat": 8.9594, "lon": 77.3152},
    "Thanjavur": {"lat": 10.7870, "lon": 79.1378},
    "Theni": {"lat": 10.0104, "lon": 77.4768},
    "Thoothukudi": {"lat": 8.7642, "lon": 78.1348},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047},
    "Tirunelveli": {"lat": 8.7139, "lon": 77.7567},
    "Tirupathur": {"lat": 12.4925, "lon": 78.5678},
    "Tiruppur": {"lat": 11.1085, "lon": 77.3411},
    "Tiruvallur": {"lat": 13.1432, "lon": 79.9079},
    "Tiruvannamalai": {"lat": 12.2253, "lon": 79.0747},
    "Tiruvarur": {"lat": 10.7725, "lon": 79.6365},
    "Vellore": {"lat": 12.9165, "lon": 79.1325},
    "Viluppuram": {"lat": 11.9401, "lon": 79.4861},
    "Virudhunagar": {"lat": 9.5680, "lon": 77.9624}
}

# Major Crops Cultivated in Tamil Nadu and South India
CROPS_LIST = [
    "Paddy (Rice)",
    "Cotton",
    "Sugarcane",
    "Groundnut",
    "Maize",
    "Banana",
    "Black Gram (Urad)",
    "Green Gram (Moong)",
    "Coconut",
    "Turmeric",
    "Tomato",
    "Chili",
    "Millets (Ragi/Bajra)",
    "Tapioca",
    "Mango"
]

# Cropping Seasons
SEASONS = [
    "Kuruvai (Jun - Sep)",
    "Samba / Thaladi (Aug - Jan)",
    "Navarai (Dec - Mar)",
    "Sornavari (Apr - Aug)",
    "Perennial / Annual"
]

# Irrigation Types
IRRIGATION_TYPES = [
    "Canal / River Water",
    "Borewell / Tube Well",
    "Open Well",
    "Drip Irrigation (Micro)",
    "Sprinkler Irrigation",
    "Rainfed / Dryland"
]

# Land Ownership Arrangements
LAND_ARRANGEMENTS = [
    "Owner-Cultivator",
    "Tenant Farmer (Leased)",
    "Sharecropper",
    "Joint Family Holding"
]

# Farmer Categories by Land Size in Acres
# Marginal: <= 2.5 acres (1 ha)
# Small: 2.5 - 5.0 acres (1-2 ha)
# Semi-medium: 5.0 - 10.0 acres
# Medium: 10.0 - 25.0 acres
# Large: > 25.0 acres
def categorize_land_size(acres: float) -> str:
    """Classifies land size based on Indian agricultural census guidelines."""
    if acres <= 0:
        return "Unknown"
    elif acres <= 2.5:
        return "Marginal Farmer (< 2.5 acres / 1 ha)"
    elif acres <= 5.0:
        return "Small Farmer (2.5 - 5.0 acres / 1-2 ha)"
    elif acres <= 10.0:
        return "Semi-Medium Farmer (5 - 10 acres)"
    elif acres <= 25.0:
        return "Medium Farmer (10 - 25 acres)"
    else:
        return "Large Farmer (> 25 acres)"

# App Metadata
APP_NAME = "KrishiAI"
APP_SUBTITLE = "Hyperlocal Crop Advisory & Farmer Benefits System"
VERSION = "1.0.0"
AUTHOR = "Student Developer (SDG Hackathon Initiative)"
TARGET_STATE = "Tamil Nadu"
