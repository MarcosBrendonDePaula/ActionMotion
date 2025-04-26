import tkinter as tk
from tkinter import ttk, messagebox
import cv2

def change_camera(root, current_camera_index):
    """
    Show dialog to change the camera.
    
    Parameters:
    - root: Tkinter root window
    - current_camera_index: current camera index
    
    Returns:
    - new camera index
    """
    # Select new camera
    cameras = {}
    for i in range(3):  # Check first 3 cameras
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cameras[i] = "Available"
                else:
                    cameras[i] = "Unavailable (No frames received)"
            cap.release()
        except Exception as e:
            print(f"Error checking camera {i}: {e}")
    
    if not cameras:
        messagebox.showerror("Camera Error", "No cameras found. Using default camera (0).")
        return 0
    
    # Create camera selection dialog
    camera_dialog = tk.Toplevel(root)
    camera_dialog.title("Select Camera")
    camera_dialog.geometry("300x200")
    camera_dialog.transient(root)
    camera_dialog.grab_set()
    
    ttk.Label(camera_dialog, text="Available Cameras", 
             font=("Arial", 12, "bold")).pack(pady=10)
    
    camera_var = tk.IntVar(value=current_camera_index)
    
    for idx, status in cameras.items():
        ttk.Radiobutton(camera_dialog, text=f"Camera {idx}: {status}", 
                       variable=camera_var, value=idx).pack(anchor=tk.W, padx=20, pady=2)
    
    # Variable to store the result
    result = [current_camera_index]
    
    def select_camera():
        result[0] = camera_var.get()
        camera_dialog.destroy()
    
    ttk.Button(camera_dialog, text="Select", 
              command=select_camera).pack(pady=20)
    
    # Wait for dialog to close
    root.wait_window(camera_dialog)
    
    return result[0]
