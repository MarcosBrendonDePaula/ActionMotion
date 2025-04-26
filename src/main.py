import cv2
import os
import time
import json
from src.core.tracker import MovementTracker
from src.gestures.detector import GestureDetector
from src.utils.helpers import select_camera, create_directories, show_help_screen
from src.ui.action_editor import edit_actions
from src.utils.config import config

def main():
    """
    Main application entry point.
    """
    # Create necessary directories
    create_directories()
    
    # Camera selection
    camera_index = select_camera()
    
    # Start video capture
    cap = cv2.VideoCapture(camera_index)
    
    # Check if camera was opened successfully
    if not cap.isOpened():
        print(f"Could not open camera {camera_index}. Trying default camera (0).")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Failed to open any camera. Exiting program.")
            return
    
    # Initialize gesture detector
    detector = GestureDetector()
    
    # Create tracker instance
    tracker = MovementTracker()
    
    # Variables for program control
    capture_mode = False
    last_gesture = {}
    frames_without_gestures = 0
    
    # Create resizable window
    cv2.namedWindow("Movement Tracker", cv2.WINDOW_NORMAL)
    
    # Set initial window size (can be resized by user)
    cv2.resizeWindow("Movement Tracker", config.window_width, config.window_height)
    
    print("\n=== Movement Tracker Started ===")
    print("Press 'r' to capture a new gesture")
    print("Press 'a' to manage gesture actions")
    print("Press 'l' to list registered gestures")
    print("Press 'd' to remove a gesture")
    print("Press 'c' to change camera")
    print("Press 'h' to toggle hand detection")
    print("Press 'p' to toggle pose detection")
    print("Press 's' to show/hide action information")
    print("Press 'f' to show/hide FPS")
    print("Press 'm' to show/hide landmarks")
    print("Press '+' to increase confidence threshold")
    print("Press '-' to decrease confidence threshold")
    print("Press 'q' to quit\n")
    
    while True:
        # Capture frame
        success, image = cap.read()
        if not success:
            print("Failed to capture image from camera.")
            break
            
        # Find hands if enabled
        hands = []
        if config.enable_hand_detection:
            image, hands = tracker.find_hands(image, draw=config.show_landmarks)
        
        # Find pose if enabled
        pose = []
        if config.enable_pose_detection:
            image, pose = tracker.find_pose(image, draw=config.show_landmarks)
        
        # Add help information to screen
        image = show_help_screen(image)
        
        # Calculate and show FPS if enabled
        fps = tracker.calculate_fps()
        if config.show_fps:
            tracker.display_fps(image, fps)
        
        # Show information about detected hands
        if hands:
            for i, hand in enumerate(hands):
                hand_type = hand.get("type", "Unknown")
                cv2.putText(image, f"Hand {i+1}: {hand_type}", (10, 70 + i*30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # If not in capture mode, detect gestures
        if not capture_mode:
            detected_gestures = detector.detect_gestures(hands, pose, similarity_threshold=config.similarity_threshold)
            
            if detected_gestures:
                last_gesture = detected_gestures
                frames_without_gestures = 0
                
                # Create a semi-transparent overlay for gesture info
                overlay = image.copy()
                height, width, _ = image.shape
                info_height = 30 * len(detected_gestures) + 25 * sum(1 for g in detected_gestures.values() if g.get("acao"))
                cv2.rectangle(overlay, (0, 120), (width, 150 + info_height), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
                
                y_offset = 150
                for name, info in detected_gestures.items():
                    # Basic text with gesture name and similarity
                    # Check which hand type was used for this gesture
                    hand_type = ""
                    if name in detector.gestures and "captura" in detector.gestures[name] and "hands" in detector.gestures[name]["captura"] and detector.gestures[name]["captura"]["hands"]:
                        for hand in hands:
                            for captured_hand in detector.gestures[name]["captura"]["hands"]:
                                if hand.get("type", "") == captured_hand.get("type", ""):
                                    hand_type = f" ({hand.get('type', '')} hand)"
                                    break
                            if hand_type:
                                break
                    
                    text = f"Gesture: {name} - {info['descricao']}{hand_type} ({info['similaridade']:.2f})"
                    cv2.putText(image, text, (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    y_offset += 30
                    
                    # If should show action information and has associated action
                    if config.show_actions and info.get("acao"):
                        action = info["acao"]
                        action_text = f"  Action: {action['tipo']} - {str(action['parametros'])}"
                        cv2.putText(image, action_text, (30, y_offset), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
                        y_offset += 25
            else:
                frames_without_gestures += 1
                
                # Keep the last gesture visible for a few frames
                if frames_without_gestures < 30 and last_gesture:
                    # Create a semi-transparent overlay for last gesture info
                    overlay = image.copy()
                    height, width, _ = image.shape
                    info_height = 30 * len(last_gesture)
                    cv2.rectangle(overlay, (0, 120), (width, 150 + info_height), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
                    
                    y_offset = 150
                    for name, info in last_gesture.items():
                        text = f"Last: {name} - {info['descricao']}"
                        cv2.putText(image, text, (10, y_offset), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 100), 2)
                        y_offset += 30
        
        # If in capture mode, show message
        if capture_mode:
            # Create a semi-transparent overlay for capture mode message
            overlay = image.copy()
            height, width, _ = image.shape
            cv2.rectangle(overlay, (0, 90), (width, 130), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
            
            text = "CAPTURE MODE ACTIVATED - Position your hands and press 'r' again"
            cv2.putText(image, text, (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Show current camera
        cv2.putText(image, f"Camera: {camera_index}", (image.shape[1] - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show image
        cv2.imshow("Movement Tracker", image)
        
        # Capture pressed key
        key = cv2.waitKey(1) & 0xFF
        
        # Process commands
        if key == ord('q'):
            # Exit program
            break
            
        elif key == ord('r'):
            # Gesture capture mode
            if not capture_mode:
                # Enter capture mode
                capture_mode = True
                print("\nCAPTURE MODE ACTIVATED")
                print("Position your hands/body in the desired position and press 'r' again to capture.")
                
            else:
                # Capture current gesture
                if not hands and not pose:
                    print("No hands or pose detected. Try again.")
                else:
                    # Capture current state
                    capture = detector.capture_gesture(hands, pose)
                    
                    # Request gesture information
                    name = input("\nEnter a name for this gesture (no spaces): ")
                    description = input("Enter a description for this gesture: ")
                    
                    # Save the gesture
                    if detector.save_gesture(name, description, capture):
                        print(f"Gesture '{name}' saved successfully!")
                        
                        # Ask if want to associate an action
                        associate = input("\nDo you want to associate an action with this gesture? (y/n): ").lower()
                        if associate == 'y':
                            edit_actions(detector, name)
                    else:
                        print("Failed to save gesture.")
                    
                # Exit capture mode
                capture_mode = False
                
        elif key == ord('a'):
            # Edit gesture actions
            cap.release()
            cv2.destroyAllWindows()
            
            edit_actions(detector)
            
            # Restart camera
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                print(f"Could not reopen camera {camera_index}. Trying default camera (0).")
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print("Failed to open any camera. Exiting program.")
                    break
        
        elif key == ord('h'):
            # Toggle hand detection
            enabled = config.toggle_hand_detection()
            print(f"Hand detection: {'ENABLED' if enabled else 'DISABLED'}")
                
        elif key == ord('p'):
            # Toggle pose detection
            enabled = config.toggle_pose_detection()
            print(f"Pose detection: {'ENABLED' if enabled else 'DISABLED'}")
                
        elif key == ord('f'):
            # Toggle FPS display
            enabled = config.toggle_fps_display()
            print(f"FPS display: {'ENABLED' if enabled else 'DISABLED'}")
                
        elif key == ord('m'):
            # Toggle landmarks display
            enabled = config.toggle_landmarks_display()
            print(f"Landmarks display: {'ENABLED' if enabled else 'DISABLED'}")
                
        elif key == ord('s'):
            # Toggle action information display
            enabled = config.toggle_actions_display()
            print(f"Action information: {'ENABLED' if enabled else 'DISABLED'}")
            
        elif key == ord('+') or key == ord('='):  # '+' key is often Shift+= on keyboards
            # Increase confidence threshold
            new_threshold = min(1.0, config.confidence_threshold + 0.05)
            config.set_confidence_threshold(new_threshold)
            print(f"Confidence threshold increased to: {config.confidence_threshold:.2f}")
            
        elif key == ord('-'):
            # Decrease confidence threshold
            new_threshold = max(0.5, config.confidence_threshold - 0.05)
            config.set_confidence_threshold(new_threshold)
            print(f"Confidence threshold decreased to: {config.confidence_threshold:.2f}")
                
        elif key == ord('l'):
            # List registered gestures
            print("\n=== Registered Gestures ===")
            gestures = detector.list_gestures()
            
            if gestures:
                for i, (name, description) in enumerate(gestures):
                    # Check if it has an associated action
                    has_action = "acao" in detector.gestures[name] and detector.gestures[name]["acao"] is not None
                    action_status = "With action" if has_action else "No action"
                    print(f"{i+1}. {name}: {description} [{action_status}]")
                    
                    # If it has an action, show details
                    if has_action:
                        action = detector.gestures[name]["acao"]
                        print(f"   Action: {action['tipo']} - {action['parametros']}")
            else:
                print("No gestures registered.")
                
            print()  # Blank line
            
        elif key == ord('d'):
            # Remove a gesture
            print("\n=== Remove Gesture ===")
            gestures = detector.list_gestures()
            
            if gestures:
                for i, (name, description) in enumerate(gestures):
                    print(f"{i+1}. {name}: {description}")
                
                try:
                    choice = int(input("\nEnter the number of the gesture to remove (0 to cancel): "))
                    
                    if 1 <= choice <= len(gestures):
                        gesture_name = gestures[choice - 1][0]
                        if detector.remove_gesture(gesture_name):
                            print(f"Gesture '{gesture_name}' removed successfully!")
                        else:
                            print(f"Failed to remove gesture '{gesture_name}'.")
                    elif choice != 0:
                        print("Invalid gesture number.")
                        
                except ValueError:
                    print("Invalid input.")
            else:
                print("No gestures registered.")
                
            print()  # Blank line
            
        elif key == ord('c'):
            # Change camera
            print("\n=== Change Camera ===")
            
            # Release current camera
            cap.release()
            
            # Select new camera
            camera_index = select_camera()
            cap = cv2.VideoCapture(camera_index)
            
            # Check if new camera was opened successfully
            if not cap.isOpened():
                print(f"Could not open camera {camera_index}. Trying default camera (0).")
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print("Failed to open any camera. Exiting program.")
                    break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("\nMovement Tracker closed.")

if __name__ == "__main__":
    main()
