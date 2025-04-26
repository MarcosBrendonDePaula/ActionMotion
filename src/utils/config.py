"""
Configuration module for ActionMotion.
"""

class Config:
    """
    Configuration class to store application settings.
    """
    def __init__(self):
        # Detection settings
        self.enable_hand_detection = True
        self.enable_pose_detection = True
        
        # Display settings
        self.show_fps = True
        self.show_landmarks = True
        self.show_actions = True
        
        # Camera settings
        self.camera_index = 0
        
        # Window settings
        self.window_width = 1280
        self.window_height = 720
        
        # Detection sensitivity
        self.similarity_threshold = 0.85
        self.confidence_threshold = 0.90  # Higher threshold for more confident detections
        
        # Action settings
        self.time_between_actions = 1.0  # seconds
    
    def toggle_hand_detection(self):
        """Toggle hand detection on/off."""
        self.enable_hand_detection = not self.enable_hand_detection
        return self.enable_hand_detection
    
    def toggle_pose_detection(self):
        """Toggle pose detection on/off."""
        self.enable_pose_detection = not self.enable_pose_detection
        return self.enable_pose_detection
    
    def toggle_fps_display(self):
        """Toggle FPS display on/off."""
        self.show_fps = not self.show_fps
        return self.show_fps
    
    def toggle_landmarks_display(self):
        """Toggle landmarks display on/off."""
        self.show_landmarks = not self.show_landmarks
        return self.show_landmarks
    
    def toggle_actions_display(self):
        """Toggle actions display on/off."""
        self.show_actions = not self.show_actions
        return self.show_actions
    
    def set_camera_index(self, index):
        """Set camera index."""
        self.camera_index = index
        return self.camera_index
    
    def set_window_size(self, width, height):
        """Set window size."""
        self.window_width = width
        self.window_height = height
        return (self.window_width, self.window_height)
    
    def set_similarity_threshold(self, threshold):
        """Set similarity threshold for gesture detection."""
        self.similarity_threshold = max(0.0, min(1.0, threshold))
        return self.similarity_threshold
    
    def set_confidence_threshold(self, threshold):
        """Set confidence threshold for reducing false positives."""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        return self.confidence_threshold
    
    def set_time_between_actions(self, seconds):
        """Set minimum time between action executions."""
        self.time_between_actions = max(0.1, seconds)
        return self.time_between_actions
    
    def get_status(self):
        """Get a dictionary with the current configuration status."""
        return {
            "Hand Detection": "Enabled" if self.enable_hand_detection else "Disabled",
            "Pose Detection": "Enabled" if self.enable_pose_detection else "Disabled",
            "FPS Display": "Enabled" if self.show_fps else "Disabled",
            "Landmarks Display": "Enabled" if self.show_landmarks else "Disabled",
            "Actions Display": "Enabled" if self.show_actions else "Disabled",
            "Camera Index": self.camera_index,
            "Window Size": f"{self.window_width}x{self.window_height}",
            "Similarity Threshold": f"{self.similarity_threshold:.2f}",
            "Confidence Threshold": f"{self.confidence_threshold:.2f}",
            "Time Between Actions": f"{self.time_between_actions:.1f}s"
        }

# Create a global configuration instance
config = Config()
