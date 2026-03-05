import streamlit as st
from backend.db.zen_repo import ZenRepository

@st.cache_data
def load_tickets():
    repo = get_repo()
    return repo.get_all_tickets()

@st.cache_resource
def get_repo():
    return ZenRepository()

def extract_values(tickets, field):
    return sorted({t[field] for t in tickets if t.get(field)})

def render_admin_dashboard():
    repo = get_repo()
    
    st.markdown("""
        <style>
        div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
            background-color: #2e7d32 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎫 Administrator Dashboard")

    # --- FILTERS ---
    tickets = load_tickets()
    st.markdown("### Filters")
    all_types = extract_values(tickets, 'TYPE')
    all_queues = extract_values(tickets, 'QUEUE')
    all_statuses = extract_values(tickets, 'STATUS')
    priority_map = {"URGENT": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    sort_options = {
    "Last updated": lambda x: x.get('UPDATED_AT') or x['CREATED_AT'],
    "Creation Date": lambda x: x['CREATED_AT'],
    "Priority": lambda x: priority_map.get(x['PRIORITY'], 4),
    "Status": lambda x: x['STATUS'],
    "Subject": lambda x: x.get('SUBJECT', "")
    }

    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2, 2, 1])
    with col1:
        filter_status = st.multiselect(
            "Status",
            options=all_statuses,
            placeholder="All statuses"
        )
    with col2:
        filter_type = st.multiselect(
            "Type",
            options=all_types,
            placeholder="All types"
        )
    with col3:
        filter_queue = st.multiselect(
            "Queue",
            options=all_queues,
            placeholder="All queues"
        )
    with col4:
        sort_col = st.selectbox(
            "Sort By",
            options=["Last updated", "Creation Date", "Priority", "Status", "Subject"]
        )
    with col5:
        sort_order = st.radio(
            "Order",
            ["DESC", "ASC"],
            horizontal=True
        )
    
    if filter_status:
        tickets = [t for t in tickets if t['STATUS'] in filter_status]

    if filter_type:
        tickets = [t for t in tickets if t['TYPE'] in filter_type]

    if filter_queue:
        tickets = [t for t in tickets if t['QUEUE'] in filter_queue]

    # Sorting Logic
    rev = sort_order == "DESC"
    tickets.sort(key=sort_options[sort_col], reverse=rev)

    st.divider()

    # --- CARD GRID ---
    if not tickets:
        st.info("No tickets found.")
    else:
        priority_colors = {
            "URGENT": "#ef4444",
            "HIGH": "#f97316",
            "MEDIUM": "#3b82f6",
            "LOW": "#22c55e"
        }
        status_styles = {
            "OPEN": ("#d4edda", "#155724"),
            "CLOSED": ("#f8d7da", "#721c24")
        }
        for row in range(0, len(tickets), 3):
            cols = st.columns(3)
            for col, t in zip(cols, tickets[row:row+3]):
                with col:
                    ticket_id_short = t['TICKET_ID'][:8]
                    p_color = priority_colors.get(t['PRIORITY'], "#6c757d")
                    status_bg, status_text = status_styles.get(t['STATUS'], ("#f8d7da", "#721c24"))

                    updated_val = t.get('UPDATED_AT') or t['CREATED_AT']

                    raw_subject = str(t.get('SUBJECT') or "").strip()
                    if not raw_subject:
                        display_subject = "[No Subject]"
                    else:
                        display_subject = raw_subject
                    subject = display_subject[:50]
                    if len(display_subject) > 50:
                        subject += "..."
                    with st.container(border=True):
                        st.markdown(f"""
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <code style='color: #888;'>#{ticket_id_short}</code>
                                <span style='background-color: {status_bg}; color: {status_text}; 
                                      padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; 
                                      font-weight: bold;'>{t['STATUS']}</span>
                            </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                            <div style='height: 60px; overflow: hidden; margin-top: 10px;'>
                                <h3 style='margin: 0; font-size: 1.15rem;'>{subject}</h3>
                            </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"**Priority:** <span style='color:{p_color};'>{t['PRIORITY']}</span>", unsafe_allow_html=True)

                        tag_type = t.get('TYPE') or '—'
                        tag_queue = t.get('QUEUE') or '—'
                        st.markdown(
                            f"<div style='margin-top:4px; font-size:0.8rem;'>"
                            f"<span style='background:#e0e7ff; color:#3730a3; padding:2px 8px; "
                            f"border-radius:12px; margin-right:6px;'>🏷 {tag_type}</span>"
                            f"<span style='background:#fef3c7; color:#92400e; padding:2px 8px; "
                            f"border-radius:12px;'>📋 {tag_queue}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                        st.markdown(f"""
                            <p style='font-style: italic; font-size: 0.8rem; color: #666; margin-bottom: 0;'>
                                Last updated: {updated_val.strftime('%Y-%m-%d %H:%M')}
                            </p>
                            <p style='font-style: italic; font-size: 0.8rem; color: #666; margin-top: 0;'>
                                Creation: {t['CREATED_AT'].strftime('%Y-%m-%d %H:%M')}
                            </p>
                        """, unsafe_allow_html=True)

                        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("💬 Open", key=f"open_{t['TICKET_ID']}", width='stretch'):
                                st.session_state.ticket_id = t['TICKET_ID']
                                st.session_state.page = "user_chat"
                                st.rerun()
                        with btn_col2:
                            if t['STATUS'] == 'OPEN':
                                if st.button("🛑 Close", key=f"close_{t['TICKET_ID']}", type="primary", width='stretch'):
                                    repo.close_ticket(t['TICKET_ID'])
                                    load_tickets.clear()
                                    st.rerun()
                            else:
                                st.button("Closed", key=f"dis_{t['TICKET_ID']}", disabled=True, width='stretch')
