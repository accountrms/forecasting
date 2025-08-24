import streamlit as st
from dashboard import dashboard_page
from material_search import material_search_page
from notification import notification_page
from tracking import tracking_page
from technical_analysis import tech_analysis

# Page configuration
st.set_page_config(page_title="Material Management", page_icon="🏭", layout="wide")

# Custom CSS for better appearance
st.markdown("""
<style>
    unsafe_allow_html=True
)
    .stTextInput input {
        font-size: 16px;
    }
    .dataframe {
        width: 100%;
    }
    .stSelectbox div {
        font-size: 16px;
    }
    .stButton button {
        background-color: #0a1172;
        color: white;
        font-weight: bold;
        width: 180px;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }
    .sidebar .sidebar-content {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Main App Controller (unchanged from your original)
def main():
    # Initialize session state for page navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "MAT Analysis"
    st.sidebar.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; padding: 20px 0;">
            <img src="https://udbhav.ongc.co.in/images/logo.png" width="150">
        </div>
        """,
        unsafe_allow_html=True
    )
    # Sidebar navigation
    with st.sidebar:
        st.title("InvOptima")
        
        if st.button("📊 Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()

        if st.button("🔍 MAT Analysis"):
            st.session_state.current_page = "MAT Analysis"
            st.session_state.show_details = False
            st.rerun()

        if st.button("📊 Notification"):
            st.session_state.current_page = "Notification"
            st.rerun()

        if st.button("📊 REQ Tracking"):
            st.session_state.current_page = "REQ Tracking"
            st.rerun()

        if st.button("📊 Technical Analysis"):
            st.session_state.current_page = "Technical Analysis"
            st.rerun()

        st.markdown("---")
    
    # Page routing
    if st.session_state.current_page == "Dashboard":
        dashboard_page()
    elif st.session_state.current_page == "MAT Analysis":
        material_search_page()
    elif st.session_state.current_page == "Notification":
        notification_page()
    elif st.session_state.current_page == "REQ Tracking":
        tracking_page()
    elif st.session_state.current_page == "Technical Analysis":
        tech_analysis()

if __name__ == "__main__":
    main()