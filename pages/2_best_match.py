import streamlit as st
import string
import PyPDF2
import base64
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import re

# --- Page Config ---
st.set_page_config(page_title="Resume Strategist | AI", layout="wide", initial_sidebar_state="collapsed")

# ---------------- PREMIUM DESIGN SYSTEM ----------------
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: radial-gradient(circle at 10% 20%, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #e0e0e0;
    }

    /* 🔥 HEADING STYLE */
    .main-title {
        font-size: 50px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }

    /* 🔥 FILE UPLOADER NAME COLOR FIX */
    div[data-testid="stFileUploaderFileName"] {
        color: #00f2fe !important;
        font-weight: bold !important;
    }

    /* 🔥 EXPANDER (CANDIDATE NAME) COLOR */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #00f2fe !important; /* Blue color for name */
        font-weight: bold !important;
        border-radius: 10px !important;
    }

    /* 🔥 COMPACT BOXES */
    .result-card-part {
        background: rgba(255, 255, 255, 0.05);
        padding: 10px 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid rgba(0, 242, 254, 0.2);
    }

    /* 🔥 BACK TO HOME BUTTON (DIFFERENT COLOR) */
    .stButton > button {
        background: linear-gradient(90deg, #ff8a65, #ff7043) !important; /* Coral/Orange for distinction */
        color: white !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 30px !important;
        width: auto !important;
    }

    /* VIEW JD BUTTON (YELLOW) */
    .view-btn {
        text-decoration: none !important;
        background: #ffd93d !important;
        color: #1a1a2e !important;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
conn = sqlite3.connect("candidates.db", check_same_thread=False)
cursor = conn.cursor()
def extract_phone(text):
    phones = re.findall(r'\b\d{10}\b', text)
    return phones[0] if phones else None


def extract_name(text):
    lines = text.split("\n")
    for line in lines[:5]:
        if len(line.split()) <= 3 and line.replace(" ", "").isalpha():
            return line.strip()
    return "Unknown"

def create_pdf_link(pdf_path, label):
    return f'<a href="/view_jd?pdf={pdf_path}" class="view-btn">📄 {label}</a>'

def clean_text(text):
    return " ".join(str(text).lower().translate(str.maketrans('', '', string.punctuation)).split())

def extract_text_from_pdf(file_input):
    try:
        if isinstance(file_input, str):
            with open(file_input, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "".join([p.extract_text() for p in reader.pages if p.extract_text()])
        else:
            reader = PyPDF2.PdfReader(file_input)
            return "".join([p.extract_text() for p in reader.pages if p.extract_text()])
    except: return ""
    
# ---------------- UI ----------------
st.markdown("<div class='main-title'>RESUME STRATEGIST</div>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload", type="pdf", accept_multiple_files=True, label_visibility="collapsed")

roles = [
    ("AI Engineer", "job_descriptions/AI ML _2-5 Experience_Job Description_Ebits.pdf"),
    ("Flutter Dev", "job_descriptions/Flutter developer_Intern_JD.pdf"),
    ("Product Mgr", "job_descriptions/Product Manager_Job Description (2-3 years).pdf"),
    ("Cyber Security", "job_descriptions/Cyber Security.pdf"),
    ("Healthcare", "job_descriptions/Healthcare.pdf"),
    ("Civil Eng", "job_descriptions/Civil Engineering.pdf"),
    ("Law", "job_descriptions/Law.pdf"),
    ("Content Creator", "job_descriptions/Content Creation.pdf")
]

if uploaded_files:
    jd_data = {}
    for r_name, r_path in roles:
        jd_data[r_name] = {"text": clean_text(extract_text_from_pdf(r_path)), "path": r_path}

    for file in uploaded_files:
        with st.expander(f"👤 Candidate: {file.name}", expanded=True):
            res_text = clean_text(extract_text_from_pdf(file))
            raw_text = extract_text_from_pdf(file)
            phone = extract_phone(raw_text)
            name = extract_name(raw_text)
            scores = {}

            for r_name, data in jd_data.items():
                if data["text"]:
                    vec = TfidfVectorizer()
                    v = vec.fit_transform([data["text"], res_text])
                    sc = round(cosine_similarity(v[0:1], v[1:])[0][0] * 100, 2)
                    scores[r_name] = (sc, data["path"])

            if scores:
                best_role = max(scores, key=lambda x: scores[x][0])
                best_sc, _ = scores[best_role]
                if phone:
                    cursor.execute(
                        "INSERT INTO candidates (name, phone, score, type) VALUES (?, ?, ?, ?)",
                        (name, phone, best_sc, "best_match")
                        )
                    conn.commit()
                best_sc, best_path = scores[best_role]

                # Top Match Hero
                st.markdown(f"""
                <div style="background:rgba(0, 242, 254, 0.05); border:2px solid #00f2fe; border-radius:15px; padding:20px; text-align:center; margin-bottom:15px;">
                    <div style="color:#00f2fe; font-size:14px; font-weight:bold; letter-spacing:1px;">🎯 OPTIMAL ALIGNMENT</div>
                    <div style="font-size:36px; font-weight:900; color:#fff; margin:5px 0;">{best_role}</div>
                    <div style="color:#ffd93d; font-size:20px; font-weight:bold;">{best_sc}% Match Accuracy</div>
                    <div style="margin-top:12px;">{create_pdf_link(best_path, "View Full Needs")}</div>
                </div>
                """, unsafe_allow_html=True)

                # Grid for alternatives
                c1, c2 = st.columns(2)
                sorted_res = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)

                for i, (role, (sc, path)) in enumerate(sorted_res):
                    target = c1 if i % 2 == 0 else c2
                    with target:
                        st.markdown(f"""
                        <div class="result-card-part">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-weight:700; color:#00f2fe; font-size:14px;">{role}</span>
                                <span style="color:#ffd93d; font-weight:800; font-size:14px;">{sc}%</span>
                            </div>
                            <div style="background:rgba(255,255,255,0.1); height:4px; border-radius:5px; margin:8px 0;">
                                <div style="background:#00f2fe; width:{sc}%; height:100%; border-radius:5px;"></div>
                            </div>
                            <div style="text-align:right;">{create_pdf_link(path, "View JD")}</div>
                        </div>
                        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("⬅ Back to Home Page"):
    st.switch_page("app.py")