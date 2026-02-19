import streamlit as st
import sqlite3
import time

def create_tables():
    conn = sqlite3.connect("consent.db")
    cur  = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS consent_requests(
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT    NOT NULL,
        org_name     TEXT    NOT NULL,
        data_type    BLOB    NOT NULL,
        purpose      BLOB    NOT NULL,
        days         INTEGER NOT NULL,
        status       TEXT    DEFAULT 'Pending'
    );
    """)
    conn.commit()
    conn.close()

st.set_page_config(page_title="Consent Management System")

create_tables()

st.title("🔐 Healthcare Consent Management System")

role = st.selectbox("Select your role", ["Patient", "Organization"])
username = st.text_input("Enter your name")

if st.button("Login"):
    with st.spinner("🔐 Encrypting session…"):
        time.sleep(1.2)          # fake but looks cryptographic
    st.session_state["role"] = role
    st.success(f"Welcome {username}!")
    st.balloons()
    st.switch_page("pages/organisation.py" if role == "Organisation" else "pages/patient.py")

