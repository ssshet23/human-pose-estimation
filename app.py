import streamlit as st
import cv2
import mediapipe as mp
import math
import sqlite3
import os
import time
from hashlib import sha256
from datetime import datetime

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Database Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def initialize_database():
    """Initialize the database with secure tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get a secure database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt=None):
    """Hash password with salt using SHA-256"""
    salt = salt or os.urandom(16).hex()
    return sha256((password + salt).encode()).hexdigest(), salt

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

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    ang = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
    return ang + 360 if ang < 0 else ang

def calculate_distance(a, b):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

def authenticate_user(username, password):
    """Secure user authentication with hashed passwords"""
    try:
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        ).fetchone()
        
        if user:
            input_hash = sha256((password + user['salt']).encode()).hexdigest()
            if input_hash == user['password_hash']:
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), user['id'])
                )
                conn.commit()
                return True
        return False
    except sqlite3.Error as e:
        st.error(f"Authentication error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def register_user(username, password):
    """Secure user registration with password hashing"""
    try:
        conn = get_db_connection()
        
        if conn.execute(
            "SELECT 1 FROM users WHERE username = ?", 
            (username,)
        ).fetchone():
            return False
            
        password_hash, salt = hash_password(password)
        
        conn.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Registration error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def users_exist():
    """Check if any users exist in database"""
    try:
        conn = get_db_connection()
        return conn.execute("SELECT 1 FROM users").fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        if conn:
            conn.close()

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

def pose_estimation_page():
    """Main pose estimation interface"""
    st.markdown(f'<div class="dark-title"><h1>Hello, {st.session_state.username}! 👋</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Category selection
    category = st.radio("Select Category:", ["Exercise", "Yoga"], horizontal=True, key="category_selector")
    
    if category == "Exercise":
        exercise_page()
    else:
        yoga_page()

def exercise_page():
    """Exercise category page"""
    with st.container():
        st.markdown('<div class="exercise-title"><h3>🏋️ Choose Your Exercise</h3></div>', unsafe_allow_html=True)
        exercise = st.selectbox("", ["Squats", "Hand Raises", "Push-ups", "Lunges", "Bicep Curls", 
                                  "Jumping Jacks", "Shoulder Press", "Plank"], key="exercise_select")
        st.markdown(f"<div class='exercise-card'>"
                   f"<h4>Current Exercise: {exercise}</h4>"
                   f"<p>Follow the on-screen guidance</p></div>", 
                   unsafe_allow_html=True)
    
    # Initialize session variables
    if 'counter' not in st.session_state:
        st.session_state.counter = 0
    if 'webcam_active' not in st.session_state:
        st.session_state.webcam_active = False
    if 'exercise_stage' not in st.session_state:
        st.session_state.exercise_stage = "start"
    
    st.markdown(f"<div class='counter-display'>"
               f"Rep Count: {st.session_state.counter}"
               f"</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎥 Start Webcam" if not st.session_state.webcam_active else "🛑 Stop Webcam", key="webcam_toggle"):
            st.session_state.webcam_active = not st.session_state.webcam_active
    with col2:
        if st.button("🔁 Reset Counter", key="reset_counter"):
            st.session_state.counter = 0
            st.session_state.exercise_stage = "start"
            st.success("Counter reset!")
    with col3:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.success("Logged out successfully!")
            st.rerun()
    
    if st.session_state.webcam_active:
        process_exercise_feed(exercise)

def yoga_page():
    """Yoga category page"""
    with st.container():
        st.markdown('<div class="exercise-title"><h3>🧘 Choose Your Yoga Pose</h3></div>', unsafe_allow_html=True)
        yoga_pose = st.selectbox("", ["Tree Pose", "Warrior II", "Downward Dog", "Cobra Pose", 
                                    "Bridge Pose", "Child's Pose", "Mountain Pose", "Cat-Cow", "Easy Pose", "Seated Forward Bend", "Legs-Up-the-Wall"], key="yoga_select")
        st.markdown(f"<div class='exercise-card'>"
                   f"<h4>Current Pose: {yoga_pose}</h4>"
                   f"<p>Hold the pose and check your form</p></div>", 
                   unsafe_allow_html=True)
    
    if 'webcam_active' not in st.session_state:
        st.session_state.webcam_active = False
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎥 Start Webcam" if not st.session_state.webcam_active else "🛑 Stop Webcam", key="yoga_webcam"):
            st.session_state.webcam_active = not st.session_state.webcam_active
    with col2:
        if st.button("🚪 Logout", key="yoga_logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.success("Logged out successfully!")
            st.rerun()
    
    if st.session_state.webcam_active:
        process_yoga_feed(yoga_pose)

def process_exercise_feed(exercise):
    """Process real-time webcam feed for exercises"""
    st.markdown("---")
    st.markdown('<div class="exercise-title"><h3>🎥 Live Exercise Detection</h3></div>', unsafe_allow_html=True)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    video_placeholder = st.empty()

    while st.session_state.webcam_active:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera error")
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            if exercise == "Squats":
                process_squats(results.pose_landmarks, image)
            elif exercise == "Hand Raises":
                process_hand_raises(results.pose_landmarks, image)
            elif exercise == "Push-ups":
                process_pushups(results.pose_landmarks, image)
            elif exercise == "Lunges":
                process_lunges(results.pose_landmarks, image)
            elif exercise == "Bicep Curls":
                process_bicep_curls(results.pose_landmarks, image)
            elif exercise == "Jumping Jacks":
                process_jumping_jacks(results.pose_landmarks, image)
            elif exercise == "Shoulder Press":
                process_shoulder_press(results.pose_landmarks, image)
            elif exercise == "Plank":
                process_plank(results.pose_landmarks, image)

            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.putText(image, f"Reps: {st.session_state.counter}", (10, 30),
                    cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 2)

        video_placeholder.image(image, channels="BGR")

    cap.release()

    

def process_yoga_feed(yoga_pose):
    """Process real-time webcam feed for yoga poses"""
    st.markdown("---")
    st.markdown('<div class="exercise-title"><h3>🎥 Live Pose Feedback</h3></div>', unsafe_allow_html=True)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    video_placeholder = st.empty()
    feedback_placeholder = st.empty()
    
    while st.session_state.webcam_active:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera error")
            break
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        feedback = ""
        if results.pose_landmarks:
            if yoga_pose == "Tree Pose":
                feedback = check_tree_pose(results.pose_landmarks, image)
            elif yoga_pose == "Warrior II":
                feedback = check_warrior_ii(results.pose_landmarks, image)
            elif yoga_pose == "Downward Dog":
                feedback = check_downward_dog(results.pose_landmarks, image)
            elif yoga_pose == "Cobra Pose":
                feedback = check_cobra_pose(results.pose_landmarks, image)
            elif yoga_pose == "Bridge Pose":
                feedback = check_bridge_pose(results.pose_landmarks, image)
            elif yoga_pose == "Child's Pose":
                feedback = check_childs_pose(results.pose_landmarks, image)
            elif yoga_pose == "Mountain Pose":
                feedback = check_mountain_pose(results.pose_landmarks, image)
            elif yoga_pose == "Cat-Cow":
                feedback = check_cat_cow_pose(results.pose_landmarks, image)
            elif yoga_pose == "Easy Pose":
                feedback = check_easy_pose(results.pose_landmarks, image)
            elif yoga_pose == "Seated Forward Bend":
                feedback = check_seated_forward_bend(results.pose_landmarks, image)
            elif yoga_pose == "Legs-Up-the-Wall":
                feedback = check_legs_up_wall(results.pose_landmarks, image)
            
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Display feedback
        if feedback:
            if "GOOD" in feedback:
                feedback_placeholder.markdown(f'<div class="pose-feedback" style="background-color:#e8f5e9;color:#4CAF50;">{feedback}</div>', unsafe_allow_html=True)
            else:
                feedback_placeholder.markdown(f'<div class="pose-feedback" style="background-color:#ffebee;color:#F44336;">{feedback}</div>', unsafe_allow_html=True)
        
        video_placeholder.image(image, channels="BGR")
        
       #if cv2.waitKey(1) & 0xFF == ord('q'):
         #  break

    cap.release()
   #cv2.destroyAllWindows()

# ===== EXERCISE PROCESSING FUNCTIONS =====

def process_squats(landmarks, image):
    """Process squats exercise"""
    try:
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
        
        if avg_knee_angle > 160:
            st.session_state.exercise_stage = "up"
            
        if avg_knee_angle < 90 and st.session_state.exercise_stage == "up":
            st.session_state.exercise_stage = "down"
            st.session_state.counter += 1
            cv2.putText(image, "REP COUNTED!", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
        
        if st.session_state.exercise_stage == "up":
            cv2.putText(image, "BEND KNEES TO SQUAT", (image.shape[1]//2 - 150, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
        else:
            cv2.putText(image, "STAND UP", (image.shape[1]//2 - 70, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    except Exception as e:
        st.error(f"Squats processing error: {e}")

def process_hand_raises(landmarks, image):
    """Process hand raises exercise"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        
        avg_wrist_height = (left_wrist.y + right_wrist.y) / 2
        avg_shoulder_height = (left_shoulder.y + right_shoulder.y) / 2
        
        if avg_wrist_height > avg_shoulder_height + 0.05:
            st.session_state.exercise_stage = "down"
            
        if avg_wrist_height < avg_shoulder_height - 0.05 and st.session_state.exercise_stage == "down":
            st.session_state.exercise_stage = "up"
            st.session_state.counter += 1
            cv2.putText(image, "REP COUNTED!", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
        
        if st.session_state.exercise_stage == "down":
            cv2.putText(image, "RAISE YOUR HANDS", (image.shape[1]//2 - 120, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
        else:
            cv2.putText(image, "LOWER YOUR HANDS", (image.shape[1]//2 - 130, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    except Exception as e:
        st.error(f"Hand raises processing error: {e}")

def process_pushups(landmarks, image):
    """Process push-ups exercise with improved detection"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        
        # Get hip landmarks (added these lines)
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        # Calculate elbow angles
        left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        # Calculate shoulder angles (using hips as the third point)
        left_shoulder_angle = calculate_angle(left_elbow, left_shoulder, left_hip)
        right_shoulder_angle = calculate_angle(right_elbow, right_shoulder, right_hip)
        
        # Get average angles
        avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2
        avg_shoulder_angle = (left_shoulder_angle + right_shoulder_angle) / 2
        
        # Push-up logic
        if avg_elbow_angle > 160 and avg_shoulder_angle > 160:
            st.session_state.exercise_stage = "up"
            
        if avg_elbow_angle < 70 and st.session_state.exercise_stage == "up":
            st.session_state.exercise_stage = "down"
            st.session_state.counter += 1
            cv2.putText(image, "REP COUNTED!", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
        
        # Visual feedback
        if st.session_state.exercise_stage == "up":
            cv2.putText(image, "LOWER YOUR BODY", (image.shape[1]//2 - 120, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            cv2.putText(image, f"Elbow Angle: {int(avg_elbow_angle)}°", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            cv2.putText(image, "PUSH UP", (image.shape[1]//2 - 70, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(image, f"Elbow Angle: {int(avg_elbow_angle)}°", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw angles on frame for debugging
        cv2.putText(image, f"L Elbow: {int(left_elbow_angle)}°", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(image, f"R Elbow: {int(right_elbow_angle)}°", 
                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    except Exception as e:
        st.error(f"Push-ups processing error: {e}")

def process_lunges(landmarks, image):
    """Process lunges exercise"""
    try:
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        if left_knee_angle > 160 and right_knee_angle > 160:
            st.session_state.exercise_stage = "up"
            
        if (left_knee_angle < 90 or right_knee_angle < 90) and st.session_state.exercise_stage == "up":
            st.session_state.exercise_stage = "down"
            st.session_state.counter += 1
            cv2.putText(image, "REP COUNTED!", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
        
        if st.session_state.exercise_stage == "up":
            cv2.putText(image, "STEP FORWARD INTO LUNGE", (image.shape[1]//2 - 180, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        else:
            cv2.putText(image, "RETURN TO START", (image.shape[1]//2 - 120, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    except Exception as e:
        st.error(f"Lunges processing error: {e}")

def process_bicep_curls(landmarks, image):
    """Process bicep curls exercise"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        
        left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        if left_elbow_angle > 160 and right_elbow_angle > 160:
            st.session_state.exercise_stage = "down"
            
        if (left_elbow_angle < 50 or right_elbow_angle < 50) and st.session_state.exercise_stage == "down":
            st.session_state.exercise_stage = "up"
            st.session_state.counter += 1
            cv2.putText(image, "REP COUNTED!", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
        
        if st.session_state.exercise_stage == "down":
            cv2.putText(image, "CURL YOUR ARMS UP", (image.shape[1]//2 - 140, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
        else:
            cv2.putText(image, "LOWER YOUR ARMS", (image.shape[1]//2 - 120, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    except Exception as e:
        st.error(f"Bicep curls processing error: {e}")

def process_jumping_jacks(landmarks, image):
    """Process jumping jacks exercise"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        
        wrist_distance = calculate_distance(left_wrist, right_wrist)
        hip_distance = calculate_distance(left_hip, right_hip)
        
        if wrist_distance < 0.2 and hip_distance < 0.2:
            st.session_state.exercise_stage = "closed"
            
        if wrist_distance > 0.4 and hip_distance > 0.3 and st.session_state.exercise_stage == "closed":
            st.session_state.exercise_stage = "open"
            st.session_state.counter += 1
            cv2.putText(image, "REP COUNTED!", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
        
        if st.session_state.exercise_stage == "closed":
            cv2.putText(image, "JUMP ARMS AND LEGS OUT", (image.shape[1]//2 - 180, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        else:
            cv2.putText(image, "JUMP ARMS AND LEGS IN", (image.shape[1]//2 - 170, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    except Exception as e:
        st.error(f"Jumping jacks processing error: {e}")

def process_shoulder_press(landmarks, image):
    """Simplified shoulder press detection - counts reps more easily"""
    try:
        # Get key landmarks
        left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        # Simple vertical movement detection
        avg_wrist_height = (left_wrist.y + right_wrist.y)/2
        avg_elbow_height = (left_elbow.y + right_elbow.y)/2
        
        # Rep counting logic
        if avg_wrist_height > avg_elbow_height + 0.1:  # Hands below elbows
            st.session_state.exercise_stage = "down"
            
        if avg_wrist_height < avg_elbow_height - 0.1 and st.session_state.exercise_stage == "down":
            st.session_state.exercise_stage = "up"
            st.session_state.counter += 1
            cv2.putText(image, "REP COUNTED!", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Simple visual feedback
        cv2.putText(image, f"Reps: {st.session_state.counter}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(image, "PRESS UP" if st.session_state.exercise_stage == "down" else "LOWER DOWN", 
                   (image.shape[1]//2 - 80, image.shape[0] - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    except Exception as e:
        st.error(f"Shoulder press error: {e}")
            
def process_plank(landmarks, image):
    """Plank exercise with persistent total time display"""
    try:
        # Get key landmarks
        shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]

        # Calculate angles
        body_angle = calculate_angle(shoulder, hip, knee)
        elbow_angle = calculate_angle(shoulder, elbow, wrist)

        # Form verification (lenient)
        is_plank = (wrist.y > elbow.y) and (60 < elbow_angle < 150) and (150 < body_angle < 210)

        # Initialize session variables
        if 'total_plank_time' not in st.session_state:
            st.session_state.total_plank_time = 0
        if 'last_plank_end' not in st.session_state:
            st.session_state.last_plank_end = 0
        if 'show_total_time' not in st.session_state:
            st.session_state.show_total_time = False

        # When in plank position
        if is_plank:
            if 'plank_start_time' not in st.session_state:
                st.session_state.plank_start_time = time.time()
                st.session_state.show_total_time = False
            
            hold_time = time.time() - st.session_state.plank_start_time
            cv2.putText(image, f"CURRENT: {int(hold_time)}s", (image.shape[1]//2 - 100, 50), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show total time in smaller font below current time
            cv2.putText(image, f"TOTAL: {int(st.session_state.total_plank_time)}s", 
                       (image.shape[1]//2 - 80, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            
        # When breaking plank position
        else:
            if 'plank_start_time' in st.session_state:
                # Add to total time
                st.session_state.total_plank_time += time.time() - st.session_state.plank_start_time
                st.session_state.last_plank_end = time.time()
                st.session_state.show_total_time = True
                del st.session_state.plank_start_time

            # Show total time for 3 seconds after breaking plank
            if st.session_state.show_total_time and (time.time() - st.session_state.last_plank_end < 3):
                cv2.putText(image, f"TOTAL TIME: {int(st.session_state.total_plank_time)}s", 
                           (image.shape[1]//2 - 120, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
                cv2.putText(image, "Great effort!", (image.shape[1]//2 - 100, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
            else:
                st.session_state.show_total_time = False

            # Form feedback
            cv2.putText(image, "Get ready for next plank!", (image.shape[1]//2 - 150, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    except Exception as e:
        st.error(f"Error tracking plank: {e}")

# ===== YOGA POSE CHECKING FUNCTIONS =====

def check_tree_pose(landmarks, image):
    """Check Tree Pose form"""
    try:
        left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        foot_near_knee = (abs(left_ankle.x - right_knee.x) < 0.05 and 
                         abs(left_ankle.y - right_knee.y) < 0.1)
        balanced = abs(left_hip.y - right_hip.y) < 0.05
        
        if foot_near_knee and balanced:
            cv2.putText(image, "GOOD TREE POSE", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD TREE POSE FORM! 👍"
        else:
            feedback = []
            if not foot_near_knee:
                cv2.putText(image, "PLACE FOOT NEAR KNEE", (image.shape[1]//2 - 150, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Place foot near knee")
            if not balanced:
                cv2.putText(image, "KEEP HIPS LEVEL", (image.shape[1]//2 - 120, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Keep hips level")
            return "ADJUST YOUR POSE: " + ", ".join(feedback)
    
    except Exception as e:
        st.error(f"Tree Pose check error: {e}")
        return ""

def check_warrior_ii(landmarks, image):
    """Check Warrior II pose form"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        
        # Check front knee angle (should be ~90 degrees)
        front_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        good_knee_angle = 80 < front_knee_angle < 100
        
        # Check arm alignment (should be straight line shoulder to wrist)
        arm_alignment = abs(left_shoulder.y - right_shoulder.y) < 0.05
        
        # Check hips facing sideways
        hips_alignment = abs(left_hip.x - right_hip.x) > 0.2
        
        if good_knee_angle and arm_alignment and hips_alignment:
            cv2.putText(image, "GOOD WARRIOR II", (image.shape[1]//2 - 120, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD WARRIOR II FORM! 👍"
        else:
            feedback = []
            if not good_knee_angle:
                cv2.putText(image, f"BEND FRONT KNEE MORE ({int(front_knee_angle)}°)", 
                           (image.shape[1]//2 - 180, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Bend front knee to 90°")
            if not arm_alignment:
                cv2.putText(image, "STRETCH ARMS STRAIGHT", (image.shape[1]//2 - 150, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Align arms straight")
            if not hips_alignment:
                cv2.putText(image, "FACE HIPS SIDEWAYS", (image.shape[1]//2 - 130, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Turn hips sideways")
            return "ADJUST YOUR POSE: " + ", ".join(feedback)
    
    except Exception as e:
        st.error(f"Warrior II check error: {e}")
        return ""
def check_downward_dog(landmarks, image):
    """Check Downward Dog pose form"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        
        # Check if hips are higher than shoulders
        hips_higher = (left_hip.y + right_hip.y)/2 < (left_shoulder.y + right_shoulder.y)/2
        # Check if legs are straight
        left_leg_angle = calculate_angle(left_hip, left_knee, landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value])
        right_leg_angle = calculate_angle(right_hip, right_knee, landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE.value])
        legs_straight = left_leg_angle > 160 and right_leg_angle > 160
        
        if hips_higher and legs_straight:
            cv2.putText(image, "GOOD DOWNWARD DOG", (image.shape[1]//2 - 150, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD DOWNWARD DOG FORM! 👍"
        else:
            feedback = []
            if not hips_higher:
                cv2.putText(image, "LIFT HIPS HIGHER", (image.shape[1]//2 - 120, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Lift hips higher")
            if not legs_straight:
                cv2.putText(image, "STRAIGHTEN LEGS", (image.shape[1]//2 - 130, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Straighten legs")
            return "ADJUST YOUR POSE: " + ", ".join(feedback)
    
    except Exception as e:
        st.error(f"Downward Dog check error: {e}")
        return ""

def check_cobra_pose(landmarks, image):
    """Check Cobra Pose form"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        
        # Check if shoulders are lifted
        shoulders_lifted = (left_shoulder.y + right_shoulder.y)/2 < 0.6
        # Check if elbows are slightly bent
        left_arm_angle = calculate_angle(
            landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value],
            left_elbow,
            left_shoulder
        )
        right_arm_angle = calculate_angle(
            landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value],
            right_elbow,
            right_shoulder
        )
        arms_bent = 140 < left_arm_angle < 170 and 140 < right_arm_angle < 170
        
        if shoulders_lifted and arms_bent:
            cv2.putText(image, "GOOD COBRA POSE", (image.shape[1]//2 - 120, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD COBRA POSE FORM! 👍"
        else:
            feedback = []
            if not shoulders_lifted:
                cv2.putText(image, "LIFT CHEST HIGHER", (image.shape[1]//2 - 140, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Lift chest higher")
            if not arms_bent:
                cv2.putText(image, "BEND ARMS SLIGHTLY", (image.shape[1]//2 - 150, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Bend arms slightly")
            return "ADJUST YOUR POSE: " + ", ".join(feedback)
    
    except Exception as e:
        st.error(f"Cobra Pose check error: {e}")
        return ""

def check_bridge_pose(landmarks, image):
    """Check Bridge Pose form"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        
        # Check if hips are lifted
        hips_lifted = (left_hip.y + right_hip.y)/2 < (left_shoulder.y + right_shoulder.y)/2
        # Check knee angles
        left_knee_angle = calculate_angle(left_hip, left_knee, landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value])
        right_knee_angle = calculate_angle(right_hip, right_knee, landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE.value])
        knees_bent = 100 < left_knee_angle < 120 and 100 < right_knee_angle < 120
        
        if hips_lifted and knees_bent:
            cv2.putText(image, "GOOD BRIDGE POSE", (image.shape[1]//2 - 130, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD BRIDGE POSE FORM! 👍"
        else:
            feedback = []
            if not hips_lifted:
                cv2.putText(image, "LIFT HIPS HIGHER", (image.shape[1]//2 - 120, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Lift hips higher")
            if not knees_bent:
                cv2.putText(image, "ADJUST KNEE ANGLES", (image.shape[1]//2 - 150, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Adjust knee angles")
            return "ADJUST YOUR POSE: " + ", ".join(feedback)
    
    except Exception as e:
        st.error(f"Bridge Pose check error: {e}")
        return ""

def check_childs_pose(landmarks, image):
    """Check Child's Pose form"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        # Check if hips are close to heels (approximation)
        hips_low = (left_hip.y + right_hip.y)/2 > 0.8
        # Check if arms are extended forward
        left_arm_angle = calculate_angle(
            left_shoulder,
            landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value],
            landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
        )
        right_arm_angle = calculate_angle(
            right_shoulder,
            landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
            landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        )
        arms_extended = left_arm_angle > 150 and right_arm_angle > 150
        
        if hips_low and arms_extended:
            cv2.putText(image, "GOOD CHILD'S POSE", (image.shape[1]//2 - 140, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD CHILD'S POSE FORM! 👍"
        else:
            feedback = []
            if not hips_low:
                cv2.putText(image, "SINK HIPS LOWER", (image.shape[1]//2 - 120, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Sink hips lower")
            if not arms_extended:
                cv2.putText(image, "EXTEND ARMS FORWARD", (image.shape[1]//2 - 160, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Extend arms forward")
            return "ADJUST YOUR POSE: " + ", ".join(feedback)
    
    except Exception as e:
        st.error(f"Child's Pose check error: {e}")
        return ""
def check_mountain_pose(landmarks, image):
    """Check Mountain Pose (Tadasana) form"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        
        # Check body alignment
        left_alignment = abs(left_shoulder.x - left_hip.x) < 0.05 and abs(left_hip.x - left_ankle.x) < 0.05
        right_alignment = abs(right_shoulder.x - right_hip.x) < 0.05 and abs(right_hip.x - right_ankle.x) < 0.05
        balanced = left_alignment and right_alignment
        
        if balanced:
            cv2.putText(image, "GOOD MOUNTAIN POSE", (image.shape[1]//2 - 150, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD MOUNTAIN POSE FORM! 👍"
        else:
            feedback = []
            if not left_alignment or not right_alignment:
                cv2.putText(image, "ALIGN SHOULDERS OVER HIPS", (image.shape[1]//2 - 180, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                feedback.append("Align shoulders over hips")
            return "ADJUST YOUR POSE: " + ", ".join(feedback)
    
    except Exception as e:
        st.error(f"Mountain Pose check error: {e}")
        return ""

def check_cat_cow_pose(landmarks, image):
    """Check Cat-Cow Pose form"""
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        # Calculate spine curvature
        shoulder_hip_angle = calculate_angle(left_shoulder, left_hip, right_hip)
        
        if shoulder_hip_angle < 160:  # Cat pose (rounded back)
            cv2.putText(image, "CAT POSE DETECTED", (image.shape[1]//2 - 120, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD CAT POSE! Now arch your back for Cow Pose"
        elif shoulder_hip_angle > 170:  # Cow pose (arched back)
            cv2.putText(image, "COW POSE DETECTED", (image.shape[1]//2 - 120, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD COW POSE! Now round your back for Cat Pose"
        else:
            cv2.putText(image, "TRANSITION BETWEEN POSES", (image.shape[1]//2 - 180, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            return "Move between Cat and Cow poses with your breath"
    
    except Exception as e:
        st.error(f"Cat-Cow Pose check error: {e}")
        return ""
def check_easy_pose(landmarks, image):
    """Easy Pose detector checking ankles, spine, and hand position"""
    try:
        # Get required landmarks
        left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]

        # 1. Check ankle crossing (lenient threshold)
        ankles_crossed = abs(left_ankle.x - right_ankle.x) < 0.25  # 25% of screen width
        
        # 2. Check spine straightness (shoulder over hip)
        spine_straight = abs(left_shoulder.x - left_hip.x) < 0.15
        
        # 3. Check hands on legs (wrists between knees and hips)
        hands_on_legs = (
            (left_wrist.y > left_knee.y) and 
            (left_wrist.y < left_hip.y) and
            (right_wrist.y > left_knee.y) and
            (right_wrist.y < left_hip.y)
        )

        # Only show feedback when all conditions are met
        if ankles_crossed and spine_straight and hands_on_legs:
            # Visual feedback elements
            cv2.putText(image, "✓ PERFECT POSTURE", (image.shape[1]//2 - 120, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 100), 2)
            
            cv2.putText(image, "Ankles crossed", (30, image.shape[0] - 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 1)
            
            cv2.putText(image, "Spine tall", (30, image.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 1)
            
            cv2.putText(image, "Hands resting", (30, image.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 1)
            
            # Gentle breathing reminder
            cv2.putText(image, "Breathe deeply...", (image.shape[1]//2 - 80, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 200), 1)
            
            return "Ideal meditation posture"

        # No feedback when not in perfect position
        return ""

    except Exception as e:
        st.error(f"Detection error: {e}")
        return ""

def check_seated_forward_bend(landmarks, image):
    """Check Paschimottanasana (Seated Forward Bend) form"""
    try:
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        spine_angle = calculate_angle(
            landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
            left_hip,
            left_knee
        )

        if spine_angle < 120:  # Bent forward
            cv2.putText(image, "GOOD FORWARD BEND", (image.shape[1]//2 - 130, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD! Hinge from hips, not waist."
        else:
            cv2.putText(image, "FOLD FORWARD MORE", (image.shape[1]//2 - 140, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return f"ADJUST: Bend forward from hips (current angle: {int(spine_angle)}°)"
    except Exception as e:
        st.error(f"Forward Bend error: {e}")
        return ""

def check_legs_up_wall(landmarks, image):
    """Check Viparita Karani (Legs-Up-the-Wall) form"""
    try:
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE.value]

        # Check if legs are mostly vertical (simplified)
        legs_vertical = (left_knee.y < left_hip.y - 0.1) and (right_knee.y < right_hip.y - 0.1)

        if legs_vertical:
            cv2.putText(image, "GOOD LEGS-UP-THE-WALL", (image.shape[1]//2 - 180, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return "GOOD! Relax and breathe deeply."
        else:
            cv2.putText(image, "LIFT LEGS HIGHER", (image.shape[1]//2 - 120, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return "ADJUST: Extend legs upward (use a wall if needed)"
    except Exception as e:
        st.error(f"Legs-Up-the-Wall error: {e}")
        return ""
# ===== MAIN APPLICATION =====

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