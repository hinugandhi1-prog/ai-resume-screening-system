import streamlit as st
import base64
import string
import PyPDF2
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import smtplib
import sqlite3
import re
from email.mime.text import MIMEText

# --- Page Config ---
st.set_page_config(page_title="AI Resume Intelligence", layout="wide")

# ---------------- SESSION STATE ----------------
conn = sqlite3.connect("candidates.db", check_same_thread=False)
cursor = conn.cursor()
if "page" not in st.session_state:
    st.session_state.page = "main"
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "email_sent" not in st.session_state:
    st.session_state.email_sent = {}

# ---------------- ANIMATED DYNAMIC STYLING ----------------
st.markdown("""
<style>
/* Smooth Color Changing Background */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #0f3460);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
    color: white;
}

[data-testid="stSidebar"] {display:none;}
header, footer {visibility:hidden;}

.main-title {
    font-size: 55px; font-weight: 900; text-align: center;
    background: linear-gradient(90deg, #00f2fe, #4facfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 30px;
}

/* Drag & Drop - High Visibility Glow */
[data-testid="stFileUploadDropzone"] {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 2px dashed #00f2fe !important;
    border-radius: 15px !important;
    padding: 20px !important;
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 10px;
}
.stTabs [data-baseweb="tab"] p {
    font-size: 22px !important; font-weight: 900 !important; color: #00f2fe !important;
}

/* RESULT CONTAINER - Full Width & Extra Vertical Spacing */
.result-container {
    background: rgba(255, 255, 255, 0.08); 
    padding: 30px; 
    border-radius: 20px;
    margin-top: 40px; /* Space from top element */
    margin-bottom: 50px; /* High space between candidate names */
    border-left: 12px solid #6c5ce7;
    width: 100%;
    box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.4);
}

.candidate-name-text {
    font-size: 28px; font-weight: 900; color: #00f2fe;
}

/* Custom Buttons */
div.stButton > button {
    height: 45px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%) !important;
    color: white !important;
    border: none;
    transition: 0.3s ease;
}

div.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 5px 15px rgba(108, 92, 231, 0.4);
}

/* Footer Back Button */
.footer-container {
    margin-top: 100px;
    text-align: center;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def extract_phone(text):
    phones = re.findall(r'\b\d{10}\b', text)
    return phones[0] if phones else None

def extract_name(text):
    lines = text.split("\n")
    for line in lines[:5]:
        if len(line.split()) <= 3 and line.replace(" ", "").isalpha():
            return line.strip()
    return "Unknown"

def clean_text(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return " ".join(text.split())

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() for page in reader.pages if page.extract_text()])

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="750px" style="border-radius:15px; border: 2px solid #00f2fe;"></iframe>', unsafe_allow_html=True)

def send_email(name, score):
    sender = "hinugandhi1@gmail.com"
    password = "rqmx yfpm gqot flbm"
    msg_body = f"""
🎉 Congratulations!

Dear Candidate,

We are pleased to inform you that your resume has been successfully evaluated and you have achieved a strong match score of {score}% for the applied role.

✅ Status: Eligible for further consideration  
📊 Match Score: {score}%

Your profile demonstrates alignment with the job requirements and shows promising potential.

🚀 Next Steps:
- Prepare for technical interview
- Strengthen your domain knowledge
- Review key concepts related to the role

We appreciate your interest and wish you the best for the upcoming stages.

Best Regards,  
AI Resume Screening System
"""
    msg = MIMEText(msg_body)
    msg["Subject"] ="🎉 Resume Shortlisted - AI Screening Result"
    msg["From"], msg["To"] = sender, sender
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# ---------------- REPORT PAGE ----------------

def report_page():
    data = st.session_state.report_data
    score = data['score']
    st.markdown(f"<h1 style='text-align:center;'>👤 {data['name']}</h1>", unsafe_allow_html=True)
    
    col_chart, col_info = st.columns([0.7, 1.3])
    with col_chart:
        fig, ax = plt.subplots(figsize=(2.5, 2.5))
        fig.patch.set_facecolor('none')
        ax.pie([score, 100-score], colors=['#2ecc71', '#34495e'], startangle=90)
        ax.text(0, 0, f"{score}%", ha='center', va='center', fontsize=22, fontweight='bold', color='white')
        st.pyplot(fig)

    with col_info:
        st.markdown("<h2 style='color:#00f2fe;'>🔍 Analysis Summary</h2>", unsafe_allow_html=True)
        summary = "Exceptional Candidate" if score >= 80 else "Strong Match" if score >= 60 else "Potential Candidate"
        st.markdown(f"### {summary}")
        st.markdown("### ✅ Matched Skills")
        st.write(", ".join(list(data["matched_words"])[:10]).upper())

    st.write("---")
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"
        st.rerun()

# ---------------- JOB SECTION ----------------

def job_section(job_title, jd_path):
    st.markdown(f"<h2 style='color:#ffd93d;'>💼 Current Opening: {job_title}</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1]) 
    with c1:
        if st.button(f"📄 View Job Description", key=f"v_{job_title}"):
            show_pdf(jd_path)
    with c2:
        up = st.file_uploader(f"📤 Upload Candidate Resumes", type="pdf", accept_multiple_files=True, key=f"u_{job_title}")
        
    if up:
        jd_text = clean_text(extract_text_from_pdf(open(jd_path, "rb")))
        jd_words = set(jd_text.split())

        for f in up:
            res_text = clean_text(extract_text_from_pdf(f))
            raw_text = extract_text_from_pdf(f)
            name = extract_name(raw_text)
            phone = extract_phone(raw_text)
            vec = TfidfVectorizer()
            v = vec.fit_transform([jd_text, res_text])
            score = round(cosine_similarity(v[0:1], v[1:])[0][0] * 100, 2)

            if phone:
                cursor.execute(
                    "INSERT INTO candidates (name, phone, score,type) VALUES (?, ?, ?,?)",
                    (name, phone, score,"screening")
                    )
                conn.commit()

            # High Spacing Container
            st.markdown(f"""
            <div class='result-container'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <span class='candidate-name-text'>👤 {f.name}</span>
                    <span style='font-size: 28px; font-weight:900; color: #ffd93d;'>{score}% Match</span>
                </div>
                <div style='margin-top: 15px;'>
                    <span style='font-size: 18px; color: {"#2ecc71" if score >= 40 else "#ff4b4b"}; font-weight: bold;'>
                        {"✅ QUALIFIED FOR ROUND 1" if score >= 40 else "⚠️ BELOW THRESHOLD"}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if score >= 40:   # 👈 IMPORTANT CONDITION
                if f.name not in st.session_state.email_sent:
                    st.session_state.email_sent[f.name] = send_email(f.name, score)
                    st.success(f"📧 Notification successfully dispatched to {f.name}")
                else:
                    st.warning(f"❌ {f.name} not qualified → No email sent")
                
                st.success(f"📧 Email sent successfully to {f.name}")
                if st.button(f"📊 Deep Dive Analysis: {f.name}", key=f"btn_{f.name}"):
                    st.session_state.report_data = {
                        "name": f.name, "score": score,
                        "matched_words": jd_words.intersection(set(res_text.split()))
                        }
                    st.session_state.page = "report"
                    st.rerun()

# ---------------- MAIN ----------------

if st.session_state.page == "main":
    st.markdown("<h1 class='main-title'>🌟 AI RESUME SCREENING HUB</h1>", unsafe_allow_html=True)

    roles = [
        ("🧪 AI Engineer", "job_descriptions/AI ML _2-5 Experience_Job Description_Ebits.pdf"),
        ("🛠️ Flutter Dev", "job_descriptions/Flutter developer_Intern_JD.pdf"),
        ("📈 Product Mgr", "job_descriptions/Product Manager_Job Description (2-3 years).pdf"),
        ("🛡️ Cyber Security", "job_descriptions/Cyber Security.pdf"),
        ("🏥 Healthcare", "job_descriptions/Healthcare.pdf"),
        ("🏗️ Civil Eng", "job_descriptions/Civil Engineering.pdf"),
        ("⚖️ Law Associate", "job_descriptions/Law.pdf"),
        ("🎨 Content Creator", "job_descriptions/Content Creation.pdf")
    ]

    tabs = st.tabs([r[0] for r in roles])
    for i, tab in enumerate(tabs):
        with tab:
            job_section(roles[i][0].split(' ', 1)[1], roles[i][1])
    
    # 🔙 BACK TO HOME PAGE AT THE VERY BOTTOM
    st.markdown("<div class='footer-container'>", unsafe_allow_html=True)
    if st.button("⬅ Back to Home Page (Main App)"):
        st.switch_page("app.py")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    report_page()