"""
Localization and Translation module for KrishiAI.
Provides bilingual key mappings for English ('en') and Tamil ('ta').
Designed to allow easy expansion to Telugu, Kannada, Hindi, etc.
"""

TRANSLATIONS = {
    "en": {
        "app_title": "KrishiAI — Hyperlocal Crop Advisory & Benefits",
        "tagline": "Empowering farmers with hyperlocal science, field planning, and verified government benefits.",
        "nav_dashboard": "🌾 Dashboard",
        "nav_fields": "🌱 My Fields",
        "nav_advisory": "📖 Crop Advisory",
        "nav_calendar": "📅 Crop Calendar",
        "nav_market": "📈 Market Intelligence",
        "nav_schemes": "🏛️ Govt Schemes & Benefits",
        "nav_impact": "📊 Impact Report",
        "nav_settings": "⚙️ Settings & Privacy",
        
        # Profile
        "profile_title": "Farmer Profile",
        "farmer_name": "Farmer Name",
        "language_pref": "Preferred Language",
        "state": "State",
        "district": "District",
        "village": "Village / Panchayat",
        "primary_crop": "Primary Crop",
        "total_land": "Total Landholding (Acres)",
        "land_arrangement": "Farming Arrangement",
        "irrigation": "Irrigation Facility",
        "season": "Current Agricultural Season",
        "soil_type": "Soil Type (Optional)",
        "woman_farmer": "Woman Farmer Headed Household",
        "save_profile": "Save Profile",
        
        # Dashboard
        "welcome": "Welcome back",
        "weather_title": "Hyperlocal Weather & Agricultural Advisory",
        "fields_overview": "My Registered Fields",
        "upcoming_tasks": "Pending Field Milestones",
        "relevant_schemes": "Eligible Government Schemes",
        
        # Provenance Tags
        "tag_live": "🟢 LIVE DATA",
        "tag_cached": "🟡 CACHED DATA",
        "tag_demo": "⚪ DEMONSTRATION DATA",
        "tag_farmer": "🔵 FARMER-ENTERED",
        "tag_calc": "🟣 CALCULATED ESTIMATE",

        # Schemes
        "scheme_status_open": "🟢 OPEN NOW",
        "scheme_status_passed": "🔴 DEADLINE PASSED",
        "scheme_status_soon": "🟡 OPENING SOON",
        "scheme_status_unverified": "⚪ STATUS NOT VERIFIED",
        "eligibility_pot": "✅ POTENTIALLY ELIGIBLE",
        "eligibility_more": "⚠️ MORE DETAILS REQUIRED",
        "eligibility_no": "❌ DOES NOT APPEAR TO MEET LISTED CRITERIA",
        "eligibility_unv": "❓ ELIGIBILITY RULES NOT VERIFIED"
    },
    "ta": {
        "app_title": "கிருஷி AI — பயிர் ஆலோசனை & அரசு திட்டங்கள்",
        "tagline": "துல்லியமான விவசாய வழிகாட்டுதல், கால அட்டவணை மற்றும் அரசு நலத்திட்டங்கள்.",
        "nav_dashboard": "🌾 முகப்பு (Dashboard)",
        "nav_fields": "🌱 என் நிலங்கள் (My Fields)",
        "nav_advisory": "📖 பயிர் ஆலோசனை (Crop Advisory)",
        "nav_calendar": "📅 பயிர் நாட்காட்டி (Calendar)",
        "nav_market": "📈 சந்தை விலை நிலவரம் (Markets)",
        "nav_schemes": "🏛️ அரசு திட்டங்கள் (Govt Schemes)",
        "nav_impact": "📊 பண்ணை அறிக்கை (Impact Report)",
        "nav_settings": "⚙️ அமைப்புகள் (Settings)",
        
        # Profile
        "profile_title": "விவசாயி விவரங்கள்",
        "farmer_name": "விவசாயி பெயர்",
        "language_pref": "விருப்பமான மொழி",
        "state": "மாநிலம்",
        "district": "மாவட்டம்",
        "village": "கிராமம் / பஞ்சாயத்து",
        "primary_crop": "முதன்மை பயிர்",
        "total_land": "மொத்த நிலப்பரப்பு (ஏக்கர்)",
        "land_arrangement": "நில உரிமை முறை",
        "irrigation": "பாசன வசதி",
        "season": "தற்போதைய சாகுபடி பருவம்",
        "soil_type": "மண் வகை (விருப்பத்தேர்வு)",
        "woman_farmer": "பெண் விவசாயி தலைமை குடும்பம்",
        "save_profile": "விவரங்களை சேமிக்கவும்",
        
        # Dashboard
        "welcome": "வணக்கம்",
        "weather_title": "உள்ளூர் வானிலை & பண்ணை ஆலோசனை",
        "fields_overview": "பதிவு செய்யப்பட்ட நிலங்கள்",
        "upcoming_tasks": "வரவிருக்கும் பண்ணை பணிகள்",
        "relevant_schemes": "பொருத்தமான அரசு நலத்திட்டங்கள்",
        
        # Provenance Tags
        "tag_live": "🟢 நேரலை தகவல்",
        "tag_cached": "🟡 சேமிக்கப்பட்ட தகவல்",
        "tag_demo": "⚪ மாதிரி தகவல்",
        "tag_farmer": "🔵 விவசாயி உள்ளிட்ட தகவல்",
        "tag_calc": "🟣 கணக்கிடப்பட்ட மதிப்பீடு",

        # Schemes
        "scheme_status_open": "🟢 விண்ணப்பிக்கலாம் (OPEN)",
        "scheme_status_passed": "🔴 காலக்கெடு முடிந்தது",
        "scheme_status_soon": "🟡 விரைவில் தொடங்கும்",
        "scheme_status_unverified": "⚪ உறுதிப்படுத்தப்படவில்லை",
        "eligibility_pot": "✅ தகுதி பெற வாய்ப்புள்ளது",
        "eligibility_more": "⚠️ கூடுதல் விவரங்கள் தேவை",
        "eligibility_no": "❌ தகுதி நிபந்தனைகள் பொருந்தவில்லை",
        "eligibility_unv": "❓ விதிகள் சரிபார்க்கப்படவில்லை"
    }
}

def t(key: str, lang: str = "en") -> str:
    """Translates a key into the chosen language, falling back to English."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
