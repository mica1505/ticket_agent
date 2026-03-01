import streamlit as st
from pathlib import Path
import base64
from backend.db.zen_repo import ZenRepository

@st.cache_resource
def get_repo():
    return ZenRepository()

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render_home():
    repo = get_repo()
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    css_path = BASE_DIR / "styles.css"
    banner_path = BASE_DIR / "banner.png"
    css = css_path.read_text()
    banner_base64 = img_to_base64(banner_path)
    
    st.markdown(
           f"""
           <style>
           {css}   
           .hero {{
                background-image:
                   linear-gradient(rgba(0,0,0,0.25), rgba(0,0,0,0.25)),
                   url("data:image/png;base64,{banner_base64}");   
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;   
                padding: 40px 20px;
                border-radius: 12px;
                color: white;
                text-align: center;
                width: 100vw;
                position: relative;
                left: 50%;
                right: 50%;
                margin-left: -50vw;
                margin-right: -50vw;
                margin-top: 0;
           }}
           
           .status-text-large {{
                font-size: 26px !important; 
                font-weight: 600 !important;
                margin: 0 !important;
                padding: 0 !important;
                margin-top: 32px !important; 
                line-height: 1.2 !important;
                white-space: nowrap;
           }}

           div[data-testid="stForm"] button[kind="primaryFormSubmit"] {{
               background-color: #ff4b4b !important;
               color: white !important;
               border: none !important;
               height: 48px !important;
               font-weight: bold !important;
           }}
           </style>
           """,
           unsafe_allow_html=True
       )

    st.markdown('<div class="hero"><h1>Support Desk</h1><h2>How can we help you today?</h2></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("Raise a Problem", use_container_width=True):
            st.session_state.messages = []
            st.session_state.loaded_ticket_id = None
            st.session_state.page = "user_chat"
            st.rerun()

    st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)

    # ---- CARDS ----
    _, c1, c2, _ = st.columns([0.5, 1.5, 1.5, 0.5])

    with c1:
        with st.form("ticket_status_form"):
            st.markdown("### 🔎 Check Ticket Status")
            st.markdown("<p style='font-size:16px;'>Enter your ID to check status.</p>", unsafe_allow_html=True)

            ticket_id = st.text_input("Ticket ID", placeholder="Enter ID...", label_visibility="collapsed")
            status_submit = st.form_submit_button("View Status", use_container_width=True)
            
            if status_submit and ticket_id.strip():
                ticket = repo.get_ticket_status(ticket_id.strip())
                st.session_state.cached_ticket = ticket
                st.session_state.last_searched = ticket_id.strip()
            
            if st.session_state.get("last_searched") == ticket_id.strip() and st.session_state.get("cached_ticket"):
                ticket = st.session_state.cached_ticket
                status_val = ticket['STATUS']
                color = '#28a745' if status_val == 'OPEN' else '#6c757d'
                
                if status_val == "OPEN":
                    col_left, col_right = st.columns([1.4, 1]) 
                    with col_left:
                         st.markdown(f'<div class="status-text-large">Status: <span style="color:{color};">{status_val}</span></div>', unsafe_allow_html=True)
                    with col_right:
                         if st.form_submit_button("💬 Open Chat", type="primary", use_container_width=True):
                            # Reset history if moving to a different ticket
                            if st.session_state.get("loaded_ticket_id") != ticket_id.strip():
                                st.session_state.messages = []
                                st.session_state.loaded_ticket_id = None
                            
                            st.session_state.ticket_id = ticket_id.strip()
                            st.session_state.page = "user_chat"
                            st.rerun()
                else:
                    st.markdown(f'<div class="status-text-large">Status: <span style="color:{color};">{status_val}</span></div>', unsafe_allow_html=True)
            elif status_submit and not st.session_state.get("cached_ticket"):
                st.error("Ticket not found")
            else:
                st.markdown("<div style='height:65px'></div>", unsafe_allow_html=True)

    with c2:
        with st.form("past_tickets_form"):
            st.markdown("### 📂 View Past Tickets")
            st.markdown("<p style='font-size:16px;'>Access your full history of previous tickets.</p>", unsafe_allow_html=True)
            st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
            if st.form_submit_button("Browse History", use_container_width=True):
                st.session_state.page = "past_tickets"
                st.rerun()

    _, footer_col, _ = st.columns([1, 1.5, 1])
    with footer_col:
        st.markdown(
            """
            <div class="kb">
                <h4>Urgent?</h4>
                <div class="kb-item">
                    <strong>Hotline: 3333</strong><br/>
                    <small>Office hours: Mon-Fri, 9am - 7pm</small>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
