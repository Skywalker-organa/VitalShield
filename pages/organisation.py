import streamlit as st
import sqlite3
from security.encryption import encrypt_data
from security.key_manager import load_key
from security.hashing import add_log
from datetime import datetime 

key = load_key()

def get_connection():
    return sqlite3.connect("consent.db", check_same_thread=False)

def init_table():
    with get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS consent_requests(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            org_name    TEXT NOT NULL,
            data_type   BLOB NOT NULL,
            purpose     BLOB NOT NULL,
            days        INTEGER NOT NULL,
            status      TEXT DEFAULT 'Pending',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );""")
init_table()

st.set_page_config(page_title="Organisation Dashboard", layout="wide")
st.title("Organisation Dashboard")
st.markdown("""
<style>
/* 1.  MAIN BODY LIGHT  */
.stApp {
    background-color: #f5f7fb !important;   /* page background */
    color: #000000 !important;              /* default text */
}

/* 2.  SIDEBAR STAYS BLACK  */
section[data-testid="stSidebar"] {
    background-color: #0d0d0d !important;
    border-right: 3px solid #3f77ff;
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;              /* white text in sidebar */
}

/* 3.  EVERY HEADING / LABEL / BUTTON TEXT → BLACK  */
h1, h2, h3, h4, h5, h6, label, p, span, div {
    color: #000000 !important;
}

/* 3.  EVERY HEADING / LABEL / BUTTON TEXT → BLACK  */
p,div {
    color: #0000CD !important;
}

/* 4.  FORM CARD + INPUTS LIGHT  */
div[data-testid="stForm"] {
    background-color: #ffffff !important;
    border: 1px solid #e0e0e0;
    border-radius: 16px;
}
input, textarea, div[data-baseweb="input"] input, div[data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #ccd1d6 !important;
    border-radius: 10px !important;
}

/* 5.  BUTTONS LIGHT  */
.stButton > button {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1.5px solid #d0d5dc !important;
    border-radius: 14px !important;
}
.stButton > button:hover {
    background-color: #f1f3f6 !important;
    color: #000000 !important;
}
.stButton > button:active {
    background-color: #e5e8eb !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

org_name = st.session_state.get("username", "DemoOrg")



with st.form("consent_request_form"):
    st.markdown("#### Request Details")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name *", placeholder="e.g. John Doe")
        data_type    = st.text_input("Data Type Requested *", placeholder="e.g. Blood Test Results")
    with col2:
        purpose = st.text_input("Purpose of Access *", placeholder="e.g. Medical Research")
        days    = st.number_input("Access Duration (days) *", min_value=1, max_value=365, value=30)

    submitted = st.form_submit_button("🔐 Send Encrypted Request", use_container_width=True)

    if submitted:
        if not patient_name or not data_type or not purpose:
            st.error(" Please fill all required fields!")
        else:
            try:
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("""INSERT INTO consent_requests
                        (patient_name, org_name, data_type, purpose, days, status)
                        VALUES (?,?,?,?,?,?)""",
                        (patient_name, org_name,
                         encrypt_data(data_type, key),
                         encrypt_data(purpose, key),
                         days, "Pending"))
                    req_id = cur.lastrowid
                    conn.commit()
                
                add_log("REQUEST", org_name, f"Requested {data_type} from {patient_name} (ID {req_id})")
                st.success(f"✅ Request sent securely! ID: {req_id}")
                st.balloons()
                
            except Exception as e:
                st.error(f" Error: {str(e)}")

st.markdown("---")
st.markdown("### Your Sent Requests")


try:
    with get_connection() as conn:
        rows = conn.execute("""SELECT id, patient_name, data_type, purpose, days, status, created_at
                               FROM consent_requests
                               WHERE org_name = ?
                               ORDER BY created_at DESC""", (org_name,)).fetchall()
except Exception as e:
    st.error(f"Error loading requests: {str(e)}")
    rows = []

if not rows:
    st.info("No requests sent yet.")
else:
    for r in rows:
        stat_emoji = {"Pending":"🟡","Accepted":"🟢","Rejected":"🔴","Revoked":"⚫"}.get(r[5],"⚪")
        with st.expander(f"{stat_emoji} Request #{r[0]} – {r[1]} – {r[5]}"):
            st.write(f"**Patient:** {r[1]}")
            st.write(f"**Status:** {r[5]}")
            st.write(f"**Duration:** {r[4]} days")
            st.write(f"**Created:** {r[6]}")
            if r[5] == "Pending":
                st.info("⏳ Waiting for patient approval")
            elif r[5] == "Accepted":
                st.success("✅ Access granted – data available")
                st.balloons()
            elif r[5] == "Rejected":
                st.error("❌ Request rejected by patient")
            elif r[5] == "Revoked":
                st.warning("⚠️ Access has been revoked")
                

