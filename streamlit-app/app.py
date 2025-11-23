"""
FinClose AI - Streamlit Application
Main entry point for the month-end close automation system
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
sys.path.append('..')

# Configure page
st.set_page_config(
    page_title="FinClose AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f9fafb;
        border-radius: 0.5rem;
        padding: 1.5rem;
        border-left: 4px solid #3b82f6;
    }
    .status-pending {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .status-in-progress {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .status-complete {
        background-color: #d1fae5;
        color: #065f46;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .status-error {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# Simple authentication (in production, use AWS Cognito)
def authenticate(username, password):
    # Mock authentication
    users = {
        "justine": {"password": "demo", "name": "Justine O'Sullivan", "role": "Controller"},
        "selena": {"password": "demo", "name": "Selena Ochoa", "role": "Senior Accountant"},
        "will": {"password": "demo", "name": "Will Ott", "role": "Equity Manager"}
    }
    
    if username in users and users[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.user_name = users[username]["name"]
        st.session_state.user_role = users[username]["role"]
        return True
    return False

# Login page
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">FinClose AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Month-End Close Automation</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if authenticate(username, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.info("Demo credentials: justine/demo, selena/demo, will/demo")
    
    st.stop()

# Sidebar navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/3b82f6/ffffff?text=FinClose+AI", use_container_width=True)
    st.markdown(f"**{st.session_state.user_name}**")
    st.caption(st.session_state.user_role)
    st.divider()
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📅 Calendar", "⚙️ Workflows", "✅ Approvals", "📊 Reports", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Main content area
if page == "🏠 Home":
    st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">November 2025 Close Cycle</div>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Close Day", "BD3", "3 days remaining")
    
    with col2:
        st.metric("Tasks Complete", "5/12", "42%")
    
    with col3:
        st.metric("Pending Approvals", "2", "-1 from yesterday")
    
    with col4:
        st.metric("Time Saved", "4.5 hrs", "+85% efficiency")
    
    st.divider()
    
    # Recent activity
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Recent Activity")
        
        activities = [
            {"time": "10 minutes ago", "event": "ZIP Accrual Agent completed", "status": "complete"},
            {"time": "2 hours ago", "event": "Payroll Reconciliation awaiting approval", "status": "pending"},
            {"time": "Yesterday", "event": "Equity Processing approved by Will Ott", "status": "complete"},
        ]
        
        for activity in activities:
            status_class = f"status-{activity['status']}"
            st.markdown(f"""
            <div style="padding: 1rem; background-color: #f9fafb; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600;">{activity['event']}</div>
                        <div style="color: #6b7280; font-size: 0.875rem;">{activity['time']}</div>
                    </div>
                    <span class="{status_class}">{activity['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Quick Actions")
        
        if st.button("🔄 Run ZIP Accrual", use_container_width=True):
            st.info("Starting ZIP Accrual workflow...")
        
        if st.button("📝 Run Payroll Recon", use_container_width=True):
            st.info("Starting Payroll Reconciliation...")
        
        if st.button("💼 Process Equity", use_container_width=True):
            st.info("Starting Equity Processing...")
        
        st.divider()
        
        st.subheader("System Health")
        st.success("✅ All systems operational")
        st.metric("API Latency", "245ms", "-50ms")

elif page == "📅 Calendar":
    st.markdown('<div class="main-header">Month-End Calendar</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">November 2025 Close Schedule</div>', unsafe_allow_html=True)
    
    # Calendar view
    import pandas as pd
    
    tasks = [
        {"day": "BD-2", "date": "Nov 26", "task": "Vendor Outreach", "owner": "ZIP Agent", "status": "Pending"},
        {"day": "BD-1", "date": "Nov 27", "task": "ZIP Accrual Processing", "owner": "ZIP Agent", "status": "In Progress"},
        {"day": "BD1", "date": "Nov 28", "task": "Payroll Recon (15th)", "owner": "Payroll Agent", "status": "Complete"},
        {"day": "BD1", "date": "Nov 28", "task": "Post BD1 Accruals", "owner": "JE Agent", "status": "Complete"},
        {"day": "BD2", "date": "Nov 29", "task": "Equity Processing", "owner": "Equity Agent", "status": "Pending"},
        {"day": "BD3", "date": "Dec 2", "task": "Post BD3 Accruals", "owner": "JE Agent", "status": "Pending"},
        {"day": "BD3", "date": "Dec 2", "task": "Final Payroll Recon", "owner": "Payroll Agent", "status": "Pending"},
        {"day": "BD4", "date": "Dec 3", "task": "Final Review", "owner": "Controller", "status": "Pending"},
    ]
    
    df = pd.DataFrame(tasks)
    
    # Filter by status
    status_filter = st.multiselect(
        "Filter by status",
        ["Pending", "In Progress", "Complete", "Error"],
        default=["Pending", "In Progress"]
    )
    
    filtered_df = df[df["status"].isin(status_filter)]
    
    # Display calendar
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "status": st.column_config.TextColumn(
                "Status",
                help="Current task status"
            )
        }
    )
    
    # Timeline visualization
    st.subheader("Timeline")
    st.progress(0.42, text="42% Complete - BD3 of Close")

