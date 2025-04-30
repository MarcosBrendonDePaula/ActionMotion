import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import threading
import time
import numpy as np
import PIL.Image, PIL.ImageTk

from src.utils.config import config
from src.core.tracker import MovementTracker
from src.gestures.detector import GestureDetector
from src.utils.helpers import select_camera, create_directories

# Import GUI components
from src.ui.components.menu import create_menu
from src.ui.components.sidebar import create_sidebar
from src.ui.components.capture import create_capture_frame
from src.ui.components.status_bar import create_status_bar
from src.ui.dialogs.gesture_dialogs import GestureDialogs
from src.ui.dialogs.camera_dialog import change_camera

class ActionMotionGUI:
    """
    Graphical user interface for ActionMotion.
    """
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Parameters:
        - root: Tkinter root window
        """
        self.root = root
        self.root.title("ActionMotion")
        self.root.geometry("1280x720")
        self.root.minsize(800, 600)
        
        # Create necessary directories
        create_directories()
        
        # Initialize components
        self.detector = GestureDetector()
        self.tracker = MovementTracker()
        
        # Initialize variables
        self.capture_mode = False
        self.last_gesture = {}
        self.frames_without_gestures = 0
        
        # Create GUI components
        self.menu_bar = create_menu(self)
        self.root.config(menu=self.menu_bar)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize camera component
        from src.ui.components.camera import CameraComponent
        self.camera = CameraComponent(self.main_frame, self)
        
        # Create capture frame
        self.capture_frame = create_capture_frame(self.main_frame, self)
        
        # Create sidebar
        self.sidebar, self.gesture_frame = create_sidebar(self.root, self)
        
        # Initialize sidebar visibility based on config
        if not config.show_gesture_sidebar:
            self.sidebar.pack_forget()
        
        # Create status bar
        self.status_bar, self.status_label, self.fps_label, self.camera_label_status = create_status_bar(self.root, self.camera.camera_index)
        
        # Create gesture dialogs handler
        self.gesture_dialogs = GestureDialogs(self.root, self.detector)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Start camera
        self.camera.start_camera()
    
    def process_frame(self, image):
        """
        Process a camera frame with gesture detection.
        
        Parameters:
        - image: frame to process
        
        Returns:
        - processed image
        """
        # Find hands if enabled
        hands = []
        if config.enable_hand_detection:
            image, hands = self.tracker.find_hands(image, draw=config.show_landmarks)
        
        # Find pose if enabled
        pose = []
        if config.enable_pose_detection:
            image, pose = self.tracker.find_pose(image, draw=config.show_landmarks)
        
        # Calculate FPS
        fps = self.tracker.calculate_fps()
        if config.show_fps:
            self.tracker.display_fps(image, fps)
            self.fps_label.config(text=f"FPS: {fps}")
        
        # Show information about detected hands
        if hands:
            for i, hand in enumerate(hands):
                hand_type = hand.get("type", "Unknown")
                cv2.putText(image, f"Hand {i+1}: {hand_type}", (10, 70 + i*30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # If not in capture mode, detect gestures
        if not self.capture_mode:
            detected_gestures = self.detector.detect_gestures(hands, pose, 
                                                            similarity_threshold=config.similarity_threshold)
            
            if detected_gestures:
                self.last_gesture = detected_gestures
                self.frames_without_gestures = 0
                
                # Update gesture display in sidebar
                self._update_gesture_display(detected_gestures)
                
                # Add gesture info to the image
                height, width, _ = image.shape
                overlay = image.copy()
                info_height = 30 * len(detected_gestures) + 25 * sum(1 for g in detected_gestures.values() if g.get("acao"))
                cv2.rectangle(overlay, (0, 120), (width, 150 + info_height), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
                
                y_offset = 150
                for name, info in detected_gestures.items():
                    # Check which hand type and direction was used for this gesture
                    hand_info = ""
                    if name in self.detector.gestures and "captura" in self.detector.gestures[name] and "hands" in self.detector.gestures[name]["captura"] and self.detector.gestures[name]["captura"]["hands"]:
                        for hand in hands:
                            # Calculate direction if not already done
                            if "direction" not in hand:
                                hand["direction"] = self.detector._calculate_hand_direction(hand["landmarks"])
                                
                            for captured_hand in self.detector.gestures[name]["captura"]["hands"]:
                                if hand.get("type", "") == captured_hand.get("type", ""):
                                    direction = hand.get("direction", "unknown")
                                    hand_info = f" ({hand.get('type', '')} hand, {direction})"
                                    break
                            if hand_info:
                                break
                    
                    text = f"Gesture: {name} - {info['descricao']}{hand_info} ({info['similaridade']:.2f})"
                    cv2.putText(image, text, (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    y_offset += 30
                    
                    # Show hold time information
                    if "hold_time" in info:
                        hold_time = info["hold_time"]
                        required_time = config.gesture_hold_time
                        progress = min(1.0, hold_time / required_time)
                        
                        # Display hold time status
                        hold_status = "Ready" if hold_time >= required_time else f"Hold: {hold_time:.1f}s / {required_time:.1f}s"
                        cv2.putText(image, f"  {hold_status}", (30, y_offset), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                        y_offset += 25
                        
                        # Draw progress bar
                        bar_length = 200
                        bar_height = 10
                        bar_x = 30
                        bar_y = y_offset - 5
                        
                        # Draw background
                        cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_length, bar_y + bar_height), (100, 100, 100), -1)
                        
                        # Draw progress
                        progress_width = int(bar_length * progress)
                        progress_color = (0, 255, 0) if progress >= 1.0 else (0, 255, 255)
                        cv2.rectangle(image, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), progress_color, -1)
                        
                        y_offset += 15
                    
                    # If should show action information and has associated action
                    if config.show_actions and info.get("acao"):
                        action = info["acao"]
                        action_text = f"  Action: {action['tipo']} - {str(action['parametros'])}"
                        cv2.putText(image, action_text, (30, y_offset), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
                        y_offset += 25
            else:
                self.frames_without_gestures += 1
                
                # Keep the last gesture visible for a few frames
                if self.frames_without_gestures < 30 and self.last_gesture:
                    # Add last gesture info to the image
                    height, width, _ = image.shape
                    overlay = image.copy()
                    info_height = 30 * len(self.last_gesture)
                    cv2.rectangle(overlay, (0, 120), (width, 150 + info_height), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
                    
                    y_offset = 150
                    for name, info in self.last_gesture.items():
                        text = f"Last: {name} - {info['descricao']}"
                        cv2.putText(image, text, (10, y_offset), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 100), 2)
                        y_offset += 30
                else:
                    # Clear gesture display in sidebar if no gestures for a while
                    if self.frames_without_gestures >= 30:
                        self._clear_gesture_display()
        
        # If in capture mode, show message
        if self.capture_mode:
            height, width, _ = image.shape
            overlay = image.copy()
            cv2.rectangle(overlay, (0, 90), (width, 130), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
            
            text = "CAPTURE MODE ACTIVATED - Position your hands and click Capture"
            cv2.putText(image, text, (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Show capture frame
            if not self.capture_frame.winfo_ismapped():
                self.capture_frame.pack(before=self.camera.camera_label, fill=tk.X, pady=10)
        else:
            # Hide capture frame
            if self.capture_frame.winfo_ismapped():
                self.capture_frame.pack_forget()
        
        # Show current camera
        height, width, _ = image.shape
        cv2.putText(image, f"Camera: {self.camera.camera_index}", (width - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return image
    
    def _update_gesture_display(self, gestures):
        """Update the gesture display in the sidebar."""
        # Store the current gestures for later reference
        self.current_gestures = gestures
        
        # Clear existing widgets
        for widget in self.gesture_frame.winfo_children():
            widget.destroy()
        
        # Create a frame for the gesture information
        info_frame = ttk.Frame(self.gesture_frame)
        info_frame.pack(fill=tk.X, expand=True)
        
        # Add gesture information
        for name, info in gestures.items():
            frame = ttk.Frame(info_frame)
            frame.pack(fill=tk.X, pady=2)
            
            # Get hand information including direction
            hand_info = []
            for hand_data in self.detector.gestures.get(name, {}).get("captura", {}).get("hands", []):
                hand_type = hand_data.get("type", "Unknown")
                direction = hand_data.get("direction", "unknown")
                hand_info.append(f"{hand_type} hand ({direction})")
            
            hand_type_str = ""
            if hand_info:
                hand_type_str = f" - {', '.join(hand_info)}"
            
            ttk.Label(frame, 
                     text=f"{name}: {info['similaridade']:.2f}",
                     font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            ttk.Label(frame, 
                     text=f"Description: {info['descricao']}").pack(anchor=tk.W)
            
            if hand_info:
                ttk.Label(frame, 
                         text=f"Hand info: {', '.join(hand_info)}",
                         foreground="blue").pack(anchor=tk.W)
            
            # Display hold time if available
            if "hold_time" in info:
                hold_time = info["hold_time"]
                required_time = config.gesture_hold_time
                progress = min(1.0, hold_time / required_time)
                
                # Create a frame for the progress bar
                progress_frame = ttk.Frame(frame)
                progress_frame.pack(fill=tk.X, pady=2)
                
                # Create a label for the hold time
                hold_status = "Ready" if hold_time >= required_time else f"Hold: {hold_time:.1f}s / {required_time:.1f}s"
                ttk.Label(progress_frame, text=hold_status).pack(side=tk.LEFT, padx=5)
                
                # Create a progress bar
                progress_bar = ttk.Progressbar(progress_frame, length=100, mode='determinate', value=progress*100)
                progress_bar.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
            
            if info.get("acao"):
                action = info["acao"]
                ttk.Label(frame, 
                         text=f"Action: {action['tipo']} - {str(action['parametros'])}",
                         foreground="purple").pack(anchor=tk.W)
            
            ttk.Separator(info_frame).pack(fill=tk.X, pady=5)
    
    def _clear_gesture_display(self):
        """Clear the gesture display in the sidebar."""
        # Only clear if we have no current gestures
        if not hasattr(self, 'current_gestures') or not self.current_gestures:
            for widget in self.gesture_frame.winfo_children():
                widget.destroy()
            
            # Add a simple label
            self.no_gestures_label = ttk.Label(self.gesture_frame, text="No gestures detected")
            self.no_gestures_label.pack(anchor=tk.W, padx=5, pady=10)
    
    def toggle_capture_mode(self):
        """Toggle capture mode on/off."""
        self.capture_mode = not self.capture_mode
        
        if self.capture_mode:
            self.status_label.config(text="Capture mode activated")
        else:
            self.status_label.config(text="Capture mode deactivated")
    
    def capture_gesture(self):
        """Capture the current gesture."""
        # Get current hands and pose
        if self.camera.cap is None:
            messagebox.showerror("Capture Error", "No camera available")
            return
            
        success, image = self.camera.read_frame()
        if not success:
            messagebox.showerror("Capture Error", "Failed to capture image from camera")
            return
        
        hands = []
        if config.enable_hand_detection:
            _, hands = self.tracker.find_hands(image, draw=False)
        
        pose = []
        if config.enable_pose_detection:
            _, pose = self.tracker.find_pose(image, draw=False)
        
        if not hands and not pose:
            messagebox.showerror("Capture Error", "No hands or pose detected. Try again.")
            return
        
        # Capture current state
        capture = self.detector.capture_gesture(hands, pose)
        
        # Show dialog to get gesture information
        self.gesture_dialogs.show_capture_dialog(capture)
        
        # Exit capture mode
        self.capture_mode = False
        self.status_label.config(text="Gesture captured")
    
    def change_camera(self):
        """Change the camera."""
        # Show camera selection dialog
        new_index = change_camera(self.root, self.camera.camera_index)
        self.camera.change_camera(new_index)
    
    def _on_close(self):
        """Handle window close event."""
        self.camera.stop_camera()
        self.root.destroy()

def run_gui():
    """Run the GUI application."""
    root = tk.Tk()
    app = ActionMotionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
