import cv2
import math
import streamlit as st
import mediapipe as mp
from utils import calculate_angle, calculate_distance

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def yoga_page():
    """Yoga category page"""
    with st.container():
        st.markdown('<div class="exercise-title"><h3>🧘 Choose Your Yoga Pose</h3></div>', unsafe_allow_html=True)
        yoga_pose = st.selectbox("", ["Tree Pose", "Warrior II", "Downward Dog", "Cobra Pose", 
                                "Bridge Pose", "Child's Pose", "Mountain Pose", "Cat-Cow", 
                                "Easy Pose", "Seated Forward Bend", "Legs-Up-the-Wall"], key="yoga_select")
        
        # Add a continue button
        if st.button("Continue", key="yoga_continue"):
            st.session_state.show_yoga_instructions = True
            st.session_state.selected_yoga_pose = yoga_pose
            st.rerun()
        
        # If we're not showing instructions, stop here
        if not st.session_state.get('show_yoga_instructions', False):
            return
            
        # Show yoga instructions page
        st.markdown(f"<div class='exercise-card'>"
                   f"<h2>{st.session_state.selected_yoga_pose} Instructions</h2>"
                   f"</div>", unsafe_allow_html=True)
        
        # Add yoga-specific instructions and images
        show_yoga_instructions(st.session_state.selected_yoga_pose)

def show_yoga_instructions(pose):
    """Show instructions and image for the selected yoga pose"""
    # Dictionary mapping yoga poses to their instructions and image URLs
    yoga_data = {
    "Tree Pose": {
        "image": "C:\Users\Asus\Downloads\code hpe\code_hpe\yoga poses\treepose.jpeg",
        "instructions": [
            "Stand tall with feet together",
            "Shift weight to left foot, bend right knee",
            "Place right foot on left inner thigh or calf",
            "Bring hands to prayer position at chest",
            "Hold for 5-8 breaths, then switch sides"
        ]
    },
    "Warrior II": {
        "image": "C:\Users\Asus\Downloads\code hpe\code_hpe\yoga poses\warrior.jpeg",
        "instructions": [
            "Stand with feet 3-4 feet apart",
            "Turn right foot out 90 degrees, left foot slightly in",
            "Bend right knee directly over right ankle",
            "Extend arms parallel to floor, palms down",
            "Gaze over right hand, hold for 5-8 breaths",
            "Repeat on other side"
        ]
    },
    "Downward Dog": {
        "image": "D:/code hpe/yoga poses/downward dog.jpeg",
        "instructions": [
            "Start on hands and knees (tabletop position)",
            "Tuck toes and lift hips up and back",
            "Straighten legs as much as comfortable",
            "Press hands firmly into the mat",
            "Relax head between arms, hold for 5-8 breaths"
        ]
    },
    "Cobra Pose": {
        "image": "D:/code hpe/yoga poses/cobra.jpeg",
        "instructions": [
            "Lie on stomach with legs extended",
            "Place hands under shoulders, elbows close to body",
            "Press tops of feet into mat",
            "Inhale and lift chest off floor",
            "Keep shoulders down, hold for 3-5 breaths",
            "Exhale to release"
        ]
    },
    "Bridge Pose": {
        "image": "D:/code hpe/yoga poses/bridge.jpeg",
        "instructions": [
            "Lie on back with knees bent, feet hip-width apart",
            "Place arms alongside body, palms down",
            "Press feet into floor to lift hips",
            "Interlace fingers under back if comfortable",
            "Hold for 5-8 breaths, then slowly lower down"
        ]
    },
    "Child's Pose": {
        "image": "D:/code hpe/yoga poses/child pose (1).jpeg",
        "instructions": [
            "Kneel on floor with big toes touching",
            "Sit back on heels, knees wide apart",
            "Fold forward, extending arms in front",
            "Rest forehead on mat",
            "Relax shoulders, hold for 5-10 breaths"
        ]
    },
    "Mountain Pose": {
        "image": "D:/code hpe/yoga poses/mountain.jpeg",
        "instructions": [
            "Stand tall with feet together or hip-width apart",
            "Distribute weight evenly through both feet",
            "Engage thigh muscles, lift kneecaps",
            "Lengthen tailbone toward floor",
            "Relax shoulders down, arms at sides",
            "Breathe deeply, hold for 5-8 breaths"
        ]
    },
    "Cat-Cow": {
        "image": "D:/code hpe/yoga poses/cat cow.jpeg",
        "instructions": [
            "Start on hands and knees in tabletop position",
            "For Cow: Inhale, drop belly, lift chin and tailbone",
            "For Cat: Exhale, round spine, tuck chin and pelvis",
            "Move slowly with breath for 5-8 rounds",
            "Keep shoulders over wrists, hips over knees"
        ]
    },
    "Easy Pose": {
        "image": "D:/code hpe/yoga poses/easypose.jpeg",
        "instructions": [
            "Sit cross-legged on floor or cushion",
            "Place hands on knees, palms up or down",
            "Lengthen spine, relax shoulders",
            "Close eyes or soften gaze",
            "Breathe naturally, hold for 1-5 minutes"
        ]
    },
    "Seated Forward Bend": {
        "image": "D:/code hpe/yoga poses/seated forward bend.jpeg",
        "instructions": [
            "Sit with legs extended straight in front",
            "Inhale and lengthen spine upward",
            "Exhale and hinge forward from hips",
            "Reach for feet, shins, or use strap",
            "Keep back straight, hold for 5-8 breaths"
        ]
    },
    "Legs-Up-the-Wall": {
        "image": "D:/code hpe/yoga poses/shoulderstand.jpeg",
        "instructions": [
            "Sit sideways with one hip against wall",
            "Swing legs up wall as you lie back",
            "Rest arms at sides, palms up",
            "Close eyes and relax completely",
            "Hold for 5-15 minutes"
        ]
    }
}
    # Get the data for the selected pose
    data = yoga_data.get(pose, {
        "image": "https://via.placeholder.com/500x300?text=Yoga+Pose+Image",
        "instructions": ["Detailed instructions coming soon!"]
    })
    
    # Display in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(data["image"], width=300, caption=pose)
        
    with col2:
        st.markdown("**Instructions:**")
        for i, instruction in enumerate(data["instructions"], 1):
            st.markdown(f"{i}. {instruction}")
    
    # Add a back button
    if st.button("Back to Selection", key="yoga_back"):
        st.session_state.show_yoga_instructions = False
        st.rerun()
    
    # Add the webcam controls below the instructions
    st.markdown("---")
    initialize_yoga_tracking(pose)

def initialize_yoga_tracking(pose):
    """Initialize the yoga tracking section"""
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
        process_yoga_feed(pose)

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
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

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