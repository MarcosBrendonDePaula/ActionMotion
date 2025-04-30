import cv2
import os
from src.utils.config import config

def list_cameras():
    """
    List all available cameras in the system.
    
    Returns:
    - dictionary with camera indices and status
    """
    available_cameras = {}
    # Only check the first 3 cameras to speed up the process
    for i in range(15):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras[i] = "Available"
            else:
                available_cameras[i] = "Unavailable (No frames received)"
            cap.release()
    
    if not available_cameras:
        # Default to camera 0 if none found
        available_cameras[0] = "Default"
        print("No cameras found. Using default camera.")
    
    return available_cameras

def select_camera():
    """
    Allow the user to select a camera.
    
    Returns:
    - selected camera index
    """
    cameras = list_cameras()
    
    if not cameras:
        print("Using default camera (0).")
        return 0
    
    print("\n=== Available Cameras ===")
    for idx, status in cameras.items():
        print(f"Camera {idx}: {status}")
    
    try:
        choice = int(input("\nSelect camera number: "))
        if choice in cameras:
            print(f"Camera {choice} selected.")
            return choice
        else:
            print("Invalid camera. Using default camera (0).")
            return 0
    except ValueError:
        print("Invalid input. Using default camera (0).")
        return 0

def create_directories():
    """
    Create necessary directories for the project.
    """
    # Directory to store gestures
    if not os.path.exists("gestos"):
        os.makedirs("gestos")
        print("Gestures directory created.")
    
    return True

def show_help_screen(image):
    """
    Add help information to the image.
    
    Parameters:
    - image: camera frame
    
    Returns:
    - image with help information
    """
    height, width, _ = image.shape
    
    # Create a semi-transparent overlay for the title
    overlay = image.copy()
    cv2.rectangle(overlay, (0, 0), (width, 50), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
    
    # Information at the top of the screen
    cv2.putText(image, "MOVEMENT TRACKER", (width // 2 - 150, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Create a semi-transparent overlay for the commands
    overlay = image.copy()
    command_height = 230  # Height for command area
    cv2.rectangle(overlay, (0, height - command_height), (200, height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
    
    # Commands at the bottom of the screen
    y = height - 20
    cv2.putText(image, "q: Quit", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(image, "c: Change camera", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(image, "r: Capture gesture", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(image, "a: Edit actions", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(image, "l: List gestures", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(image, "d: Remove gesture", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(image, "s: Show/hide actions", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(image, "h: Toggle hand detection", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(image, "p: Toggle pose detection", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Create a semi-transparent overlay for the status
    overlay = image.copy()
    status_width = 250
    status_height = 120
    cv2.rectangle(overlay, (width - status_width, 50), (width, 50 + status_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
    
    # Show configuration status
    status_x = width - status_width + 10
    status_y = 70
    cv2.putText(image, "Status:", (status_x, status_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    status_y += 20
    
    # Show detection status
    hand_status = "ON" if config.enable_hand_detection else "OFF"
    pose_status = "ON" if config.enable_pose_detection else "OFF"
    cv2.putText(image, f"Hands: {hand_status}", (status_x, status_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if config.enable_hand_detection else (0, 0, 255), 1)
    status_y += 20
    cv2.putText(image, f"Pose: {pose_status}", (status_x, status_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if config.enable_pose_detection else (0, 0, 255), 1)
    status_y += 20
    
    # Show display settings
    landmarks_status = "ON" if config.show_landmarks else "OFF"
    cv2.putText(image, f"Landmarks: {landmarks_status}", (status_x, status_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if config.show_landmarks else (0, 0, 255), 1)
    status_y += 20
    
    # Show confidence threshold
    # Color changes based on threshold value: green for high confidence, yellow for medium, red for low
    confidence_color = (0, 255, 0)  # Green by default
    if config.confidence_threshold < 0.7:
        confidence_color = (0, 0, 255)  # Red for low threshold
    elif config.confidence_threshold < 0.85:
        confidence_color = (0, 255, 255)  # Yellow for medium threshold
        
    cv2.putText(image, f"Confidence: {config.confidence_threshold:.2f}", (status_x, status_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, confidence_color, 1)
    
    return image

def key_listener(callback):
    """
    Listen for key presses and call the callback function when a key is pressed.
    
    Parameters:
    - callback: function to call when a key is pressed
    """
    def on_key_press(key):
        callback(key)
    
    return on_key_press
