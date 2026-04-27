import streamlit as st
import base64
import os

st.set_page_config(page_title="View JD", layout="wide")

# ---------------- GET PDF ----------------
pdf_path = st.query_params.get("pdf")

if pdf_path and os.path.exists(pdf_path):

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        base_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    # ---------------- DOWNLOAD BUTTON ----------------
    st.download_button(
        label="⬇ Download PDF",
        data=pdf_bytes,
        file_name="Job_Description.pdf",
        mime="application/pdf"
    )

    # ---------------- FULL PAGE PDF VIEW ----------------
    st.markdown(
        f"""
        <iframe 
            src="data:application/pdf;base64,{base_pdf}" 
            width="100%" 
            height="1000px" 
            style="border:none;">
        </iframe>
        """,
        unsafe_allow_html=True
    )

else:
    st.error("PDF not found")

# ---------------- BACK BUTTON ----------------
if st.button("⬅ Back"):
    st.switch_page("2_best_match")