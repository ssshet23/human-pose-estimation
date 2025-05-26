import streamlit as st
from auth import login_page, register_page
from database import initialize_database, users_exist
from utils import set_page_config

def pose_estimation_page():
    """Main pose estimation interface"""
    from exercises import exercise_page
    from yoga import yoga_page
    
    st.markdown(f'<div class="dark-title"><h1>Hello, {st.session_state.username}! 👋</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize session state variables if they don't exist
    if 'show_exercise_instructions' not in st.session_state:
        st.session_state.show_exercise_instructions = False
    if 'show_yoga_instructions' not in st.session_state:
        st.session_state.show_yoga_instructions = False
    
    # Category selection
    category = st.radio("Select Category:", ["Exercise", "Yoga"], horizontal=True, key="category_selector")

    if category == "Exercise":
        exercise_page()
    else:
        yoga_page()
        

def main():
    # Initialize the database
    initialize_database()
    
    # Set up page configuration
    set_page_config()
    
    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'register_mode' not in st.session_state:
        st.session_state.register_mode = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # Check if any users exist (first run)
    if not users_exist() and not st.session_state.register_mode:
        st.session_state.register_mode = True
    
    # Show appropriate page based on state
    if not st.session_state.logged_in:
        if st.session_state.register_mode:
            register_page()
        else:
            login_page()
    else:
        pose_estimation_page()

if __name__ == "__main__":
    main()