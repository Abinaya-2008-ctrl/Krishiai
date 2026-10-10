"""
KrishiAI — Hyperlocal Crop Advisory & Farmer Benefits System
Streamlit Main Application
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
import json

from src.config import (
    APP_NAME, APP_SUBTITLE, VERSION, TN_DISTRICTS,
    CROPS_LIST, SEASONS, IRRIGATION_TYPES, LAND_ARRANGEMENTS,
    categorize_land_size
)
from src.database import (
    init_db, get_farmer_profile, save_or_update_profile,
    get_all_fields, add_field, update_field, delete_field,
    get_tasks_for_field, add_calendar_task, toggle_task_completion, delete_calendar_task,
    get_saved_schemes, save_scheme, update_saved_scheme_status, remove_saved_scheme,
    log_advisory_view, add_farm_record, get_farm_records, clear_all_data
)
from src.weather_service import WeatherService
from src.advisory_engine import AdvisoryEngine
from src.calendar_service import CalendarService
from src.market_service import MarketService
from src.scheme_engine import SchemeEngine
from src.impact_calculator import ImpactCalculator
from src.translations import t
from src.ui_components import (
    inject_custom_styles,
    render_provenance_badge,
    render_eligibility_badge
)

# ----------------- Page Setup -----------------
st.set_page_config(
    page_title=f"{APP_NAME} — Hyperlocal Crop Advisory",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# Initialize Engines
weather_service = WeatherService()
advisory_engine = AdvisoryEngine()
market_service = MarketService()
scheme_engine = SchemeEngine()

# Apply CSS
inject_custom_styles()

# Load Profile
profile = get_farmer_profile()
current_lang = profile.get("preferred_language", "en") if profile else "en"

# ----------------- Sidebar Navigation -----------------
with st.sidebar:
    st.markdown(f"### 🌾 **{APP_NAME}**")
    st.caption(f"v{VERSION} • {APP_SUBTITLE}")
    
    # Quick Language Toggle
    selected_lang = st.radio("Language / மொழி:", options=["en", "ta"], format_func=lambda x: "English" if x == "en" else "தமிழ் (Tamil)", index=0 if current_lang == "en" else 1, horizontal=True)
    if selected_lang != current_lang and profile:
        profile_update = profile.copy()
        profile_update["preferred_language"] = selected_lang
        save_or_update_profile(profile_update)
        st.rerun()

    st.markdown("---")
    menu = st.radio(
        "Navigation",
        [
            t("nav_dashboard", selected_lang),
            t("nav_fields", selected_lang),
            t("nav_advisory", selected_lang),
            t("nav_calendar", selected_lang),
            t("nav_market", selected_lang),
            t("nav_schemes", selected_lang),
            t("nav_impact", selected_lang),
            t("nav_settings", selected_lang)
        ]
    )
    
    st.markdown("---")
    if profile:
        st.markdown(f"**👤 Farmer:** {profile.get('farmer_name')}")
        st.markdown(f"**📍 District:** {profile.get('district')}")
        st.markdown(f"**🌾 Crop:** {profile.get('primary_crop')}")
        st.markdown(f"**📐 Land:** {profile.get('total_land_acres')} Acres")
        st.caption(categorize_land_size(profile.get('total_land_acres', 0)))
    else:
        st.info("👋 Welcome! Please complete your Farmer Profile in Settings or Onboarding.")

# ----------------- Hero Banner -----------------
def render_header(title: str, subtitle: str):
    st.markdown(f"""
    <div class="krishi-hero">
        <h1>{title}</h1>
        <p>{subtitle}</p>
        <span class="pill-badge pill-live">Hyperlocal Advisory</span>
        <span class="pill-badge pill-cached">Tamil Nadu & Central Schemes</span>
        <span class="pill-badge pill-farmer">Explainable AI</span>
    </div>
    """, unsafe_allow_html=True)


# =========================================================================
# 1. DASHBOARD
# =========================================================================
if menu == t("nav_dashboard", selected_lang):
    farmer_name = profile.get("farmer_name", "Farmer") if profile else "Farmer"
    render_header(
        f"{t('welcome', selected_lang)}, {farmer_name}!",
        "Hyperlocal weather, field calendar milestones, verified schemes, and advisory recommendations at a glance."
    )

    if not profile:
        st.warning("⚠️ You have not set up your Farmer Profile yet. Go to **Settings & Profile** to personalize your advisories and scheme matching.")

    district_name = profile.get("district", "Thanjavur") if profile else "Thanjavur"
    weather = weather_service.get_weather_for_district(district_name)

    # Top Row: Weather & Farm Quick Stats
    col_w, col_s = st.columns([1.4, 1])

    with col_w:
        st.subheader("🌦️ Hyperlocal Weather & Advisory")
        with st.container(border=True):
            prov = weather.get("provenance", "OFFLINE_UNAVAILABLE")
            render_provenance_badge(prov)
            st.caption(f"Location: **{weather.get('district')}** | Updated: {weather.get('timestamp')}")
            
            w_c1, w_c2, w_c3, w_c4 = st.columns(4)
            w_c1.metric("Temperature", f"{weather.get('temperature_c', '--')} °C")
            w_c2.metric("Humidity", f"{weather.get('relative_humidity', '--')} %")
            w_c3.metric("Rainfall", f"{weather.get('precipitation_mm', 0)} mm")
            w_c4.metric("Wind Speed", f"{weather.get('wind_speed_kmh', '--')} km/h")
            
            st.info(f"{weather.get('icon', '🌾')} **Condition:** {weather.get('condition_desc')}\n\n**Agricultural Action Hint:** {weather.get('agricultural_hint')}")
            st.caption(weather.get("attribution", "Open-Meteo"))

    with col_s:
        st.subheader("📊 Farm At-a-Glance")
        with st.container(border=True):
            summary = ImpactCalculator.calculate_farm_summary()
            st.metric("Registered Fields", f"{summary['fields_count']} ({summary['total_acres']} Acres)")
            st.metric("Task Completion Rate", f"{summary['task_completion_rate_pct']}% ({summary['completed_tasks']}/{summary['total_tasks']} tasks)")
            st.metric("Saved Govt Schemes", f"{summary['schemes_saved']} Schemes")
            render_provenance_badge("CALCULATED ESTIMATE")

    st.markdown("---")

    # Second Row: Upcoming Tasks & Matched Schemes
    col_t, col_sc = st.columns(2)

    with col_t:
        st.subheader("📅 Upcoming Field Milestones")
        tasks = get_tasks_for_field(None)
        pending_tasks = [t for t in tasks if t.get("is_completed") == 0]

        if pending_tasks:
            for task in pending_tasks[:4]:
                with st.container(border=True):
                    tc1, tc2 = st.columns([3, 1])
                    tc1.markdown(f"**{task.get('crop')}** — {task.get('task_name')}")
                    tc1.caption(f"Due: {task.get('scheduled_date')} | Stage: {task.get('growth_stage')}")
                    if tc2.button("Done ✔", key=f"dash_task_{task['id']}"):
                        toggle_task_completion(task['id'], True)
                        st.rerun()
        else:
            st.success("No pending tasks! All scheduled milestones are up to date.")

    with col_sc:
        st.subheader("🏛️ High-Priority Government Schemes")
        matched = scheme_engine.match_schemes_for_farmer(profile)
        eligible_schemes = [s for s in matched if s["evaluation"]["status"] == "POTENTIALLY ELIGIBLE"]

        if eligible_schemes:
            for sc in eligible_schemes[:3]:
                with st.container(border=True):
                    st.markdown(f"**{sc.get('scheme_name')}**")
                    st.caption(f"{sc.get('department')} • Benefit: {sc.get('subsidy_details')}")
                    render_eligibility_badge(sc["evaluation"]["status"])
                    st.write(sc.get("benefit_description"))
        else:
            st.info("Complete your profile to see personalized matching schemes.")


# =========================================================================
# 2. MY FIELDS MODULE
# =========================================================================
elif menu == t("nav_fields", selected_lang):
    render_header(
        t("nav_fields", selected_lang),
        "Register your land parcels, track crop growth milestones, and receive parcel-specific advisories."
    )

    tab_view, tab_add = st.tabs(["🌾 Saved Fields", "➕ Register New Field"])

    with tab_add:
        st.subheader("Add a New Agricultural Field")
        with st.form("add_field_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                f_name = st.text_input("Field Name / Nickname*", placeholder="e.g. Riverbank North Field, Well Plot")
                f_crop = st.selectbox("Crop Cultivated*", CROPS_LIST)
                f_variety = st.text_input("Crop Variety / Hybrid (Optional)", placeholder="e.g. ADT-45, MCU-5, Grand Naine")
                f_acres = st.number_input("Area in Acres* (Supports fractional acres)", min_value=0.05, max_value=500.0, value=1.0, step=0.25)
            
            with f_col2:
                f_sowing = st.date_input("Sowing / Planting Date*", value=date.today())
                f_irrigation = st.selectbox("Irrigation Type*", IRRIGATION_TYPES)
                f_soil = st.selectbox("Soil Type (Optional)", ["Clay Loam", "Sandy Loam", "Red Soil", "Black Cotton Soil", "Alluvial", "Laterite", "Other"])
                f_notes = st.text_area("Field Notes (Optional)", placeholder="e.g. Certified seeds purchased from local AEC; drip lines installed.")
            
            auto_plan = st.checkbox("Auto-generate suggested ICAR/TNAU growth milestone tasks for this field", value=True)
            submit_field = st.form_submit_button("🌱 Save Field to Database")

            if submit_field:
                if not f_name.strip():
                    st.error("Please enter a field name.")
                else:
                    field_data = {
                        "field_name": f_name.strip(),
                        "crop": f_crop,
                        "variety": f_variety.strip(),
                        "area_acres": float(f_acres),
                        "sowing_date": f_sowing.strftime("%Y-%m-%d"),
                        "irrigation_type": f_irrigation,
                        "soil_type": f_soil,
                        "notes": f_notes.strip()
                    }
                    new_id = add_field(field_data)
                    if auto_plan:
                        CalendarService.generate_default_tasks_for_field(new_id, f_crop, field_data["sowing_date"])
                    st.success(f"Field '{f_name}' registered successfully in SQLite database!")
                    st.rerun()

    with tab_view:
        fields = get_all_fields()
        if not fields:
            st.info("No fields registered yet. Use the 'Register New Field' tab above to add your first plot.")
        else:
            st.markdown(f"**Total Registered Fields:** {len(fields)}")
            for f in fields:
                with st.container(border=True):
                    fc1, fc2, fc3 = st.columns([2.5, 1.5, 1])
                    
                    with fc1:
                        st.markdown(f"### 🌿 {f['field_name']} ({f['crop']})")
                        if f['variety']:
                            st.caption(f"Variety: **{f['variety']}**")
                        st.markdown(f"**Area:** {f['area_acres']} Acres | **Irrigation:** {f['irrigation_type']} | **Soil:** {f['soil_type'] or 'Unspecified'}")
                        if f['notes']:
                            st.caption(f"Notes: {f['notes']}")
                    
                    with fc2:
                        progress = CalendarService.calculate_crop_progress(f['sowing_date'], f['crop'])
                        st.markdown(f"**Sown on:** {f['sowing_date']}")
                        st.markdown(f"**Stage:** {progress['current_stage']}")
                        st.progress(progress['estimated_progress_pct'] / 100)
                        st.caption(f"DAS: {progress['days_after_sowing']} days | {progress['estimated_progress_pct']}% timeline")
                    
                    with fc3:
                        render_provenance_badge("FARMER-ENTERED")
                        if st.button("🗑️ Delete", key=f"del_field_{f['id']}"):
                            delete_field(f['id'])
                            st.warning(f"Deleted field {f['field_name']}")
                            st.rerun()


# =========================================================================
# 3. CROP ADVISORY MODULE
# =========================================================================
elif menu == t("nav_advisory", selected_lang):
    render_header(
        t("nav_advisory", selected_lang),
        "Transparent, explainable crop recommendations from verified ICAR, TNAU, and KVK scientific guidelines."
    )

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sel_crop = st.selectbox("Select Crop", ["All Crops"] + CROPS_LIST, index=0)
    with col_f2:
        categories = ["All Categories"] + advisory_engine.get_categories()
        sel_cat = st.selectbox("Advisory Category", categories)

    crop_filter = None if sel_crop == "All Crops" else sel_crop
    
    # Get current weather conditions for triggers
    current_district = profile.get("district", "Thanjavur") if profile else "Thanjavur"
    w_data = weather_service.get_weather_for_district(current_district)

    advisories = advisory_engine.get_advisories_for_crop_and_stage(
        crop=crop_filter or "",
        growth_stage=None,
        weather_conditions=w_data
    )

    if sel_cat != "All Categories":
        advisories = [a for a in advisories if a.get("category") == sel_cat]

    st.markdown(f"**Found {len(advisories)} relevant scientific recommendations:**")

    for adv in advisories:
        with st.container(border=True):
            st.markdown(f"#### 📌 {adv.get('category')} — {adv.get('crop')} ({adv.get('growth_stage')})")
            st.markdown(f"**Recommendation:** {adv.get('recommendation')}")
            st.markdown(f"💡 **Why this is relevant:** {adv.get('relevance_reason')}")
            
            st.caption(f"🏛️ **Scientific Source:** {adv.get('supporting_source')} | Verified: {adv.get('last_verified_date')}")
            
            # Limitations & Disclaimers
            st.markdown(f"""
            <div class="disclaimer-box">
                ⚠️ <b>Limitations:</b> {adv.get('limitations_disclaimer')}
            </div>
            """, unsafe_allow_html=True)
            
            # Log view for impact tracking
            log_advisory_view(adv.get("advisory_id"), adv.get("crop"), adv.get("category"))


# =========================================================================
# 4. CROP CALENDAR & PLANNER
# =========================================================================
elif menu == t("nav_calendar", selected_lang):
    render_header(
        t("nav_calendar", selected_lang),
        "Manage field operations, growth milestones, and custom farm reminders in persistent SQLite storage."
    )

    fields = get_all_fields()
    if not fields:
        st.warning("Please register at least one field under 'My Fields' to view calendar timelines.")
    else:
        field_names = {f["id"]: f"{f['field_name']} ({f['crop']})" for f in fields}
        selected_field_id = st.selectbox("Select Field", options=list(field_names.keys()), format_func=lambda x: field_names[x])
        
        selected_field = next(f for f in fields if f["id"] == selected_field_id)
        progress = CalendarService.calculate_crop_progress(selected_field["sowing_date"], selected_field["crop"])

        # Field Status Summary
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Current Stage", progress["current_stage"])
            c2.metric("Days After Sowing (DAS)", f"{progress['days_after_sowing']} days")
            c3.metric("Growth Progress", f"{progress['estimated_progress_pct']}%")
            st.progress(progress['estimated_progress_pct'] / 100)
            st.caption(progress["note"])

        st.markdown("---")

        tab_tasks, tab_add_task = st.tabs(["📋 Milestone Checklist", "➕ Add Custom Reminder"])

        with tab_tasks:
            tasks = get_tasks_for_field(selected_field_id)
            if not tasks:
                st.info("No milestone tasks currently logged for this field.")
                if st.button("Generate Recommended ICAR/TNAU Milestones"):
                    CalendarService.generate_default_tasks_for_field(selected_field_id, selected_field["crop"], selected_field["sowing_date"])
                    st.rerun()
            else:
                for tsk in tasks:
                    with st.container(border=True):
                        col_chk, col_det, col_del = st.columns([0.6, 4, 0.6])
                        
                        is_done = tsk["is_completed"] == 1
                        new_state = col_chk.checkbox("", value=is_done, key=f"task_check_{tsk['id']}")
                        if new_state != is_done:
                            toggle_task_completion(tsk["id"], new_state)
                            st.rerun()

                        with col_det:
                            task_title = f"~~{tsk['task_name']}~~" if is_done else f"**{tsk['task_name']}**"
                            st.markdown(task_title)
                            st.caption(f"Stage: {tsk['growth_stage']} | Target Date: {tsk['scheduled_date']} | {'Custom Task' if tsk['is_custom'] else 'Standard Milestone'}")
                            if tsk["notes"]:
                                st.caption(f"Notes: {tsk['notes']}")

                        if col_del.button("❌", key=f"task_del_{tsk['id']}"):
                            delete_calendar_task(tsk["id"])
                            st.rerun()

        with tab_add_task:
            st.subheader("Add Custom Reminder for this Field")
            with st.form("custom_task_form", clear_on_submit=True):
                t_name = st.text_input("Task / Activity Name*", placeholder="e.g. Schedule tractor cultivator; Apply micronutrient zinc")
                t_stage = st.text_input("Growth Stage", value=progress["current_stage"])
                t_date = st.date_input("Target Date*", value=date.today())
                t_notes = st.text_area("Notes", placeholder="e.g. Contact driver Selvam; Purchase from primary agro service")
                sub_task = st.form_submit_button("Add Task to Calendar")

                if sub_task:
                    if not t_name.strip():
                        st.error("Please enter a task name.")
                    else:
                        add_calendar_task({
                            "field_id": selected_field_id,
                            "crop": selected_field["crop"],
                            "task_name": t_name.strip(),
                            "growth_stage": t_stage.strip(),
                            "scheduled_date": t_date.strftime("%Y-%m-%d"),
                            "is_completed": 0,
                            "is_custom": 1,
                            "notes": t_notes.strip()
                        })
                        st.success("Custom reminder added!")
                        st.rerun()


# =========================================================================
# 5. MARKET INTELLIGENCE
# =========================================================================
elif menu == t("nav_market", selected_lang):
    render_header(
        t("nav_market", selected_lang),
        "Transparent market prices from APMC Regulated Markets and farmer sales logs. No fabricated numbers."
    )

    tab_mandi, tab_my_sales = st.tabs(["🏛️ Mandi & APMC Benchmarks", "💰 My Sales Log"])

    with tab_mandi:
        sel_market_crop = st.selectbox("Filter by Crop", ["All Crops"] + CROPS_LIST)
        crop_arg = None if sel_market_crop == "All Crops" else sel_market_crop
        prices = market_service.get_prices_for_crop(crop_arg)

        st.info("ℹ️ Market prices fluctuate daily based on arrivals, moisture content, and auction bids. Refer to local Regulated Market Committee or Agmarknet.gov.in for live auction figures.")

        for p in prices:
            with st.container(border=True):
                mc1, mc2, mc3 = st.columns([2.5, 1.5, 1])
                with mc1:
                    st.markdown(f"### {p.get('crop')} — {p.get('variety')}")
                    st.markdown(f"📍 **Market:** {p.get('market_name')} ({p.get('district')})")
                    st.caption(f"Source: {p.get('source_name')} | Date: {p.get('data_date')}")
                    st.caption(f"Note: {p.get('disclaimer')}")

                with mc2:
                    st.metric("Modal Price", f"₹{p.get('modal_price_inr'):,} / {p.get('unit')}")
                    st.caption(f"Range: ₹{p.get('min_price_inr')} - ₹{p.get('max_price_inr')}")

                with mc3:
                    render_provenance_badge(p.get("data_provenance", "DEMONSTRATION_BENCHMARK"))
                    st.link_button("Official Agmarknet ↗", p.get("official_portal_url", "https://agmarknet.gov.in/"))

    with tab_my_sales:
        st.subheader("Record Verified Sale of Farm Produce")
        with st.form("sale_entry_form", clear_on_submit=True):
            sc1, sc2 = st.columns(2)
            with sc1:
                sale_crop = st.selectbox("Crop Sold*", CROPS_LIST)
                sale_market = st.text_input("Market / Trader Name*", placeholder="e.g. Thanjavur Regulated Market or Local Commission Agent")
                sale_date_val = st.date_input("Date of Sale*", value=date.today())
            with sc2:
                sale_qty_qtl = st.number_input("Quantity in Quintals (100 kg)*", min_value=0.1, value=10.0, step=0.5)
                sale_rate = st.number_input("Price Received per Quintal (₹)*", min_value=100.0, value=2300.0, step=50.0)
            
            sub_sale = st.form_submit_button("Record Sale in Farm Economics")
            if sub_sale:
                market_service.record_farmer_sale(
                    field_id=None,
                    crop=sale_crop,
                    price_per_quintal=sale_rate,
                    quantity_quintals=sale_qty_qtl,
                    sale_date=sale_date_val.strftime("%Y-%m-%d"),
                    market_name=sale_market.strip()
                )
                st.success("Sale transaction recorded in your local Farm Records database!")
                st.rerun()

        # Existing Sales
        sales = market_service.get_farmer_sales()
        if sales:
            st.markdown("#### Your Historical Recorded Sales")
            sales_df = pd.DataFrame(sales)[["record_date", "description", "quantity_kg", "amount_inr"]]
            sales_df.columns = ["Date", "Description", "Weight (kg)", "Total Revenue (₹)"]
            st.dataframe(sales_df, use_container_width=True)


# =========================================================================
# 6. GOVERNMENT SCHEMES & FARMER BENEFITS (CORE MODULE)
# =========================================================================
elif menu == t("nav_schemes", selected_lang):
    render_header(
        t("nav_schemes", selected_lang),
        "Transparent scheme matching, honest eligibility evaluations, deadline verifications, and verified official government portals."
    )

    tab_discover, tab_saved = st.tabs(["🏛️ Discover Schemes", "📌 Saved & Tracked Schemes"])

    with tab_discover:
        all_matched = scheme_engine.match_schemes_for_farmer(profile)

        # Filters
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            status_filter = st.selectbox("Filter by Eligibility", ["All Statuses", "Potentially Eligible Only", "More Details Required"])
        with f_col2:
            cat_list = ["All Categories"] + list(set(s.get("category") for s in all_matched))
            cat_filter = st.selectbox("Filter by Category", cat_list)

        filtered = all_matched
        if status_filter == "Potentially Eligible Only":
            filtered = [s for s in filtered if s["evaluation"]["status"] == "POTENTIALLY ELIGIBLE"]
        elif status_filter == "More Details Required":
            filtered = [s for s in filtered if s["evaluation"]["status"] == "MORE DETAILS REQUIRED"]

        if cat_filter != "All Categories":
            filtered = [s for s in filtered if s.get("category") == cat_filter]

        st.markdown(f"**Showing {len(filtered)} government schemes:**")

        for sc in filtered:
            with st.container(border=True):
                head_col1, head_col2 = st.columns([3, 1])
                with head_col1:
                    st.markdown(f"### {sc.get('scheme_name')}")
                    st.caption(f"🏛️ **Department:** {sc.get('department')} | **Category:** {sc.get('category')}")
                with head_col2:
                    render_eligibility_badge(sc["evaluation"]["status"])

                st.markdown(f"**Benefit:** {sc.get('benefit_description')}")
                st.markdown(f"**Subsidy / Financial Terms:** `{sc.get('subsidy_details')}`")

                # Honest Eligibility Breakdown
                eval_res = sc["evaluation"]
                with st.expander("🔍 Detailed Eligibility & Criteria Analysis", expanded=False):
                    st.markdown("**Matched Profile Attributes:**")
                    for mr in eval_res.get("matched_reasons", []):
                        st.markdown(f"- {mr}")
                    
                    if eval_res.get("missing_details"):
                        st.markdown("**Missing Farmer Information to Confirm:**")
                        for md in eval_res.get("missing_details", []):
                            st.markdown(f"- ⚠️ {md}")

                    st.markdown("**Official Departmental Conditions:**")
                    for oc in eval_res.get("official_conditions", []):
                        st.caption(f"• {oc}")

                # Required Documents & Steps
                with st.expander("📄 Required Documents & Application Steps", expanded=False):
                    st.markdown("**Required Documents:**")
                    for doc in sc.get("required_documents", []):
                        st.markdown(f"- 📋 {doc}")
                    
                    st.markdown("**Application Steps:**")
                    for step in sc.get("application_steps", []):
                        st.markdown(f"- {step}")

                # Deadline and Official Portals
                st.markdown("---")
                d_col1, d_col2 = st.columns([2, 1.5])
                
                with d_col1:
                    dl_status, dl_note = scheme_engine.verify_deadline_status(sc.get("application_deadline", ""))
                    st.markdown(f"**Application Deadline:** {sc.get('application_deadline')} ({dl_note})")
                    st.caption(f"Last checked timestamp: {sc.get('last_checked_timestamp')} | Verified Date: {sc.get('status_verified_date')}")

                with d_col2:
                    is_verified_apply = sc.get("is_apply_url_verified", False)
                    apply_url = sc.get("official_apply_url")
                    info_url = sc.get("official_info_url")

                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if is_verified_apply and apply_url:
                            st.link_button("Apply on Official Portal ↗", apply_url)
                        else:
                            st.button("Link Not Verified", disabled=True)

                    with btn_c2:
                        if st.button("📌 Save Scheme", key=f"save_sc_{sc['scheme_id']}"):
                            save_scheme({
                                "scheme_id": sc["scheme_id"],
                                "scheme_name": sc["scheme_name"],
                                "department": sc["department"],
                                "application_status": "Planned",
                                "documents_checklist": {doc: False for doc in sc.get("required_documents", [])},
                                "farmer_notes": ""
                            })
                            st.success("Scheme saved to your personal tracker!")
                            st.rerun()

    with tab_saved:
        saved_list = get_saved_schemes()
        if not saved_list:
            st.info("You haven't saved any schemes yet. Browse the 'Discover Schemes' tab and tap 'Save Scheme' to track deadlines and personal checklist progress.")
        else:
            st.markdown(f"### You have saved {len(saved_list)} schemes for personal tracking")
            for item in saved_list:
                with st.container(border=True):
                    sc_col1, sc_col2 = st.columns([3, 1])
                    with sc_col1:
                        st.markdown(f"#### 📌 {item.get('scheme_name')}")
                        st.caption(f"Department: {item.get('department')} | Saved: {item.get('saved_at')[:10]}")
                    
                    with sc_col2:
                        if st.button("🗑️ Remove", key=f"rem_sc_{item['scheme_id']}"):
                            remove_saved_scheme(item["scheme_id"])
                            st.rerun()

                    # Personal Status Tracking Form
                    with st.form(f"track_form_{item['scheme_id']}"):
                        status_options = ["Planned", "Applied / Submitted", "Awaiting Verification", "Approved", "Rejected"]
                        curr_idx = status_options.index(item.get("application_status", "Planned")) if item.get("application_status") in status_options else 0
                        new_status = st.selectbox("Your Personal Application Status*", status_options, index=curr_idx)
                        notes_val = st.text_area("Personal Notes / Application Reference No.", value=item.get("farmer_notes", ""), placeholder="e.g. Submitted at AEC centre on Tuesday; Reference ack no: TN-2026-9812")
                        
                        st.markdown("**Documents Readiness Checklist:**")
                        doc_dict = item.get("documents_checklist", {})
                        updated_docs = {}
                        for doc_name, checked in doc_dict.items():
                            updated_docs[doc_name] = st.checkbox(doc_name, value=bool(checked), key=f"chk_{item['scheme_id']}_{doc_name}")

                        save_track = st.form_submit_button("Update Progress")
                        if save_track:
                            update_saved_scheme_status(item["scheme_id"], new_status, notes_val, updated_docs)
                            st.success("Progress updated!")
                            st.rerun()


# =========================================================================
# 7. IMPACT REPORT
# =========================================================================
elif menu == t("nav_impact", selected_lang):
    render_header(
        t("nav_impact", selected_lang),
        "Farm performance and digital activity records derived strictly from your verified local SQLite records."
    )

    summary = ImpactCalculator.calculate_farm_summary()

    st.markdown("### 📊 Personal Farm Performance Overview")
    st.info("ℹ️ " + summary["disclaimer"])

    # Metric Cards Row 1
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fields Cultivated", f"{summary['fields_count']} plots", f"{summary['total_acres']} Total Acres")
    m2.metric("Task Completion", f"{summary['task_completion_rate_pct']}%", f"{summary['completed_tasks']} of {summary['total_tasks']} tasks")
    m3.metric("Advisories Consulted", f"{summary['advisories_viewed']} reads")
    m4.metric("Schemes Tracked", f"{summary['schemes_saved']} Saved", f"{summary['applications_self_reported_submitted']} Submitted")

    st.markdown("---")

    # Financial / Economics Summary Row
    st.subheader("💵 Farm Economics (Farmer-Entered Transactions)")
    ec1, ec2, ec3 = st.columns(3)
    ec1.metric("Recorded Input Expenses", f"₹{summary['total_input_costs_inr']:,.2f}")
    ec2.metric("Recorded Crop Sales Revenue", f"₹{summary['total_sales_revenue_inr']:,.2f}")
    
    net = summary["net_cashflow_inr"]
    net_display = f"₹{net:,.2f}" if net is not None else "No data entered"
    ec3.metric("Net Operating Cashflow", net_display)

    # Input Cost Form
    with st.expander("➕ Record Farm Input Expense (Seeds, Fertilizer, Labour, Fuel)"):
        with st.form("input_cost_form", clear_on_submit=True):
            exp_desc = st.text_input("Expense Description*", placeholder="e.g. Certified paddy seeds ADT-45 (30 kg)")
            exp_amount = st.number_input("Amount Paid (₹)*", min_value=1.0, value=1500.0, step=50.0)
            exp_date = st.date_input("Date Paid*", value=date.today())
            sub_exp = st.form_submit_button("Record Expense")
            if sub_exp:
                add_farm_record({
                    "field_id": None,
                    "record_type": "INPUT_COST",
                    "description": exp_desc.strip(),
                    "amount_inr": exp_amount,
                    "quantity_kg": 0.0,
                    "record_date": exp_date.strftime("%Y-%m-%d")
                })
                st.success("Expense recorded!")
                st.rerun()

    # Records Log
    records = get_farm_records()
    if records:
        st.markdown("#### Transaction Log")
        rec_df = pd.DataFrame(records)[["record_date", "record_type", "description", "amount_inr"]]
        rec_df.columns = ["Date", "Type", "Description", "Amount (₹)"]
        st.dataframe(rec_df, use_container_width=True)


# =========================================================================
# 8. SETTINGS & PROFILE
# =========================================================================
elif menu == t("nav_settings", selected_lang):
    render_header(
        t("nav_settings", selected_lang),
        "Manage your farmer profile, localization preferences, export records, or purge local data."
    )

    tab_prof, tab_data, tab_about = st.tabs(["👤 Farmer Profile", "💾 Data & Privacy", "ℹ️ About KrishiAI"])

    with tab_prof:
        st.subheader("Edit Farmer Profile")
        with st.form("profile_form"):
            p1, p2 = st.columns(2)
            with p1:
                p_name = st.text_input("Farmer Name*", value=profile.get("farmer_name", "") if profile else "Karthik Raja")
                p_state = st.selectbox("State*", ["Tamil Nadu"])
                district_names = list(TN_DISTRICTS.keys())
                curr_dist_idx = district_names.index(profile.get("district", "Thanjavur")) if profile and profile.get("district") in district_names else 25 # Thanjavur default
                p_district = st.selectbox("District*", district_names, index=curr_dist_idx)
                p_village = st.text_input("Village / Revenue Panchayat", value=profile.get("village", "") if profile else "Ammapettai")
                p_crop = st.selectbox("Primary Crop*", CROPS_LIST, index=CROPS_LIST.index(profile.get("primary_crop", "Paddy (Rice)")) if profile and profile.get("primary_crop") in CROPS_LIST else 0)

            with p2:
                p_land = st.number_input("Total Landholding in Acres*", min_value=0.1, max_value=500.0, value=float(profile.get("total_land_acres", 2.0)) if profile else 2.0, step=0.25)
                st.caption(f"Census Classification: **{categorize_land_size(p_land)}**")
                
                curr_arr_idx = LAND_ARRANGEMENTS.index(profile.get("land_arrangement", "Owner-Cultivator")) if profile and profile.get("land_arrangement") in LAND_ARRANGEMENTS else 0
                p_arr = st.selectbox("Land Holding Arrangement*", LAND_ARRANGEMENTS, index=curr_arr_idx)
                
                curr_irr_idx = IRRIGATION_TYPES.index(profile.get("irrigation_type", "Canal / River Water")) if profile and profile.get("irrigation_type") in IRRIGATION_TYPES else 0
                p_irr = st.selectbox("Irrigation Type*", IRRIGATION_TYPES, index=curr_irr_idx)
                
                curr_sea_idx = SEASONS.index(profile.get("current_season", "Samba / Thaladi (Aug - Jan)")) if profile and profile.get("current_season") in SEASONS else 1
                p_sea = st.selectbox("Current Agricultural Season*", SEASONS, index=curr_sea_idx)

                p_soil = st.selectbox("Soil Type", ["Clay Loam", "Sandy Loam", "Red Soil", "Black Cotton Soil", "Alluvial", "Other"], index=0)
                p_woman = st.checkbox("Woman Farmer Headed Household (For targeted scheme quotas)", value=bool(profile.get("is_woman_farmer", 0)) if profile else False)

            save_prof = st.form_submit_button("💾 Save Farmer Profile")
            if save_prof:
                if not p_name.strip():
                    st.error("Please enter farmer name.")
                else:
                    save_or_update_profile({
                        "farmer_name": p_name.strip(),
                        "preferred_language": selected_lang,
                        "state": p_state,
                        "district": p_district,
                        "village": p_village.strip(),
                        "primary_crop": p_crop,
                        "total_land_acres": float(p_land),
                        "land_arrangement": p_arr,
                        "irrigation_type": p_irr,
                        "current_season": p_sea,
                        "soil_type": p_soil,
                        "is_woman_farmer": 1 if p_woman else 0
                    })
                    st.success("Farmer profile updated successfully in SQLite database!")
                    st.rerun()

    with tab_data:
        st.subheader("Data Export & Privacy Controls")
        st.markdown("""
        - **Local-First Architecture:** All your personal records, fields, and calendar milestones are saved directly on your local device in SQLite (`krishiai.db`).
        - **No Sensitive Identifiers Required:** KrishiAI never stores or requires your Aadhaar number, bank passwords, or payment credentials.
        """)

        st.markdown("#### 📥 Export Data")
        fields_all = get_all_fields()
        if fields_all:
            csv_data = pd.DataFrame(fields_all).to_csv(index=False)
            st.download_button(
                label="Export Registered Fields to CSV",
                data=csv_data,
                file_name="krishiai_fields.csv",
                mime="text/csv"
            )

        st.markdown("---")
        st.markdown("#### 🗑️ Purge Local Data")
        st.warning("This action permanently removes all registered fields, calendar tasks, farm records, and saved schemes from your local SQLite database.")
        if st.button("Delete All Data Permanently", type="primary"):
            clear_all_data()
            st.success("All local data has been erased.")
            st.rerun()

    with tab_about:
        st.subheader(f"About {APP_NAME} (v{VERSION})")
        st.markdown("""
        **KrishiAI — Hyperlocal Crop Advisory & Farmer Benefits System** is an open-source, student-engineered agricultural intelligence platform developed for the SDG Hackathon initiative.
        
        **Key Architectural Highlights:**
        - **Rule-Based Explainable Advisory Engine:** Cites genuine ICAR, TNAU, and KVK production guidelines.
        - **Government Schemes Discovery & Verification:** Matches Central and Tamil Nadu government schemes against farmer profiles with honest eligibility statuses and official portal links.
        - **Hyperlocal Agromet Forecasts:** Powered by Open-Meteo with caching, provenance tagging, and WMO agricultural hints.
        - **Crop Calendar & Planner:** Tracks Days After Sowing (DAS) milestones with custom reminders.
        - **SQLite Persistence:** Zero cloud lock-in; lightweight local database.
        
        **Contact & Mentor Attribution:**
        - Student Developer Project (CSE Dept)
        - Target Geography: Tamil Nadu, India
        """)
