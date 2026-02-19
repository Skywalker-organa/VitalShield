# --------------  patient.py  –  READS REAL DB  --------------
import streamlit as st
from datetime import date
import sqlite3
from security.encryption import decrypt_data
from security.key_manager import load_key
from security.hashing import add_log
from ai_utils import ai_recommendation

key   = load_key()
TODAY = date.today().strftime("%d/%m/%Y")
st.set_page_config(page_title="Vital Shield", layout="wide", initial_sidebar_state="expanded")


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,.stApp{font-family:"Inter",sans-serif;background:#f5f7fb;color:#1a1a1a}
section[data-testid="stSidebar"]{background:#0d0d0d;border-right:3px solid #3f77ff}
.sidebar-header{font-size:1.6rem;font-weight:800;color:#fff;margin-bottom:1.2rem}
.nav-item{padding:.6rem .8rem;margin:.3rem 0;border-radius:8px;color:#fff;font-weight:500;cursor:pointer;transition:background .2s}
.nav-item:hover{background:rgba(63,119,255,.15)}.nav-item.active{background:rgba(63,119,255,.25)}
.main-card{background:#fff;border:2px solid #dfe4ea;border-radius:16px;padding:2rem;margin-bottom:1.5rem}
.card-title{font-size:1.1rem;font-weight:700;margin-bottom:.8rem;text-transform:uppercase;letter-spacing:.5px;color:#3f77ff}
.row{margin-bottom:.7rem}.label{font-weight:600;color:#6c757d;font-size:.9rem}.value{font-size:1.05rem;font-weight:500}
.badge{display:inline-block;padding:.35rem .9rem;border-radius:20px;font-size:.85rem;font-weight:600}
.badge.accepted{background:#d1fae5;color:#065f46}.badge.pending{background:#fff3cd;color:#856404}
.badge.rejected{background:#fee2e2;color:#991b1b}.badge.revoked{background:#e5e7eb;color:#4b5563}
.risk-high{background:#fee2e2;color:#b91c1c;border:1.5px solid #fca5a5}.risk-medium{background:#fff3cd;color:#b45309;border:1.5px solid #fde68a}.risk-low{background:#d1fae5;color:#047857;border:1.5px solid #a7f3d0}
.stButton>button{width:100%;border-radius:24px;font-weight:600;padding:.5rem 0;border:1.5px solid #d1d5db;background:#fff;color:#111;transition:all .2s}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 4px 14px rgba(0,0,0,.12)}
.data-list{background:#f0fdf4;border:1.5px solid #bbf7d0;border-radius:12px;padding:1.2rem 1.5rem}
.data-list ul{list-style:none;padding:0;margin:.6rem 0 0 0}.data-list li{padding:.4rem 0;font-size:.95rem}
.timeline-box{background:#eff6ff;border:1.5px solid #93c5fd;border-radius:12px;padding:1.2rem 1.5rem;text-align:center}
.timeline-bars{display:flex;justify-content:space-between;align-items:flex-end;height:90px;margin-top:.8rem}
.bar{width:26px;background:#3b82f6;border-radius:4px 4px 0 0}.labels{display:flex;justify-content:space-between;font-size:.75rem;font-weight:500;color:#4b5563;margin-top:.4rem}
.ai-box{background:#faf5ff;border:1.5px solid #c4b5fd;border-radius:12px;padding:1.2rem 1.5rem}
.rec{padding:.8rem 1rem;border-radius:10px;margin:.8rem 0;font-weight:600}.rec.accept{background:#d1fae5;color:#065f46}.rec.reject{background:#fee2e2;color:#991b1b}.rec.consider{background:#fff3cd;color:#b45309}
.reason{background:#fff;border-left:4px solid #8b5cf6;padding:.8rem 1rem;border-radius:8px;font-size:.95rem;line-height:1.5}
.log-card{background:#fdf4ff;border:1.5px solid #f0abfc;border-radius:12px;padding:1.2rem 1.5rem}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
#  FETCH ALL PENDING REQUESTS
# ---------------------------------------------------------
def get_connection():
    return sqlite3.connect("consent.db", check_same_thread=False)

# Fetch ALL pending requests instead of just the newest one
with get_connection() as conn:
    rows = conn.execute(
        "SELECT id, patient_name, org_name, data_type, purpose, days, status "
        "FROM consent_requests "
        "WHERE status = 'Pending' "
        "ORDER BY id DESC"
    ).fetchall()

# fallback dummy row if no pending requests
if not rows:
    # Show a demo request if no real ones exist
    demo_row = (1, "John Doe", "DemoOrg", b"Blood test", b"General check-up", 30, "Pending")
    rows = [demo_row]

# ---------------------------------------------------------
#  SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-header">🛡️ Vital Shield</div>', unsafe_allow_html=True)
    st.markdown("---")
    for label, icon in [("📊 Dashboard","active"), ("📋 Consent request list",""),
                        ("✅ Active consents",""), ("⏳ Pending requests",""),
                        ("🚫 Revoked",""), ("⚠️ High-risk shares","")]:
        st.markdown(f'<div class="nav-item {icon}">{label}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
#  MAIN
# ---------------------------------------------------------
st.markdown("# HELLO THERE!")

# Show count of pending requests
pending_count = len(rows)
if pending_count == 1 and rows[0][0] == 1:  # Check if it's the demo request
    st.markdown(f"### 📋 Consent Request List (Demo)")
else:
    st.markdown(f"### 📋 Consent Request List ({pending_count} Pending Request{'s' if pending_count > 1 else ''})")

# Create a container for all requests
requests_container = st.container()

# Display each request in its own card
for i, row in enumerate(rows):
    request_id, patient_name, org_name, data_type, purpose, days, status = row
    
    # Try to decrypt, but if it fails, show placeholder
    try:
        if status == "Accepted":
            decrypted_data = decrypt_data(data_type, key) if isinstance(data_type, bytes) else data_type
            decrypted_purpose = decrypt_data(purpose, key) if isinstance(purpose, bytes) else purpose
        else:
            # For pending requests, try to decrypt to show what's being requested
            decrypted_data = decrypt_data(data_type, key) if isinstance(data_type, bytes) else data_type
            decrypted_purpose = decrypt_data(purpose, key) if isinstance(purpose, bytes) else purpose
    except:
        decrypted_data = "🔒 Encrypted Data"
        decrypted_purpose = "🔒 Encrypted Purpose"
    
    # badge / risk colours
    status_colour = {"Pending":"pending","Accepted":"accepted","Rejected":"rejected","Revoked":"revoked"}.get(status, "pending")
    risk_colour = "risk-low"
    
    # Add some spacing between requests
    if i > 0:
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Create columns for this specific request
    left, right = st.columns([2, 1])
    
    with left:
        st.markdown(f"""
        <div class="main-card">
            <div class="row"><span class="label">Request ID</span><div class="value">{request_id}</div></div>
            <div class="row"><span class="label">Patient</span><div class="value">{patient_name}</div></div>
            <div class="row"><span class="label">Organisation</span><div class="value">{org_name}</div></div>
            <div class="row"><span class="label">Data Requested</span><div class="value">{decrypted_data}</div></div>
            <div class="row"><span class="label">Purpose</span><div class="value">{decrypted_purpose}</div></div>
            <div class="row"><span class="label">Duration</span><div class="value">{days} days</div></div>
            <div class="row"><span class="label">Risk Level</span><span class="badge {risk_colour}">Low Risk</span></div>
            <div class="row"><span class="label">Status</span><span class="badge {status_colour}">{status}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # Action buttons for THIS specific request
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button("ACCEPT", key=f"accept_{request_id}"):
                try:
                    with get_connection() as conn:
                        conn.execute(
                            "UPDATE consent_requests SET status = 'Accepted' WHERE id = ?",
                            (request_id,)
                        )
                        conn.commit()
                    add_log("ACCEPT", st.session_state.get("username", "Patient"), f"Accepted request #{request_id}")
                    st.success(f"✅ Request #{request_id} accepted!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with b2:
            if st.button("REJECT", key=f"reject_{request_id}"):
                try:
                    with get_connection() as conn:
                        conn.execute(
                            "UPDATE consent_requests SET status = 'Rejected' WHERE id = ?",
                            (request_id,)
                        )
                        conn.commit()
                    add_log("REJECT", st.session_state.get("username", "Patient"), f"Rejected request #{request_id}")
                    st.success(f"❌ Request #{request_id} rejected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with b3:
            if st.button("REVOKE", key=f"revoke_{request_id}"):
                try:
                    with get_connection() as conn:
                        conn.execute(
                            "UPDATE consent_requests SET status = 'Revoked' WHERE id = ?",
                            (request_id,)
                        )
                        conn.commit()
                    add_log("REVOKE", st.session_state.get("username", "Patient"), f"Revoked request #{request_id}")
                    st.success(f"🔄 Request #{request_id} revoked!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with b4:
            if st.button("ASK AI", key=f"ai_{request_id}"):
                st.session_state[f"show_ai_{request_id}"] = True
                st.rerun()
    
    with right:
        # Show shared data list for this request
        st.markdown(f"""
        <div class="data-list"><div class="card-title">Data to be Shared</div>
        <ul><li>{decrypted_data}</li></ul></div>
        """, unsafe_allow_html=True)
        
        # Show timeline chart
        st.markdown("""
        <div class="timeline-box"><div class="card-title">Data Access History</div>
        <div class="timeline-bars">
            <div class="bar" style="height:30%"></div><div class="bar" style="height:80%"></div>
            <div class="bar" style="height:50%"></div><div class="bar" style="height:90%"></div>
            <div class="bar" style="height:60%"></div><div class="bar" style="height:95%"></div>
            <div class="bar" style="height:40%"></div>
        </div>
        <div class="labels"><span>J</span><span>F</span><span>M</span><span>A</span><span>M</span><span>J</span><span>J</span></div></div>
        """, unsafe_allow_html=True)
    
    # ---------------  AI BOX for THIS request  ----------------
    if st.session_state.get(f"show_ai_{request_id}"):
        try:
            recommendation, reason = ai_recommendation(decrypted_data, decrypted_purpose)
            rec_class = {"Accept":"accept","Reject":"reject"}.get(recommendation, "consider")
            st.markdown(f"""
            <div class="ai-box"><div class="card-title">🤖 AI-Powered Recommendation (Request #{request_id})</div>
            <div class="rec {rec_class}">{recommendation}</div>
            <div class="reason"><strong>Analysis:</strong><br>{reason}</div></div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"AI analysis failed: {str(e)}")

# ---------------  LOG CARD  ----------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div class="log-card"><div class="card-title">Log History of Previous Actions</div>
<div style="font-size:0.95rem;line-height:1.6">
<strong>{TODAY}:</strong> Blood test to check hemoglobin was recorded by Apollo Diagnostics and synced to Apollo Hospital via EHR for patient condition evaluation as part of general check-up.<br>
<span style="color:#047857;font-weight:600">[Consent Accepted]</span>
</div></div>
""", unsafe_allow_html=True)