elif page == "⚙️ Workflows":
    st.markdown('<div class="main-header">Workflow Execution</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["ZIP Accrual", "Payroll Reconciliation", "Equity Processing"])
    
    with tab1:
        st.subheader("ZIP Accrual Processing")
        
        with st.form("zip_accrual_form"):
            close_date = st.date_input("Close Date", value=datetime(2025, 11, 30))
            subsidiary = st.selectbox("Subsidiary", ["Gusto US", "Gusto Canada"])
            zip_file = st.file_uploader("Upload ZIP Export CSV", type=["csv"])
            
            submitted = st.form_submit_button("Start Workflow", type="primary")
            
            if submitted:
                with st.spinner("Running ZIP Accrual Agent..."):
                    st.success("Workflow started successfully!")
                    
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    import time
                    steps = [
                        "Extracting ZIP invoices...",
                        "Fetching NetSuite bills...",
                        "Identifying service periods...",
                        "Calculating accruals...",
                        "Generating journal entries...",
                        "Validating entries...",
                        "Creating approval request..."
                    ]
                    
                    for i, step in enumerate(steps):
                        status_text.text(step)
                        progress_bar.progress((i + 1) / len(steps))
                        time.sleep(0.5)
                    
                    st.success("✅ Workflow complete! Approval request created.")
                    
                    # Show results
                    st.subheader("Results")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Invoices Processed", "12")
                    with col2:
                        st.metric("Total Accrual", "$47,500")
                    with col3:
                        st.metric("JE Lines", "8")
    
    with tab2:
        st.subheader("Payroll Reconciliation")
        st.info("Configure and run payroll reconciliation workflow")
    
    with tab3:
        st.subheader("Equity Transaction Processing")
        st.info("Configure and run equity processing workflow")

elif page == "✅ Approvals":
    st.markdown('<div class="main-header">Approval Queue</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Human-in-the-Loop Review</div>', unsafe_allow_html=True)
    
    # Approval requests
    approvals = [
        {
            "id": "REQ-20251122-001",
            "workflow": "Payroll Reconciliation",
            "created": "2 hours ago",
            "variances": 2,
            "amount": "$1,200",
            "status": "Pending Review"
        },
        {
            "id": "REQ-20251121-005",
            "workflow": "ZIP Accrual",
            "created": "Yesterday",
            "variances": 0,
            "amount": "$47,500",
            "status": "Pending Review"
        }
    ]
    
    for approval in approvals:
        with st.expander(f"**{approval['id']}** - {approval['workflow']} - {approval['created']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Material Variances", approval['variances'])
            with col2:
                st.metric("Total Amount", approval['amount'])
            with col3:
                st.markdown(f"**Status:** {approval['status']}")
            
            st.divider()
            
            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                if st.button("✅ Approve", key=f"approve_{approval['id']}", type="primary"):
                    st.success(f"Approved {approval['id']}")
            with col2:
                if st.button("❌ Reject", key=f"reject_{approval['id']}"):
                    st.error(f"Rejected {approval['id']}")

elif page == "📊 Reports":
    st.markdown('<div class="main-header">Reports & Analytics</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Performance", "Audit Trail", "Trends"])
    
    with tab1:
        st.subheader("Workflow Performance")
        
        import pandas as pd
        import plotly.express as px
        
        # Time savings chart
        data = pd.DataFrame({
            "Workflow": ["ZIP Accrual", "Payroll Recon", "Equity Processing"],
            "Manual Time (hrs)": [2.5, 1.5, 1.0],
            "Automated Time (hrs)": [0.25, 0.33, 0.17]
        })
        
        fig = px.bar(data, x="Workflow", y=["Manual Time (hrs)", "Automated Time (hrs)"],
                     title="Time Savings by Workflow", barmode="group")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Audit Trail")
        st.info("Complete audit trail of all workflow executions")
    
    with tab3:
        st.subheader("Trend Analysis")
        st.info("Historical trends and analytics")

elif page == "⚙️ Settings":
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["System", "Users", "Integrations"])
    
    with tab1:
        st.subheader("System Configuration")
        
        st.text_input("Close Date Format", value="YYYY-MM-DD")
        st.number_input("Materiality Threshold ($)", value=1000, step=100)
        st.selectbox("Default Subsidiary", ["Gusto US", "Gusto Canada", "Zero Payment Routing"])
        
        if st.button("Save Settings", type="primary"):
            st.success("Settings saved successfully!")
    
    with tab2:
        st.subheader("User Management")
        st.info("Manage users and roles")
    
    with tab3:
        st.subheader("System Integrations")
        
        integrations = [
            {"name": "NetSuite", "status": "Connected", "color": "green"},
            {"name": "Google Drive", "status": "Connected", "color": "green"},
            {"name": "Workday", "status": "Not Configured", "color": "orange"},
            {"name": "ShareWorks", "status": "Not Configured", "color": "orange"}
        ]
        
        for integration in integrations:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{integration['name']}**")
            with col2:
                if integration['color'] == 'green':
                    st.success(integration['status'])
                else:
                    st.warning(integration['status'])
            with col3:
                st.button("Configure", key=f"config_{integration['name']}")
