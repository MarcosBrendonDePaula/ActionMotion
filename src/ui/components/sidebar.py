import tkinter as tk
from tkinter import ttk
from src.utils.config import config

def create_sidebar(root, gui):
    """
    Create the sidebar with controls and information.
    
    Parameters:
    - root: Tkinter root window
    - gui: ActionMotionGUI instance
    
    Returns:
    - sidebar frame
    - gesture frame (for updating gesture display)
    """
    # Import config here to avoid circular imports
    from src.utils.config import config
    
    sidebar = ttk.Frame(root, width=300)
    sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
    
    # Detected gestures section
    ttk.Label(sidebar, text="Detected Gestures", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
    gesture_frame = ttk.Frame(sidebar)
    gesture_frame.pack(fill=tk.X, pady=5)
    
    # No gestures detected initially
    no_gestures_label = ttk.Label(gesture_frame, text="No gestures detected")
    no_gestures_label.pack(anchor=tk.W)
    
    # Configuration section
    ttk.Separator(sidebar).pack(fill=tk.X, pady=10)
    ttk.Label(sidebar, text="Configuration", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
    
    # Detection settings
    detection_frame = ttk.LabelFrame(sidebar, text="Detection")
    detection_frame.pack(fill=tk.X, pady=5)
    
    ttk.Checkbutton(detection_frame, text="Hand Detection", 
                   variable=gui.hand_detection_var,
                   command=lambda: toggle_hand_detection(gui)).pack(anchor=tk.W, padx=5, pady=2)
    
    ttk.Checkbutton(detection_frame, text="Pose Detection", 
                   variable=gui.pose_detection_var,
                   command=lambda: toggle_pose_detection(gui)).pack(anchor=tk.W, padx=5, pady=2)
    
    # Display settings
    display_frame = ttk.LabelFrame(sidebar, text="Display")
    display_frame.pack(fill=tk.X, pady=5)
    
    ttk.Checkbutton(display_frame, text="Show FPS", 
                   variable=gui.show_fps_var,
                   command=lambda: toggle_fps_display(gui)).pack(anchor=tk.W, padx=5, pady=2)
    
    ttk.Checkbutton(display_frame, text="Show Landmarks", 
                   variable=gui.show_landmarks_var,
                   command=lambda: toggle_landmarks_display(gui)).pack(anchor=tk.W, padx=5, pady=2)
    
    ttk.Checkbutton(display_frame, text="Show Actions", 
                   variable=gui.show_actions_var,
                   command=lambda: toggle_actions_display(gui)).pack(anchor=tk.W, padx=5, pady=2)
    
    # Confidence threshold
    threshold_frame = ttk.LabelFrame(sidebar, text="Confidence Threshold")
    threshold_frame.pack(fill=tk.X, pady=5)
    
    gui.threshold_scale = ttk.Scale(threshold_frame, 
                                   from_=0.5, to=1.0, 
                                   value=config.confidence_threshold,
                                   command=lambda value: update_confidence_threshold(gui, value))
    gui.threshold_scale.pack(fill=tk.X, padx=5, pady=5)
    
    gui.threshold_label = ttk.Label(threshold_frame, 
                                   text=f"Threshold: {config.confidence_threshold:.2f}")
    gui.threshold_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
    
    # Quick actions
    ttk.Separator(sidebar).pack(fill=tk.X, pady=10)
    ttk.Label(sidebar, text="Quick Actions", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
    
    actions_frame = ttk.Frame(sidebar)
    actions_frame.pack(fill=tk.X, pady=5)
    
    ttk.Button(actions_frame, text="Capture Gesture", 
              command=gui.toggle_capture_mode).pack(fill=tk.X, pady=2)
    
    ttk.Button(actions_frame, text="Edit Actions", 
              command=lambda: gui.gesture_dialogs.show_edit_dialog()).pack(fill=tk.X, pady=2)
    
    ttk.Button(actions_frame, text="List Gestures", 
              command=lambda: gui.gesture_dialogs.show_list_dialog()).pack(fill=tk.X, pady=2)
    
    return sidebar, gesture_frame

def toggle_hand_detection(gui):
    """Toggle hand detection on/off."""
    config.toggle_hand_detection()
    gui.status_label.config(text=f"Hand detection: {'enabled' if config.enable_hand_detection else 'disabled'}")

def toggle_pose_detection(gui):
    """Toggle pose detection on/off."""
    config.toggle_pose_detection()
    gui.status_label.config(text=f"Pose detection: {'enabled' if config.enable_pose_detection else 'disabled'}")

def toggle_fps_display(gui):
    """Toggle FPS display on/off."""
    config.toggle_fps_display()
    gui.status_label.config(text=f"FPS display: {'enabled' if config.show_fps else 'disabled'}")

def toggle_landmarks_display(gui):
    """Toggle landmarks display on/off."""
    config.toggle_landmarks_display()
    gui.status_label.config(text=f"Landmarks display: {'enabled' if config.show_landmarks else 'disabled'}")

def toggle_actions_display(gui):
    """Toggle actions display on/off."""
    config.toggle_actions_display()
    gui.status_label.config(text=f"Actions display: {'enabled' if config.show_actions else 'disabled'}")

def update_confidence_threshold(gui, value):
    """Update confidence threshold."""
    threshold = float(value)
    config.set_confidence_threshold(threshold)
    gui.threshold_label.config(text=f"Threshold: {config.confidence_threshold:.2f}")
