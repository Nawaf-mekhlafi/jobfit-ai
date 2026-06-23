import streamlit as st
import plotly.graph_objects as go
import sys
import os
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.document_parser import DocumentParser
from utils.scraper import JobScraper
from utils.docx_generator import DocumentGenerator
from ai_engine.ai_agent import JobMatchAgent

st.set_page_config(
    page_title="AI Job Intelligence Engine",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_aurora_glassmorphism():
    imports = """
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    """
    
    css_rules = """
    /* Hide Streamlit Top Menu, Header, Footer, and Header Anchors */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 1. FIX: Hide Streamlit link icons next to headers */
    a.header-anchor, a.header-anchor * { display: none !important; opacity: 0 !important; visibility: hidden !important; }
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    .stApp {
        background-color: #030712 !important; 
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%), 
            radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.12) 0px, transparent 50%) !important;
        background-attachment: fixed !important;
        color: #F8FAFC !important;
    }
    
    h1, h2, h3, h4, p, span, label, li { 
        font-family: 'Plus Jakarta Sans', sans-serif !important; 
        color: #F8FAFC !important; 
    }
    
    div[data-testid="stFileUploader"], 
    div[data-testid="stTextArea"], 
    .glass-card {
        background: rgba(17, 24, 39, 0.55) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        margin-bottom: 1rem;
    }
    
    div[data-testid="stFileUploader"]:hover, 
    div[data-testid="stTextArea"]:hover,
    .glass-card:hover {
        transform: translateY(-4px) scale(1.005) !important;
        border-color: rgba(168, 85, 247, 0.4) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: transparent !important;
        border: none !important;
        color: #F8FAFC !important;
    }
    
    div[data-testid="stButton"] > button {
        width: 100%;
        background: linear-gradient(135deg, #4F46E5, #9333EA) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.5px !important;
        padding: 1rem 0 !important;
        box-shadow: 0 4px 15px rgba(147, 51, 234, 0.25) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(147, 51, 234, 0.4) !important;
        background: linear-gradient(135deg, #4338CA, #7E22CE) !important;
    }
    
    div[data-testid="stDownloadButton"] > button {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #F8FAFC !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
    }

    .fa-fw { margin-right: 8px; color: #A855F7; }
    </style>
    """
    compressed_css = css_rules.replace('\n', ' ')
    st.markdown(imports + compressed_css, unsafe_allow_html=True)

def render_gauge_chart(score: int):
    if score <= 30: bar_color = "#EF4444"
    elif score <= 70: bar_color = "#F59E0B"
    else: bar_color = "#10B981"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        number = {'font': {'size': 56, 'color': '#F8FAFC', 'family': 'Plus Jakarta Sans'}, 'suffix': "%"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 0, 'visible': False},
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': "rgba(30, 41, 59, 0.4)",
            'borderwidth': 0,
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#F8FAFC", 'family': "Plus Jakarta Sans"},
        height=250,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

def main():
    inject_aurora_glassmorphism()
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    st.markdown("<br><br><h1><i class='fa-solid fa-layer-group fa-fw'></i> The AI Job Intelligence Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; font-size: 1.1rem;'>Enterprise-Grade Candidate Analysis & ATS Optimization System</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("<h3><i class='fa-solid fa-file-pdf fa-fw'></i> 1. Candidate Profile</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Professional CV (PDF)", type=["pdf"])
        
    with col2:
        st.markdown("<h3><i class='fa-solid fa-link fa-fw'></i> 2. Target Role</h3>", unsafe_allow_html=True)
        job_input = st.text_area("Paste Job Description OR direct URL", height=130, placeholder="https://linkedin.com/jobs/... or raw text")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Initialize Semantic Analysis"):
        if uploaded_file and job_input:
            with st.spinner("Executing AI Inference..."):
                try:
                    cv_text = DocumentParser.extract_text_from_pdf(BytesIO(uploaded_file.getvalue()))
                    if job_input.startswith("http://") or job_input.startswith("https://"):
                        job_desc = JobScraper.extract_text_from_url(job_input)
                    else:
                        job_desc = job_input
                        
                    agent = JobMatchAgent()
                    results = agent.analyze_cv_against_job(cv_text, job_desc)
                    st.session_state.analysis_results = results
                    
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")
        else:
            st.warning("Please provide both a CV and a Job Description/URL.")

    if st.session_state.analysis_results:
        res = st.session_state.analysis_results
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        st.markdown("<h2><i class='fa-solid fa-chart-pie fa-fw'></i> Diagnostic Results</h2>", unsafe_allow_html=True)
        
        res_col1, res_col2 = st.columns([1, 1.5], gap="large")
        with res_col1:
            st.markdown("<div style='text-align: center; color: #94A3B8; font-weight: 600;'>Semantic Match Score</div>", unsafe_allow_html=True)
            st.plotly_chart(render_gauge_chart(res.get('match_score', 0)), use_container_width=True, config={'displayModeBar': False})
        with res_col2:
            st.markdown("<h4><i class='fa-solid fa-microchip fa-fw'></i> Overall Fit Summary</h4>", unsafe_allow_html=True)
            st.markdown(f"<div class='glass-card' style='line-height: 1.6;'>{res.get('overall_summary', 'N/A')}</div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        kw_col1, kw_col2 = st.columns(2, gap="large")
        with kw_col1:
            st.markdown("<h4><i class='fa-solid fa-check-double fa-fw' style='color:#10B981;'></i> Verified Skills</h4>", unsafe_allow_html=True)
            match_html = "".join([f"<span style='display:inline-block; background:rgba(16, 185, 129, 0.15); color:#34D399; padding:6px 14px; border-radius:20px; margin:4px; border:1px solid rgba(16, 185, 129, 0.4); font-size:0.9em; font-weight:500;'>{k}</span>" for k in res.get('matching_keywords', [])])
            st.markdown(f"<div class='glass-card'>{match_html or 'No matches found.'}</div>", unsafe_allow_html=True)
            
        with kw_col2:
            st.markdown("<h4><i class='fa-solid fa-triangle-exclamation fa-fw' style='color:#F43F5E;'></i> Identified Gaps</h4>", unsafe_allow_html=True)
            missing_html = ""
            for k in res.get('missing_keywords', []):
                skill_name = k.get('skill', str(k)) if isinstance(k, dict) else str(k)
                missing_html += f"<span style='display:inline-block; background:rgba(244, 63, 94, 0.15); color:#FB7185; padding:6px 14px; border-radius:20px; margin:4px; border:1px solid rgba(244, 63, 94, 0.4); font-size:0.9em; font-weight:500;'>{skill_name}</span>"
            st.markdown(f"<div class='glass-card'>{missing_html or 'No critical gaps.'}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        grid_col1, grid_col2 = st.columns(2, gap="large")
        with grid_col1:
            st.markdown("<h4><i class='fa-solid fa-shield-halved fa-fw'></i> ATS CV Improvements</h4>", unsafe_allow_html=True)
            ats_html = "".join([f"<li style='margin-bottom: 12px; color: #E2E8F0;'>{item}</li>" for item in res.get('ats_improvements', [])])
            st.markdown(f"<div class='glass-card'><ul style='padding-left: 20px;'>{ats_html}</ul></div>", unsafe_allow_html=True)
            
        with grid_col2:
            st.markdown("<h4><i class='fa-solid fa-pen-nib fa-fw'></i> Suggested Bullet Improvements</h4>", unsafe_allow_html=True)
            bullets_html = "".join([f"<li style='margin-bottom: 12px; color: #E2E8F0;'>{item}</li>" for item in res.get('bullet_improvements', [])])
            st.markdown(f"<div class='glass-card'><ul style='padding-left: 20px;'>{bullets_html}</ul></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        route_col1, route_col2 = st.columns(2, gap="large")
        with route_col1:
            st.markdown("<h4><i class='fa-solid fa-map-location-dot fa-fw'></i> Smart Educational Router</h4>", unsafe_allow_html=True)
            
            # 2. FIX: Prevent markdown from interpreting indented HTML as code block
            router_html = ""
            for missing in res.get('missing_keywords', []):
                if isinstance(missing, dict):
                    skill = missing.get('skill', 'Unknown Skill')
                    platform = missing.get('platform', 'Suggested Platform')
                else:
                    skill = str(missing)
                    platform = "Coursera / Udemy"
                
                # Render HTML entirely on a single logical line without leading spaces
                router_html += f"<div style='background: rgba(255,255,255,0.03); padding: 12px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #A855F7;'><strong style='color:#F8FAFC;'>{skill}</strong><br><span style='color: #94A3B8; font-size: 0.85em;'><i class='fa-solid fa-graduation-cap'></i> Recommended Platform: <span style='color:#A855F7;'>{platform}</span></span></div>"
                
            st.markdown(f"<div class='glass-card'>{router_html or 'Analysis pending...'}</div>", unsafe_allow_html=True)
            
        with route_col2:
            st.markdown("<h4><i class='fa-solid fa-arrows-turn-to-dots fa-fw'></i> Reverse Job Recommendations</h4>", unsafe_allow_html=True)
            reverse_html = "".join([f"<li style='margin-bottom: 12px; color: #E2E8F0;'><strong>{item}</strong></li>" for item in res.get('reverse_job_recommendations', [])])
            st.markdown(f"<div class='glass-card'><ul style='padding-left: 20px;'>{reverse_html}</ul></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("<h3><i class='fa-solid fa-envelope-open-text fa-fw'></i> Enterprise Cover Letter</h3>", unsafe_allow_html=True)
        
        # 3. FIX: Replace \n characters with <br> for proper HTML rendering
        cover_letter_text = res.get('cover_letter_draft', '')
        formatted_letter = cover_letter_text.replace('\n', '<br>')
        
        st.markdown(f"<div class='glass-card' style='line-height: 1.8; font-size: 1.05rem; color: #E2E8F0; padding: 2rem;'>{formatted_letter}</div>", unsafe_allow_html=True)
        
        docx_buffer = DocumentGenerator.create_cover_letter_docx(cover_letter_text)
        
        st.download_button(
            label="📥 Download as Word Document",
            data=docx_buffer,
            file_name="Enterprise_Cover_Letter.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

if __name__ == "__main__":
    main()