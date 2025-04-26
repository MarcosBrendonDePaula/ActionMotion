import tkinter as tk
from tkinter import ttk

def create_status_bar(root, camera_index):
    """
    Create the status bar at the bottom of the window.
    
    Parameters:
    - root: Tkinter root window
    - camera_index: current camera index
    
    Returns:
    - status bar frame
    - status label
    - fps label
    - camera label
    """
    status_bar = ttk.Frame(root)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Status label (left side)
    status_label = ttk.Label(status_bar, text="Ready")
    status_label.pack(side=tk.LEFT, padx=5)
    
    # FPS label (right side)
    fps_label = ttk.Label(status_bar, text="FPS: 0")
    fps_label.pack(side=tk.RIGHT, padx=5)
    
    # Camera label (right side)
    camera_label = ttk.Label(status_bar, text=f"Camera: {camera_index}")
    camera_label.pack(side=tk.RIGHT, padx=5)
    
    return status_bar, status_label, fps_label, camera_label
