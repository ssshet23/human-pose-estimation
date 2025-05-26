import streamlit as st
from database import authenticate_user, register_user

def login_page():
    """Login page with secure authentication"""
    st.markdown('<div class="dark-title"><h1>Welcome to Human Pose Estimation 🏋️</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://deeplobe.ai/wp-content/uploads/2023/04/Deeplobe-Pose-Detection-Yoga-Image-1024x683.png", 
                    width=500)
        with col2:
            st.markdown('<div class="exercise-title"><h3>Login to Your Account</h3></div>', unsafe_allow_html=True)
            username = st.text_input("👤 Username")
            password = st.text_input("🔒 Password", type="password")
            
            if st.button("Login", key="login_btn"):
                if authenticate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            
            st.markdown("---")
            st.markdown("Don't have an account?")
            if st.button("Register Now", key="go_to_register"):
                st.session_state.register_mode = True
                st.rerun()

def register_page():
    """Secure user registration page"""
    st.markdown('<div class="dark-title"><h1>Create Your Account 🏆</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://quickpose.ai/wp-content/uploads/2023/03/What-is-Human-Pose-Estimation-QuickPose.png", 
                    width=500)
        with col2:
            st.markdown('<div class="exercise-title"><h3>Account Registration</h3></div>', unsafe_allow_html=True)
            username = st.text_input("👤 Choose a username")
            password = st.text_input("🔒 Choose a password", type="password")
            confirm_password = st.text_input("🔒 Confirm password", type="password")
            
            if st.button("Register", key="register_btn"):
                if password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                elif register_user(username, password):
                    st.success("Account created! Please login.")
                    st.session_state.register_mode = False
                    st.rerun()
                else:
                    st.error("Username already exists")
            
            st.markdown("---")
            st.markdown("Already have an account?")
            if st.button("Back to Login", key="go_to_login"):
                st.session_state.register_mode = False
                st.rerun()