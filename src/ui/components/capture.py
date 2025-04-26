import tkinter as tk
from tkinter import ttk

def create_capture_frame(parent, gui):
    """
    Create the capture mode frame.
    
    Parameters:
    - parent: parent frame
    - gui: ActionMotionGUI instance
    
    Returns:
    - capture frame
    """
    capture_frame = ttk.Frame(parent)
    
    # Capture mode label
    capture_label = ttk.Label(capture_frame, 
                             text="CAPTURE MODE: Position your hands and click Capture",
                             font=("Arial", 14, "bold"),
                             foreground="red")
    capture_label.pack(pady=10)
    
    # Capture button
    capture_button = ttk.Button(capture_frame, 
                               text="Capture Gesture",
                               command=gui.capture_gesture)
    capture_button.pack(pady=5)
    
    # Cancel button
    cancel_button = ttk.Button(capture_frame, 
                              text="Cancel",
                              command=gui.toggle_capture_mode)
    cancel_button.pack(pady=5)
    
    # Initially hidden
    # Will be shown/hidden by the main GUI when needed
    
    return capture_frame
