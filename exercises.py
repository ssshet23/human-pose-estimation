import cv2
import math
import time
import streamlit as st
import mediapipe as mp
from utils import calculate_angle, calculate_distance

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def exercise_page():
    """Exercise category page"""
    with st.container():
        st.markdown('<div class="exercise-title"><h3>🏋️ Choose Your Exercise</h3></div>', unsafe_allow_html=True)
        exercise = st.selectbox("", ["Squats", "Hand Raises", "Push-ups", "Lunges", "Bicep Curls", 
                                  "Jumping Jacks", "Shoulder Press", "Plank"], key="exercise_select")
        
        # Add a continue button
        if st.button("Continue", key="exercise_continue"):
            st.session_state.show_exercise_instructions = True
            st.session_state.selected_exercise = exercise
            st.rerun()
        
        # If we're not showing instructions, stop here
        if not st.session_state.get('show_exercise_instructions', False):
            return
            
        # Show exercise instructions page
        st.markdown(f"<div class='exercise-card'>"
                   f"<h2>{st.session_state.selected_exercise} Instructions</h2>"
                   f"</div>", unsafe_allow_html=True)
        
        # Add exercise-specific instructions and images
        show_exercise_instructions(st.session_state.selected_exercise)

def show_exercise_instructions(exercise):
    """Show instructions and image for the selected exercise"""
    # Dictionary mapping exercises to their instructions and image URLs
    exercise_data = {
        "Squats": {
            "image": "D:/code hpe/exercise/squat-exercise-men-workout-fitness-aerobic-and-exercises-vector.jpg",
            "instructions": [
                "Stand with feet shoulder-width apart",
                "Lower your body as if sitting in a chair",
                "Keep your back straight and knees behind toes",
                "Go as low as you can while maintaining form",
                "Push through your heels to return to standing"
            ]
        },
        "Push-ups": {
            "image": "https://www.verywellfit.com/thmb/0ZEDvIxr9j0wv5Z0YtYHwVn4XwM=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/push-up-06-722x1024-27a1c0f9a1f34b3c9b9d5b8a5d5b5b5b.jpg",
            "instructions": [
                "Start in a plank position with hands under shoulders",
                "Lower your body until chest nearly touches the floor",
                "Keep your body in a straight line",
                "Push back up to starting position",
                "Modify with knees down if needed"
            ]
        },
         "Hand Raises": {
        "image": "D:/code hpe/exercise/hand raise.jpg",
        "instructions": [
            "Stand tall with feet hip-width apart",
            "Hold arms straight down at your sides",
            "Slowly raise both arms straight out to the sides",
            "Lift until arms are parallel to the floor",
            "Lower back down with control",
            "Repeat for desired repetitions"
        ]
        },
          "Push-ups": {
        "image": "D:/code hpe/exercise/pushups.jpeg",
        "instructions": [
            "Start in a plank position with hands under shoulders",
            "Lower your body until chest nearly touches the floor",
            "Keep your body in a straight line",
            "Push back up to starting position",
            "Modify with knees down if needed"
        ]
    },
    "Lunges": {
        "image": "D:/code hpe/exercise/lunges.jpg",
        "instructions": [
            "Stand tall with feet together",
            "Step forward with one leg and lower your hips",
            "Bend both knees to about 90 degrees",
            "Keep front knee directly above ankle",
            "Push back up to starting position",
            "Alternate legs with each repetition"
        ]
    },
    "Bicep Curls": {
        "image": "exercise/bicep-curls.webp",
        "instructions": [
            "Stand holding dumbbells at your sides",
            "Keep elbows close to your torso",
            "Curl weights while contracting biceps",
            "Raise until dumbbells are at shoulder level",
            "Slowly lower back to starting position",
            "Maintain controlled movement throughout"
        ]
    },
     "Jumping Jacks": {
        "image": "D:/code hpe/exercise/jumping jacks.webp",
        "instructions": [
            "Stand with feet together and arms at sides",
            "Jump while spreading legs shoulder-width apart",
            "Simultaneously raise arms above head",
            "Quickly reverse the motion to return to start",
            "Land softly on the balls of your feet",
            "Maintain steady breathing throughout"
        ]
    },
    "Shoulder Press": {
        "image": "D:/code hpe/exercise/shoulder press.jpg",
        "instructions": [
            "Hold dumbbells at shoulder height",
            "Keep elbows at 90 degrees, palms forward",
            "Press weights upward until arms are straight",
            "Pause briefly at the top position",
            "Slowly lower back to starting position",
            "Keep core engaged throughout movement"
        ]
    },
    "Plank": {
        "image": "D:/code hpe/exercise/plankk.jpg",
        "instructions": [
            "Begin in push-up position on hands and toes",
            "Lower onto forearms, elbows under shoulders",
            "Keep body in straight line from head to heels",
            "Engage core and glutes to maintain position",
            "Hold for desired time (start with 20-30 seconds)",
            "Avoid letting hips sag or rise too high"
        ]
    }
    }
    
    # Get the data for the selected exercise
    data = exercise_data.get(exercise, {
        "image": "https://via.placeholder.com/500x300?text=Exercise+Image",
        "instructions": ["Detailed instructions coming soon!"]
    })
    
    # Display in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(data["image"], width=300, caption=exercise)
        
    with col2:
        st.markdown("**Instructions:**")
        for i, instruction in enumerate(data["instructions"], 1):
            st.markdown(f"{i}. {instruction}")
    
    # Add a back button
    if st.button("Back to Selection", key="exercise_back"):
        st.session_state.show_exercise_instructions = False
        st.rerun()
    
    # Add the webcam controls below the instructions
    st.markdown("---")
    initialize_exercise_tracking(exercise)

