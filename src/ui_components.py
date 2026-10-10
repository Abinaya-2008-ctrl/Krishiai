"""
UI Components and Visual Design Elements for KrishiAI.
Implements the AgroBloom-inspired agricultural theme:
Emerald green gradients, modern cards, frosted glass pills, and accessible labels.
"""
import streamlit as st
from typing import Dict, Any, Optional

def inject_custom_styles():
    """Injects modern agricultural CSS styles."""
    st.markdown("""
    <style>
    /* Main Background & Typography */
    .stApp {
        background-color: #F8FAF7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Card */
    .krishi-hero {
        background: linear-gradient(135deg, #143D1A 0%, #1E5627 50%, #2E7D32 100%);
        color: #FFFFFF;
        padding: 24px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(20, 61, 26, 0.15);
    }
    .krishi-hero h1 {
        color: #FFFFFF !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
        letter-spacing: -0.5px;
    }
    .krishi-hero p {
        color: #D1E7D5 !important;
        font-size: 1.05rem !important;
        margin-bottom: 14px !important;
    }
    
    /* Badges */
    .pill-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .pill-live {
        background-color: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }
    .pill-cached {
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FCD34D;
    }
    .pill-farmer {
        background-color: #E0E7FF;
        color: #4338CA;
        border: 1px solid #C7D2FE;
    }
    .pill-demo {
        background-color: #F3F4F6;
        color: #4B5563;
        border: 1px solid #E5E7EB;
    }
    .pill-calc {
        background-color: #F3E8FF;
        color: #7E22CE;
        border: 1px solid #E9D5FF;
    }
    
    /* Eligibility Badges */
    .pill-pot-eligible {
        background-color: #DCFCE7;
        color: #166534;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        border: 1.5px solid #22C55E;
    }
    .pill-more-details {
        background-color: #FEF3C7;
        color: #92400E;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        border: 1.5px solid #F59E0B;
    }
    .pill-not-eligible {
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        border: 1.5px solid #EF4444;
    }
    
    /* Content Cards */
    .agri-card {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .agri-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Scientific Advisory Card */
    .advisory-box {
        background-color: #FFFFFF;
        border-left: 5px solid #2E7D32;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .citation-note {
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 8px;
        font-style: italic;
    }
    .disclaimer-box {
        background-color: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 0.85rem;
        color: #92400E;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def render_provenance_badge(provenance: str):
    """Renders visual provenance badges."""
    prov = (provenance or "").upper()
    if "LIVE" in prov:
        st.markdown('<span class="pill-badge pill-live">🟢 LIVE DATA</span>', unsafe_allow_html=True)
    elif "CACHED" in prov:
        st.markdown('<span class="pill-badge pill-cached">🟡 CACHED DATA</span>', unsafe_allow_html=True)
    elif "FARMER" in prov:
        st.markdown('<span class="pill-badge pill-farmer">🔵 FARMER-ENTERED</span>', unsafe_allow_html=True)
    elif "CALCULATED" in prov or "ESTIMATE" in prov:
        st.markdown('<span class="pill-badge pill-calc">🟣 CALCULATED ESTIMATE</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill-badge pill-demo">⚪ DEMO / BENCHMARK</span>', unsafe_allow_html=True)

def render_eligibility_badge(status: str):
    """Renders honest eligibility badge."""
    stat = (status or "").upper()
    if "POTENTIALLY ELIGIBLE" in stat:
        st.markdown('<span class="pill-pot-eligible">✅ POTENTIALLY ELIGIBLE</span>', unsafe_allow_html=True)
    elif "MORE DETAILS" in stat:
        st.markdown('<span class="pill-more-details">⚠️ MORE DETAILS REQUIRED</span>', unsafe_allow_html=True)
    elif "DOES NOT" in stat:
        st.markdown('<span class="pill-not-eligible">❌ DOES NOT MEET LISTED CRITERIA</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill-demo">❓ ELIGIBILITY RULES NOT VERIFIED</span>', unsafe_allow_html=True)
