import streamlit as st
from dashboard import dashboard_page
from data import load_main_data
from material_search import material_search_page
from notification import notification_page

# Page configuration
st.set_page_config(page_title="Material Management", page_icon="🏭", layout="wide")

# Custom CSS for better appearance
st.markdown("""
<style>
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
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
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
        st.session_state.current_page = "Material Search"
    
    # Sidebar navigation
    with st.sidebar:
        st.title("InvOptima")
        
        if st.button("📊 Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()

        if st.button("🔍 Material Search"):
            st.session_state.current_page = "Material Search"
            st.session_state.show_details = False
            st.rerun()

        if st.button("📊 Notification"):
            st.session_state.current_page = "Notification"
            st.rerun()
        
        st.markdown("---")
    
    # Page routing
    if st.session_state.current_page == "Dashboard":
        dashboard_page()
    elif st.session_state.current_page == "Material Search":
        material_search_page()
    elif st.session_state.current_page == "Notification":
        notification_page()

if __name__ == "__main__":
    main()