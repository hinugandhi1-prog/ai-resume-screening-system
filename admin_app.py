import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admin Dashboard", layout="wide")

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_logout_screen" not in st.session_state:
    st.session_state.show_logout_screen = False

# --- CSS FOR UI (COLORS KEPT SAME) ---
st.markdown("""
<style>
    .stApp { background-color: #cbd5e0; }
    section[data-testid="stSidebar"] {
        display: """ + ("block" if st.session_state.logged_in and not st.session_state.show_logout_screen else "none") + """ !important;
    }
    .stButton > button {
        width: 130px !important; border-radius: 20px !important;
        background-color: #4834d4 !important; color: white !important;
        margin: 0 auto; display: block; border: none; font-weight: bold;
    }
    .metric-card {
        padding: 25px; border-radius: 15px; color: white;
        text-align: center; box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .header-box {
        background: #4834d4; color: white; padding: 10px;
        border-radius: 8px; font-weight: bold; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- 1. LOGOUT SCREEN ----------------
if st.session_state.show_logout_screen:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    height: 100vh; width: 100vw; position: fixed; top: 0; left: 0; 
                    display: flex; align-items: center; justify-content: center; z-index: 9999;">
            <div style="background: white; padding: 60px; border-radius: 30px; 
                        text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.3); width: 450px;">
                <div style="font-size: 70px; margin-bottom: 20px;">✅</div>
                <h1 style="color: #4834d4; font-size: 32px;">Logged Out</h1>
                <p style="color: #2d3436; font-size: 18px;">Your session has been securely closed.</p>
                <form action="/" target="_self">
                    <button style="background: #4834d4; color: white; border: none; padding: 12px 35px; border-radius: 25px; cursor: pointer; font-weight: bold;">Login Again 🔄</button>
                </form>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------- 2. LOGIN PAGE ----------------
if not st.session_state.logged_in:
    st.write("<br><br><br><br><br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h2 style='text-align: center; color: #2c3e50;'>Admin Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username", label_visibility="collapsed", placeholder="Username")
        p = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Password")
        if st.button("Login"):
            if u == "admin" and p == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# ---------------- 3. DASHBOARD ----------------
conn = sqlite3.connect("candidates.db", check_same_thread=False)
cursor = conn.cursor()

# Sidebar
st.sidebar.markdown("<h2 style='text-align:center;'>🚀 Admin Panel</h2>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", ["📄 Screening Data", "🔍 Best Match Data"])
if st.sidebar.button("Logout"):
    st.session_state.show_logout_screen = True
    st.rerun()

# Fetch Data
query = "SELECT * FROM candidates WHERE type='screening'" if page == "📄 Screening Data" else "SELECT * FROM candidates WHERE type='best_match'"
df = pd.read_sql_query(query, conn)

st.markdown(f"<h1>{page} Overview</h1>", unsafe_allow_html=True)

# Metrics (Original Colors)
if not df.empty:
    m1, m2, m3 = st.columns(3)
    short = df[df["score"] >= 40].shape[0]
    with m1: st.markdown(f"<div class='metric-card' style='background:#0984e3'><p>Total</p><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with m2: st.markdown(f"<div class='metric-card' style='background:#00b894'><p>Avg Score</p><h2>{round(df['score'].mean(), 1)}%</h2></div>", unsafe_allow_html=True)
    with m3: st.markdown(f"<div class='metric-card' style='background:#6c5ce7'><p>Shortlisted</p><h2>{short}</h2></div>", unsafe_allow_html=True)

st.divider()

# --- CSV DOWNLOAD BUTTON ---
st.subheader("📋 Candidate Records")
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"{page.lower().replace(' ', '_')}_export.csv",
        mime='text/csv',
    )

# Table Rendering (Scores and Actions Kept)
h1, h2, h3, h4, h5 = st.columns([0.5, 3, 1, 2, 1])
h1.markdown("<div class='header-box'>#</div>", unsafe_allow_html=True)
h2.markdown("<div class='header-box'>Candidate Name</div>", unsafe_allow_html=True)
h3.markdown("<div class='header-box'>Score</div>", unsafe_allow_html=True)
h4.markdown("<div class='header-box'>Status</div>", unsafe_allow_html=True)
h5.markdown("<div class='header-box'>Action</div>", unsafe_allow_html=True)

for i, row in df.iterrows():
    r1, r2, r3, r4, r5 = st.columns([0.5, 3, 1, 2, 1])
    r1.write(f"**{i+1}**")
    r2.write(row["name"])
    r3.write(f"**{row['score']}%**")
    status, color = ("Qualified", "#27ae60") if row['score'] >= 40 else ("Review", "#c0392b")
    r4.markdown(f"<p style='color:{color}; font-weight:bold; text-align:center;'>{status}</p>", unsafe_allow_html=True)
    if r5.button("🗑️", key=f"del_{row['id']}"):
        cursor.execute("DELETE FROM candidates WHERE id=?", (row["id"],))
        conn.commit()
        st.rerun()

st.divider()

# Charts (Original Colors + No White Box)
if not df.empty:
    c1, c2 = st.columns(2)
    with c1:
        top_3 = df.groupby('name', as_index=False)['score'].max().sort_values(by='score', ascending=False).head(3)
        fig_bar = px.bar(top_3, x='name', y='score', text='score', title="Top 3 Candidates", 
                         color='name', color_discrete_sequence=px.colors.qualitative.Bold)
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        fig_pie = px.pie(names=["Qualified", "Review"], values=[short, len(df)-short], 
                         hole=0.5, title="Selection Ratio", color_discrete_sequence=['#00cec9', '#ff7675'])
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

conn.close()