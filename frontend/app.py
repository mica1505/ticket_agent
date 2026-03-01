import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]  # ticket_agent/
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pages.user_home import render_home
from pages.past_tickets import render_past_tickets
from pages.user_chat import render_user_chat

# --- CONFIG ---
st.set_page_config(
    page_title="Support Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- STATE INIT ---
if "entered_app" not in st.session_state:
    st.session_state.entered_app = False
if "role" not in st.session_state:
    st.session_state.role = "User"
if "page" not in st.session_state:
    st.session_state.page = "home"


# --- ROUTER ---
if st.session_state.page == "home":
    render_home()

elif st.session_state.page == "past_tickets":
    render_past_tickets()

elif st.session_state.page == "user_chat":
    render_user_chat()