def initialize_exercise_tracking(exercise):
    """Initialize the exercise tracking section"""
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
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

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
        
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        left_shoulder_angle = calculate_angle(left_elbow, left_shoulder, left_hip)
        right_shoulder_angle = calculate_angle(right_elbow, right_shoulder, right_hip)
        
        avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2
        avg_shoulder_angle = (left_shoulder_angle + right_shoulder_angle) / 2
        
        if avg_elbow_angle > 160 and avg_shoulder_angle > 160:
            st.session_state.exercise_stage = "up"
            
        if avg_elbow_angle < 70 and st.session_state.exercise_stage == "up":
            st.session_state.exercise_stage = "down"
            st.session_state.counter += 1
            cv2.putText(image, "REP COUNTED!", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
        
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
        left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        avg_wrist_height = (left_wrist.y + right_wrist.y)/2
        avg_elbow_height = (left_elbow.y + right_elbow.y)/2
        
        if avg_wrist_height > avg_elbow_height + 0.1:
            st.session_state.exercise_stage = "down"
            
        if avg_wrist_height < avg_elbow_height - 0.1 and st.session_state.exercise_stage == "down":
            st.session_state.exercise_stage = "up"
            st.session_state.counter += 1
            cv2.putText(image, "REP COUNTED!", (image.shape[1]//2 - 100, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
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
        shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
        elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]

        body_angle = calculate_angle(shoulder, hip, knee)
        elbow_angle = calculate_angle(shoulder, elbow, wrist)

        is_plank = (wrist.y > elbow.y) and (60 < elbow_angle < 150) and (150 < body_angle < 210)

        if 'total_plank_time' not in st.session_state:
            st.session_state.total_plank_time = 0
        if 'last_plank_end' not in st.session_state:
            st.session_state.last_plank_end = 0
        if 'show_total_time' not in st.session_state:
            st.session_state.show_total_time = False

        if is_plank:
            if 'plank_start_time' not in st.session_state:
                st.session_state.plank_start_time = time.time()
                st.session_state.show_total_time = False
            
            hold_time = time.time() - st.session_state.plank_start_time
            cv2.putText(image, f"CURRENT: {int(hold_time)}s", (image.shape[1]//2 - 100, 50), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.putText(image, f"TOTAL: {int(st.session_state.total_plank_time)}s", 
                       (image.shape[1]//2 - 80, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            
        else:
            if 'plank_start_time' in st.session_state:
                st.session_state.total_plank_time += time.time() - st.session_state.plank_start_time
                st.session_state.last_plank_end = time.time()
                st.session_state.show_total_time = True
                del st.session_state.plank_start_time

            if st.session_state.show_total_time and (time.time() - st.session_state.last_plank_end < 3):
                cv2.putText(image, f"TOTAL TIME: {int(st.session_state.total_plank_time)}s", 
                           (image.shape[1]//2 - 120, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
                cv2.putText(image, "Great effort!", (image.shape[1]//2 - 100, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
            else:
                st.session_state.show_total_time = False

            cv2.putText(image, "Get ready for next plank!", (image.shape[1]//2 - 150, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    except Exception as e:
        st.error(f"Error tracking plank: {e}")