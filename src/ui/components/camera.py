import cv2
import numpy as np
import PIL.Image, PIL.ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

from src.utils.config import config
from src.ui.dialogs.camera_dialog import change_camera

class CameraComponent:
    """
    Component for handling camera operations and display.
    """
    def __init__(self, parent, gui):
        """
        Initialize the camera component.
        
        Parameters:
        - parent: parent frame
        - gui: ActionMotionGUI instance
        """
        self.parent = parent
        self.gui = gui
        
        # Camera variables
        self.camera_index = config.last_camera_index
        self.cap = None
        self.is_running = False
        self.frame_failures = 0
        
        # Create camera frame to control size
        self.camera_frame = ttk.Frame(parent, width=640, height=480)
        self.camera_frame.pack(fill=tk.BOTH, expand=True)
        self.camera_frame.pack_propagate(False)  # Prevent frame from resizing to fit content
        
        # Create camera view
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)
    
    def start_camera(self):
        """Start the camera capture."""
        # Initialize camera
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Try to set camera properties
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 60)
        
        if not self.cap.isOpened():
            if messagebox.askyesno("Camera Error", 
                                    f"Could not open camera {self.camera_index}. Would you like to select another camera?"):
                # Show camera selection dialog
                new_index = change_camera(self.gui.root, self.camera_index)
                self.change_camera(new_index)
                return
            else:
                # Try default camera as fallback
                self.camera_index = 0
                config.last_camera_index = 0
                config.save_settings()
                # Try default camera
                self.cap = cv2.VideoCapture(0)
                
                # Try to set camera properties
                if self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.cap.set(cv2.CAP_PROP_FPS, 60)
                
                if not self.cap.isOpened():
                    if messagebox.askyesno("Camera Error", 
                                           "Failed to open default camera. Would you like to select another camera?"):
                        # Show camera selection dialog
                        new_index = change_camera(self.gui.root, self.camera_index)
                        self.change_camera(new_index)
                        return
                    else:
                        messagebox.showinfo("No Camera", 
                                            "The application will run without camera. Some features may not work.")
                        # Continue without camera
                        self.gui.status_label.config(text="No camera available")
                        return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_frame)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        self.gui.status_label.config(text="Camera started")
        self.gui.camera_label_status.config(text=f"Camera: {self.camera_index}")
    
    def stop_camera(self):
        """Stop the camera capture."""
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def change_camera(self, new_index):
        """
        Change to a different camera.
        
        Parameters:
        - new_index: new camera index
        """
        self.stop_camera()
        self.camera_index = new_index
        config.last_camera_index = new_index
        config.save_settings()
        self.start_camera()
    
    def read_frame(self):
        """
        Read a frame from the camera.
        
        Returns:
        - success: whether frame was read successfully
        - image: the frame image (or black image if no camera)
        """
        # Initialize default image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        height, width = image.shape[:2]
        
        success = False
        if self.cap is None:
            # Show "No Camera" message on black background
            cv2.putText(image, "No Camera Available", (width//2 - 100, height//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            try:
                success, frame = self.cap.read()
                if success:
                    image = frame
            except Exception as e:
                print(f"Error reading from camera: {e}")
                return False, image
        
        return success, image
    
    def _update_frame(self):
        """Update the camera frame continuously."""
        while self.is_running:
            success, image = self.read_frame()
            
            if self.cap is not None and not success:
                self.gui.status_label.config(text="Failed to capture image from camera")
                # If we consistently fail to get frames, offer to change camera
                self.frame_failures += 1
                
                if self.frame_failures > 30:  # About 3 seconds of failures
                    self.frame_failures = 0
                    # Ask in the main thread
                    self.gui.root.after(0, self._handle_camera_failure)
                    time.sleep(1)  # Wait a bit before trying again
                else:
                    time.sleep(0.1)
                continue
            
            # Reset failure counter on success
            self.frame_failures = 0
            
            try:
                # Process frame with gesture detection
                image = self.gui.process_frame(image)
                
                # Get frame dimensions once
                frame_width = self.camera_frame.winfo_width()
                frame_height = self.camera_frame.winfo_height()
                
                if frame_width > 1 and frame_height > 1:  # Ensure valid dimensions
                    # Calculate target size maintaining aspect ratio
                    img_height, img_width = image.shape[:2]
                    scale = min(frame_width/img_width, frame_height/img_height)
                    
                    if scale != 1:
                        # Only resize if needed
                        new_width = int(img_width * scale)
                        new_height = int(img_height * scale)
                        image = cv2.resize(image, (new_width, new_height), 
                                        interpolation=cv2.INTER_NEAREST)  # Faster interpolation
                
                # Convert to RGB
                if image.shape[-1] == 3:  # Only convert if BGR
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Create PIL image and convert to Tkinter format in one step
                tk_image = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(image))
                
                # Update label using root's after method to avoid thread issues
                self.gui.root.after(0, self._update_label, tk_image)
            except Exception as e:
                print(f"Error updating frame: {e}")
    
    def _update_label(self, tk_image):
        """Update label with new image."""
        self.camera_label.configure(image=tk_image)
        self.camera_label.image = tk_image  # Keep a reference
    
    def _handle_camera_failure(self):
        """Handle persistent camera failures by offering to change camera."""
        if messagebox.askyesno("Camera Problem", 
                              "There seems to be a problem with the current camera. Would you like to select another camera?"):
            self.gui.change_camera()
