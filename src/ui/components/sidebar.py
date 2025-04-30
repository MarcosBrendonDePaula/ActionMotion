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
    
    # Create main sidebar frame
    sidebar = ttk.Frame(root, width=300)
    sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
    
    # Create a canvas with scrollbar for the sidebar content
    canvas = tk.Canvas(sidebar, width=280)
    scrollbar = ttk.Scrollbar(sidebar, orient="vertical", command=canvas.yview)
    
    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create a frame inside the canvas for all sidebar content
    sidebar_content = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=sidebar_content, anchor="nw", width=280)
    
    # Detected gestures section
    ttk.Label(sidebar_content, text="Detected Gestures", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
    gesture_frame = ttk.Frame(sidebar_content)
    gesture_frame.pack(fill=tk.X, pady=5)
    
    # No gestures detected initially
    no_gestures_label = ttk.Label(gesture_frame, text="No gestures detected")
    no_gestures_label.pack(anchor=tk.W)
    
    # Configuration section
    ttk.Separator(sidebar_content).pack(fill=tk.X, pady=10)
    ttk.Label(sidebar_content, text="Configuration", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
    
    # Detection settings
    detection_frame = ttk.LabelFrame(sidebar_content, text="Detection")
    detection_frame.pack(fill=tk.X, pady=5)
    
    ttk.Checkbutton(detection_frame, text="Hand Detection", 
                   variable=gui.hand_detection_var,
                   command=lambda: toggle_hand_detection(gui)).pack(anchor=tk.W, padx=5, pady=2)
    
    ttk.Checkbutton(detection_frame, text="Pose Detection", 
                   variable=gui.pose_detection_var,
                   command=lambda: toggle_pose_detection(gui)).pack(anchor=tk.W, padx=5, pady=2)
    
    # Display settings
    display_frame = ttk.LabelFrame(sidebar_content, text="Display")
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
    
    ttk.Checkbutton(display_frame, text="Show Gesture Sidebar", 
                   variable=gui.show_gesture_sidebar_var,
                   command=lambda: toggle_gesture_sidebar(gui)).pack(anchor=tk.W, padx=5, pady=2)
    
    # Confidence threshold
    threshold_frame = ttk.LabelFrame(sidebar_content, text="Confidence Threshold")
    threshold_frame.pack(fill=tk.X, pady=5)
    
    gui.threshold_scale = ttk.Scale(threshold_frame, 
                                   from_=0.5, to=1.0, 
                                   value=config.confidence_threshold,
                                   command=lambda value: update_confidence_threshold(gui, value))
    gui.threshold_scale.pack(fill=tk.X, padx=5, pady=5)
    
    gui.threshold_label = ttk.Label(threshold_frame, 
                                   text=f"Threshold: {config.confidence_threshold:.2f}")
    gui.threshold_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
    
    # Gesture hold time
    hold_time_frame = ttk.LabelFrame(sidebar_content, text="Gesture Hold Time")
    hold_time_frame.pack(fill=tk.X, pady=5)
    
    gui.hold_time_scale = ttk.Scale(hold_time_frame, 
                                   from_=0.1, to=3.0, 
                                   value=config.gesture_hold_time,
                                   command=lambda value: update_hold_time(gui, value))
    gui.hold_time_scale.pack(fill=tk.X, padx=5, pady=5)
    
    gui.hold_time_label = ttk.Label(hold_time_frame, 
                                   text=f"Hold Time: {config.gesture_hold_time:.1f}s")
    gui.hold_time_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
    
    # Quick actions
    ttk.Separator(sidebar_content).pack(fill=tk.X, pady=10)
    ttk.Label(sidebar_content, text="Quick Actions", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
    
    actions_frame = ttk.Frame(sidebar_content)
    actions_frame.pack(fill=tk.X, pady=5)
    
    ttk.Button(actions_frame, text="Capture Gesture", 
              command=gui.toggle_capture_mode).pack(fill=tk.X, pady=2)
    
    ttk.Button(actions_frame, text="Edit Actions", 
              command=lambda: gui.gesture_dialogs.show_edit_dialog()).pack(fill=tk.X, pady=2)
    
    ttk.Button(actions_frame, text="List Gestures", 
              command=lambda: gui.gesture_dialogs.show_list_dialog()).pack(fill=tk.X, pady=2)
    
    # Update the canvas scroll region when the sidebar content changes
    sidebar_content.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    
    # Bind mouse wheel to scroll
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
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

def toggle_gesture_sidebar(gui):
    """Toggle gesture sidebar display on/off."""
    config.toggle_gesture_sidebar()
    gui.status_label.config(text=f"Gesture sidebar: {'enabled' if config.show_gesture_sidebar else 'disabled'}")
    
    # Update the sidebar visibility
    if config.show_gesture_sidebar:
        gui.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
    else:
        gui.sidebar.pack_forget()

def update_confidence_threshold(gui, value):
    """Update confidence threshold."""
    threshold = float(value)
    config.set_confidence_threshold(threshold)
    gui.threshold_label.config(text=f"Threshold: {config.confidence_threshold:.2f}")

def update_hold_time(gui, value):
    """Update gesture hold time."""
    hold_time = float(value)
    config.set_gesture_hold_time(hold_time)
    gui.hold_time_label.config(text=f"Hold Time: {config.gesture_hold_time:.1f}s")
    gui.status_label.config(text=f"Gesture hold time set to {config.gesture_hold_time:.1f} seconds")
