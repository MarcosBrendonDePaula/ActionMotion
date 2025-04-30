import tkinter as tk
from tkinter import ttk

def create_menu(gui):
    """
    Create the menu bar for the application.
    
    Parameters:
    - gui: ActionMotionGUI instance
    
    Returns:
    - menu bar
    """
    menu_bar = tk.Menu(gui.root)
    
    # File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Change Camera", command=gui.change_camera)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=gui._on_close)
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    # Gesture menu
    gesture_menu = tk.Menu(menu_bar, tearoff=0)
    gesture_menu.add_command(label="Capture Gesture", command=gui.toggle_capture_mode)
    gesture_menu.add_command(label="List Gestures", command=lambda: gui.gesture_dialogs.show_list_dialog())
    gesture_menu.add_command(label="Edit Actions", command=lambda: gui.gesture_dialogs.show_edit_dialog())
    gesture_menu.add_command(label="Remove Gesture", command=lambda: gui.gesture_dialogs.show_remove_dialog())
    menu_bar.add_cascade(label="Gestures", menu=gesture_menu)
    
    # Settings menu
    settings_menu = tk.Menu(menu_bar, tearoff=0)
    
    # Import config here to avoid circular imports
    from src.utils.config import config
    
    # Detection submenu
    detection_menu = tk.Menu(settings_menu, tearoff=0)
    gui.hand_detection_var = tk.BooleanVar(value=config.enable_hand_detection)
    detection_menu.add_checkbutton(label="Hand Detection", 
                                  variable=gui.hand_detection_var,
                                  command=lambda: toggle_hand_detection(gui))
    
    gui.pose_detection_var = tk.BooleanVar(value=config.enable_pose_detection)
    detection_menu.add_checkbutton(label="Pose Detection", 
                                  variable=gui.pose_detection_var,
                                  command=lambda: toggle_pose_detection(gui))
    settings_menu.add_cascade(label="Detection", menu=detection_menu)
    
    # Display submenu
    display_menu = tk.Menu(settings_menu, tearoff=0)
    gui.show_fps_var = tk.BooleanVar(value=config.show_fps)
    display_menu.add_checkbutton(label="Show FPS", 
                                variable=gui.show_fps_var,
                                command=lambda: toggle_fps_display(gui))
    
    gui.show_landmarks_var = tk.BooleanVar(value=config.show_landmarks)
    display_menu.add_checkbutton(label="Show Landmarks", 
                                variable=gui.show_landmarks_var,
                                command=lambda: toggle_landmarks_display(gui))
    
    gui.show_actions_var = tk.BooleanVar(value=config.show_actions)
    display_menu.add_checkbutton(label="Show Actions", 
                                variable=gui.show_actions_var,
                                command=lambda: toggle_actions_display(gui))
    
    gui.show_gesture_sidebar_var = tk.BooleanVar(value=config.show_gesture_sidebar)
    display_menu.add_checkbutton(label="Show Gesture Sidebar", 
                                variable=gui.show_gesture_sidebar_var,
                                command=lambda: toggle_gesture_sidebar(gui))
    settings_menu.add_cascade(label="Display", menu=display_menu)
    
    # Confidence threshold
    settings_menu.add_command(label="Adjust Confidence Threshold", 
                             command=lambda: gui.gesture_dialogs.show_threshold_dialog())
    
    menu_bar.add_cascade(label="Settings", menu=settings_menu)
    
    # Help menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: gui.gesture_dialogs.show_about_dialog())
    help_menu.add_command(label="Keyboard Shortcuts", command=lambda: gui.gesture_dialogs.show_shortcuts_dialog())
    menu_bar.add_cascade(label="Help", menu=help_menu)
    
    return menu_bar

def toggle_hand_detection(gui):
    """Toggle hand detection on/off."""
    from src.utils.config import config
    config.toggle_hand_detection()
    gui.status_label.config(text=f"Hand detection: {'enabled' if config.enable_hand_detection else 'disabled'}")

def toggle_pose_detection(gui):
    """Toggle pose detection on/off."""
    from src.utils.config import config
    config.toggle_pose_detection()
    gui.status_label.config(text=f"Pose detection: {'enabled' if config.enable_pose_detection else 'disabled'}")

def toggle_fps_display(gui):
    """Toggle FPS display on/off."""
    from src.utils.config import config
    config.toggle_fps_display()
    gui.status_label.config(text=f"FPS display: {'enabled' if config.show_fps else 'disabled'}")

def toggle_landmarks_display(gui):
    """Toggle landmarks display on/off."""
    from src.utils.config import config
    config.toggle_landmarks_display()
    gui.status_label.config(text=f"Landmarks display: {'enabled' if config.show_landmarks else 'disabled'}")

def toggle_actions_display(gui):
    """Toggle actions display on/off."""
    from src.utils.config import config
    config.toggle_actions_display()
    gui.status_label.config(text=f"Actions display: {'enabled' if config.show_actions else 'disabled'}")

def toggle_gesture_sidebar(gui):
    """Toggle gesture sidebar display on/off."""
    from src.utils.config import config
    config.toggle_gesture_sidebar()
    gui.status_label.config(text=f"Gesture sidebar: {'enabled' if config.show_gesture_sidebar else 'disabled'}")
    
    # Update the sidebar visibility
    if config.show_gesture_sidebar:
        gui.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
    else:
        gui.sidebar.pack_forget()
