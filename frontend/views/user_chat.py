import streamlit as st
from backend.agent import run_agent
from backend.db.zen_repo import ZenRepository

@st.cache_resource
def get_repo():
    return ZenRepository()

def render_user_chat():
    st.cache_data.clear()
    repo = get_repo()
    user_role = st.session_state.get("role", "User")

    # --- STATE INIT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "loaded_ticket_id" not in st.session_state:
        st.session_state.loaded_ticket_id = None
    if "ticket_id" not in st.session_state:
        st.session_state.ticket_id = None
    if "error_message" not in st.session_state:
        st.session_state.error_message = None

    current_target_id = st.session_state.ticket_id
    
    if current_target_id and st.session_state.loaded_ticket_id != current_target_id:
        with st.spinner("Loading conversation history..."):
            history = repo.get_ticket_messages(current_target_id)
            ticket_info = repo.get_ticket_status(current_target_id)
            
            st.session_state.messages = history
            st.session_state.loaded_ticket_id = current_target_id
            
            if ticket_info:
                st.session_state.priority = ticket_info.get("PRIORITY", "LOW")

    # --- LOADING LOGIC ---
    if st.session_state.ticket_id and not st.session_state.messages:
        with st.spinner("Loading conversation history..."):
            history = repo.get_ticket_messages(st.session_state.ticket_id)
            ticket_info = repo.get_ticket_status(st.session_state.ticket_id)
            
            if history:
                st.session_state.messages = history
            if ticket_info:
                st.session_state.priority = ticket_info.get("PRIORITY", "LOW")

    # --- TOP NAVIGATION BAR ---
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("🏠 Home"):
            st.session_state.page = "home"
            st.session_state.ticket_id = None
            st.session_state.error_message = None
            st.session_state.loaded_ticket_id = None
            st.rerun()

    with nav_col2:
        if st.session_state.ticket_id:
            priority = st.session_state.get("priority", "LOW")
            p_color = {"URGENT": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#3b82f6", "LOW": "#22c55e"}.get(priority)
            
            st.markdown(
                f"""
                <div style='text-align: center; margin-top: -10px;'>
                    <h3 style='margin-bottom: 0;'>Ticket #{st.session_state.ticket_id[:8]}</h3>
                    <span style='background-color: {p_color}; color: white; padding: 2px 10px; 
                                 border-radius: 12px; font-size: 0.8rem; font-weight: bold;'>{priority}</span>
                </div>
            """, unsafe_allow_html=True)

    with nav_col3:
        if st.session_state.ticket_id:
            if user_role == "Admin":
                if st.button("Close Ticket", type="primary"):
                    repo.close_ticket(st.session_state.ticket_id)
                    st.toast("Ticket closed.")
                    st.session_state.page = "home"
                    st.rerun()
            else:
                if st.button("Exit Chat"):
                    st.session_state.page = "home"
                    st.rerun()

    st.divider()

    # --- ERROR DISPLAY ---
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        if st.button("Clear Error"):
            st.session_state.error_message = None
            st.rerun()

    # --- ICONS ---
    ICON_ROBOT = "data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSItNiAtNiAzNi4wMCAzNi4wMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBzdHJva2U9IiNmZmZmZmYiPjxnIGlkPSJTVkdSZXBvX2JnQ2FycmllciIgc3Ryb2tlLXdpZHRoPSIwIj48cmVjdCB4PSItNiIgeT0iLTYiIHdpZHRoPSIzNi4wMCIgaGVpZ2h0PSIzNi4wMCIgcng9IjAiIGZpbGw9IiNkYjZhMDAiIHN0cm9rZXdpZHRoPSIwIj48L3JlY3Q+PC9nPjxnIGlkPSJTVkdSZXBvX3RyYWNlckNhcnJpZXIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PC9nPjxnIGlkPSJTVkdSZXBvX2ljb25DYXJyaWVyIj4gPHBhdGggZD0iTTkgMTVDOC40NDc3MSAxNSA4IDE1LjQ0NzcgOCAxNkM4IDE2LjU1MjMgOC40NDc3MSAxNyA5IDE3QzkuNTUyMjkgMTcgMTAgMTYuNTUyMyAxMCAxNkMxMCAxNS40NDc3IDkuNTUyMjkgMTUgOSAxNVoiIGZpbGw9IiNmZmZmZmYiPjwvcGF0aD4gPHBhdGggZD0iTTE0IDE2QzE0IDE1LjQ0NzcgMTQuNDQ3NyAxNSAxNSAxNUMxNS41NTIzIDE1IDE2IDE1LjQ0NzcgMTYgMTZDMTYgMTYuNTUyMyAxNS41NTIzIDE3IDE1IDE3QzE0LjQ0NzcgMTcgMTQgMTYuNTUyMyAxNCAxNloiIGZpbGw9IiNmZmZmZmYiPjwvcGF0aD4gPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGRkIiBkPSJNMTIgMUMxMC44OTU0IDEgMTAgMS44OTU0MyAxMCAzQzEwIDMuNzQwMjggMTAuNDAyMiA0LjM4NjYzIDExIDQuNzMyNDRWN0g2QzQuMzQzMTUgNyAzIDguMzQzMTUgMyAxMFYyMEMzIDIxLjY1NjkgNC4zNDMxNSAyMyA2IDIzSDE4QzE5LjY1NjkgMjMgMjEgMjEuNjU2OSAyMSAyMFYxMEMyMSA4LjM0MzE1IDE5LjY1NjkgNyAxOCA3SDEzVjQuNzMyNDRDMTMuNTk3OCA0LjM4NjYzIDE0IDMuNzQwMjggMTQgM0MxNCAxLjg5NTQzIDEzLjEwNDYgMSAxMiAxWk01IDEwQzUgOS40NDc3MiA1LjQ0NzcyIDkgNiA5SDcuMzgxOTdMOC44MjkxOCAxMS44OTQ0QzkuMTY3OTYgMTIuNTcyIDEwLjg2MDUgMTMgMTAuNjE4IDEzSDEzLjM4MkMxNC4xMzk1IDEzIDE0LjgzMiAxMi41NzIgMTUuMTcwOCAxMS44OTQ0TDE2LjYxOCA5SDE4QzE4LjU1MjMgOSAxOSA5LjQ0NzcyIDE5IDEwVjIwQzE5IDIwLjU1MjMgMTguNTUyMyAyMSAxOCAyMUg2QzUuNDQ3NzIgMjEgNSAyMC41NTIzIDUgMjBWMTRaTTEzLjM4MiAxMUwxNC4zODIgOUg5LjYxODAzTDEwLjYxOCAxMUgxMy4zODJaIiBmaWxsPSIjZmZmZmZmIj48L3BhdGg+IDxwYXRoIGQ9Ik0xIDE0QzAuNDQ3NzE1IDE0IDAgMTQuNDQ3NyAwIDE1VjE3QzAgMTcuNTUyMyAwLjQ0NzcxNSAxOCAxIDE4QzEuNTUyMjggMTggMiAxNy41NTIzIDIgMTdWMTVDMiAxNC40NDc3IDEuNTUyMjggMTQgMSAxNFoiIGZpbGw9IiNmZmZmZmYiPjwvcGF0aD4gPHBhdGggZD0iTTIyIDE1QzIyIDE0LjQ0NzcgMjIuNDQ3NyAxNCAyMyAxNEMyMy41NTIzIDE0IDI0IDE0LjQ0NzcgMjQgMTVWMTdDMjQgMTcuNTUyMyAyMy41NTIzIDE4IDIzIDE4QzIyLjQ0NzcgMTggMjIgMTcuNTUyMyAyMiAxN1YxNVoiIGZpbGw9IiNmZmZmZmYiPjwvcGF0aD4gPC9nPjwvc3ZnPg=="
    ICON_USER = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgcng9IjQiIGZpbGw9IiNlZjQ0NDQiLz48cGF0aCBkPSJNMTggMjF2LTJhNCA0IDAgMCAwLTQtNEg4YTQgNCAwIDAgMC00IDR2MiIvPjxjaXJjbGUgY3g9IjEyIiBjeT0iNyIgcj0iNCIvPjwvc3ZnPg=="
    ICON_ADMIN = "data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSItNy43NSAtNy43NSA0MC41MCA0MC41MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBzdHJva2U9IiNmZmZmZmYiPjxnIGlkPSJTVkdSZXBvX2JnQ2FycmllciIgc3Ryb2tlLXdpZHRoPSIwIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLDApLCBzY2FsZSgxKSI+PHJlY3QgeD0iLTcuNzUiIHk9Ii03Ljc1IiB3aWR0aD0iNDAuNTAiIGhlaWdodD0iNDAuNTAiIHJ4PSIyLjAyNSIgZmlsbD0iIzAwMGRiZCIgc3Ryb2tld2lkdGg9IjAiPjwvcmVjdD48L2c+PGcgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNNi43MjI2NiA1LjQ3OTY4QzYuODEwMTEgNC42MDMyIDcuMTE2NjMgMy43NjI4IDcuNjE0MDIgMy4wMzU4NUM4LjExMTQxIDIuMzA4ODkgOC43ODM2OCAxLjcxODc0IDkuNTY4OTUgMS4zMTk3MUMxMC4zNTQyIDAuOTIwNjg0IDExLjIyNzIgMC43MjU2MDcgMTIuMTA3NyAwLjc1MjQzN0MxMi45ODgxIDAuNzc5MjY3IDEzLjg0NzYgMS4wMjcxNCAxNC42MDcxIDEuNDczMjRDMTUuMzY2NiAxLjkxOTM1IDE2LjAwMTcgMi41NDkzNCAxNi40NTM5IDMuMzA1MjRDMTYuOTA2MSA0LjA2MTEzIDE3LjE2MDkgNC45MTg2MyAxNy4xOTQ4IDUuNzk4ODFDMjAuMjI4NyA2LjY3ODk5IDE3LjA0MDcgNy41NTM1NSAxNi42NDggOC4zNDJDMTYuMjYyNyA5LjExNTYzIDE1LjY5MjUgOS43ODE5NSAxNC45ODgzIDEwLjI4MjEiPjwvcGF0aD48cGF0aCBkPSJNNy40Mzk0NSAzLjM1MjY4QzguMjUyMDcgNC4xOTE2MSA5LjIyNTEyIDQuODU4NTQgMTAuMzAwNyA1LjMxMzc5QzExLjM3NjMgNS43NjkwNCAxMi41MzI1IDYuMDAzMzIgMTMuNzAwNSA2LjAwMjY4QzE0Ljg0OTIgNi4wMDM4MiAxNS45ODY1IDUuNzc3NjIgMTcuMDQ2OSA1LjMzNzQyIj48L3BhdGg+PHBhdGggZD0iTTEwLjgyMzIgOS43NTI2OEMxMC41MjY2IDkuNzUyNjggMTAuMjM2NiA5Ljg0MDY1IDkuOTg5ODkgMTAuMDA1NUM5Ljc0MzIxIDEwLjE3MDMgOS41NTA5NiAxMC40MDQ2IDkuNDM3NDIgMTAuNjc4N0M5LjMyMzg5IDEwLjk1MjcgOS4yOTQxOSAxMS4yNTQzIDkuMzUyMDYgMTEuNTQ1M0M5LjQwOTk0IDExLjgzNjMgOS41NTI4IDEyLjEwMzYgOS43NjI1OCAxMi4zMTMzQzkuOTcyMzYgMTIuNTIzMSAxMC4yMzk2IDEyLjY2NiAxMC41MzA2IDEyLjcyMzlDMTAuODIxNiAxMi43ODE3IDExLjEyMzIgMTIuNzUyIDExLjM5NzMgMTIuNjM4NUMxMS42NzE0IDEyLjUyNSAxMS45MDU2IDEyLjMzMjcgMTIuMDcwNCAxMi4wODZDMTIuMjM1MyAxMS44Mzk0IDEyLjMyMzIgMTEuNTQ5MyAxMi4zMjMyIDExLjI1MjdDMTEuMjMyMyAxMC44NTQ5IDEyLjE2NTIgMTAuNDczMyAxMS44ODM5IDEwLjE5MkMxMS42MDI2IDkuOTEwNzEgMTEuMjIxMSA5Ljc1MjY4IDEwLjgyMzIgOS43NTI2OFoiPjwvcGF0aD48cGF0aCBkPSJNNC44MjMyNCA3LjE3NDY3VjguMjUyNjhDNC44MjMyNCA5LjA0ODMyIDUuMTM5MzEgOS44MTEzOSA1LjcwMTkyIDEwLjM3NEM2LjI2NDUzIDEwLjkzNjYgNy4wMjc1OSAxMS4yNTI3IDcuODIzMjQgMTEuMjUyN0g5LjI0NjQ5Ij48L3BhdGg+PHBhdGggZD0iTTIxLjcwMDUgMjMuMjUyN0MyMS43MDA2IDIxLjQ2OTMgMjEuMjExIDE5LjcyMDIgMjAuMjg1MiAxOC4xOTZDMTkuMzYzMiAxNi42Nzc5IDE4LjA0MzggMTUuNDQwOSAxNi40Njk3IDE0LjYxODciPjwvcGF0aD48cGF0aCBkPSJNMi4yMDAyIDIzLjI1MjdDMi4yIDIxLjQ2OTUgMi42ODkyNiAxOS43MjA2IDMuNjE0NjUgMTguMTk2M0M0LjUzNTQyIDE2LjY3OTcgNS44NTI4NCAxNS40NDM1IDcuNDI0NTMgMTQuNjIxIj48L3BhdGg+PC9nPjwvc3ZnPg=="


    # --- MESSAGE RENDERER ---
    for msg in st.session_state.messages:
        db_role = msg["role"]
        if user_role == "Admin":
            if db_role == "USER":
                with st.chat_message("assistant", avatar=ICON_USER):
                    st.markdown(msg["content"])
            elif db_role == "AGENT_AI":
                with st.chat_message("assistant", avatar=ICON_ROBOT):
                    st.markdown(msg["content"])

            elif db_role == "AGENT_HUMAN":
                with st.chat_message("user", avatar=ICON_ADMIN):
                    st.markdown(msg["content"])
        else:
            if db_role == "USER":
                with st.chat_message("user", avatar=ICON_USER):
                    st.markdown(msg["content"])
            elif db_role == "AGENT_AI":
                with st.chat_message("assistant", avatar=ICON_ROBOT):
                    st.markdown(msg["content"])

            elif db_role == "AGENT_HUMAN":
                with st.chat_message("assistant", avatar=ICON_ADMIN):
                    st.markdown(msg["content"])

    # --- CHAT INPUT ---
    placeholder = "Admin Reply..." if user_role == "Admin" else "Describe your issue..."
    if prompt := st.chat_input(placeholder):
        if user_role == "Admin":
            repo.add_message(st.session_state.ticket_id, "AGENT_HUMAN", prompt)
            st.session_state.messages.append({"role": "AGENT_HUMAN", "content": prompt})
            st.rerun()
        else:
            st.session_state.messages.append({"role": "USER", "content": prompt})
            st.session_state.processing_agent = True
            st.rerun()

    # --- AGENT PROCESSING ---
    if st.session_state.get("processing_agent"):
        st.session_state.processing_agent = False
        with st.chat_message("assistant", avatar=ICON_ROBOT):
            with st.spinner("Thinking..."):
                try:
                    response = run_agent(st.session_state.messages[-1]["content"], st.session_state.ticket_id)
                    st.session_state.ticket_id = response.get("ticket_id")
                    st.session_state.messages.append({"role": "AGENT_AI", "content": response["response"]})
                    st.rerun()
                except Exception as e:
                    st.session_state.error_message = str(e)
                    st.rerun()