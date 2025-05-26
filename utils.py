import math
import streamlit as st

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    ang = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
    return ang + 360 if ang < 0 else ang

def calculate_distance(a, b):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

def set_page_config():
    st.set_page_config(
        page_title="Human Pose Estimation",
        page_icon="💪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
        .main { background-color: #9c8572; }
        .dark-title {
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .exercise-title {
            background-color: #34495e;
            color: white;
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
            font-weight: bold;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #45a049;
            transform: scale(1.02);
        }
        .exercise-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .counter-display {
            font-size: 2rem;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            margin: 20px 0;
            padding: 10px;
            background: #e8f5e9;
            border-radius: 10px;
        }
        .webcam-container {
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 10px;
            margin-top: 20px;
        }
        .feedback-good {
            color: #4CAF50;
            font-weight: bold;
        }
        .feedback-warning {
            color: #FF9800;
            font-weight: bold;
        }
        .feedback-bad {
            color: #F44336;
            font-weight: bold;
        }
        .pose-feedback {
            font-size: 1.5rem;
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
        }
        .category-tabs {
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)