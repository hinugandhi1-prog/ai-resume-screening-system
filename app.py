import streamlit as st
import sqlite3

conn = sqlite3.connect("candidates.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    score REAL
)
""")
conn.commit()

st.set_page_config(
    page_title="AI Resume Intelligence Hub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- PREMIMUM UX STYLING ----------------
st.markdown("""
<style>
/* Hide Default Streamlit Elements */
[data-testid="stSidebar"] {display: none;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Professional Dark Gradient Background */
.stApp {
    background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
    min-height: 100vh;
    font-family: 'Inter', sans-serif;
}

/* Glassmorphism Main Card */
.main-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 40px;
    padding: 80px 40px;
    margin: 80px auto;
    max-width: 1000px;
    text-align: center;
    box-shadow: 0 40px 100px rgba(0, 0, 0, 0.5);
    animation: fadeIn 1.2s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Title with Neon Glow */
.hero-title {
    font-size: 75px;
    font-weight: 900;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
    filter: drop-shadow(0 0 15px rgba(168, 85, 247, 0.3));
}

.hero-subtitle {
    font-size: 22px;
    color: #94a3b8;
    max-width: 700px;
    margin: 0 auto 50px auto;
    line-height: 1.6;
}

/* Premium Selection Cards */
.mode-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 35px 25px;
    border-radius: 25px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.mode-card:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: translateY(-15px);
    border-color: #6366f1;
    box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
}

/* Button Styling */
div.stButton > button {
    background: linear-gradient(90deg, #6366f1, #a855f7) !important;
    color: white !important;
    border: none !important;
    padding: 15px 40px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    border-radius: 15px !important;
    transition: 0.3s all !important;
    box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3) !important;
    width: 100%;
}

div.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 15px 30px rgba(168, 85, 247, 0.4) !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- MAIN HERO ----------------
st.markdown("""
<div class="main-card">
    <div class="hero-title">AI Resume Intelligence</div>
    <div class="hero-subtitle">
        Empower your hiring process with cutting-edge Semantic Vectorization and 
        Word2Vec technology for intelligent candidate-job matching.
    </div>
""", unsafe_allow_html=True)

# Session States
if "show_options" not in st.session_state:
    st.session_state.show_options = False

# Launch Button
if not st.session_state.show_options:
    c1, c2, c3 = st.columns([1, 0.8, 1])
    with c2:
        if st.button("🚀 Launch Experience"):
            st.session_state.show_options = True
            st.rerun()

# ---------------- OPTIONS SECTION ----------------
if st.session_state.show_options:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="mode-card">
            <h2 style='color: #f8fafc; font-size: 28px;'>📄 JD Screening</h2>
            <p style='color: #64748b; font-size: 16px; margin: 15px 0;'>
                Bulk analyze resumes against a specific job description to find the top 1% talent.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Screening"):
            st.session_state.mode = "jd"
            st.switch_page("pages/1_screening.py")

    with col2:
        st.markdown("""
        <div class="mode-card">
            <h2 style='color: #f8fafc; font-size: 28px;'>🔍 Best Fit Finder</h2>
            <p style='color: #64748b; font-size: 16px; margin: 15px 0;'>
                Upload a single resume to discover the most compatible role from your database.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Find Best Match"):
            st.session_state.mode = "best"
            st.switch_page("pages/2_best_match.py")

st.markdown('</div>', unsafe_allow_html=True)