import cv2
import mediapipe as mp
import numpy as np
import time
import os

# Suppress MediaPipe warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
import logging
logging.getLogger('absl').setLevel(logging.ERROR)  # Suppress absl logging

class MovementTracker:
    """
    Class responsible for tracking hand and body movements using MediaPipe.
    """
    def __init__(self, static_mode=False, max_hands=2, model_complexity=1, 
                 detection_confidence=0.5, tracking_confidence=0.5):
        """
        Initialize the movement tracker.
        
        Parameters:
        - static_mode: static (True) or tracking (False) mode
        - max_hands: maximum number of hands to track
        - model_complexity: model complexity level (0 or 1)
        - detection_confidence: minimum confidence threshold for detection
        - tracking_confidence: minimum confidence threshold for tracking
        """
        self.static_mode = static_mode
        self.max_hands = max_hands
        self.model_complexity = model_complexity
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        
        # Initialize MediaPipe modules
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.static_mode,
            max_num_hands=self.max_hands,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        
        # Initialize pose module
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=self.static_mode,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        
        # Variables for FPS calculation
        self.current_time = 0
        self.previous_time = 0
    
    def find_hands(self, image, draw=True):
        """
        Detect hands in the image.
        
        Parameters:
        - image: camera frame
        - draw: if True, draw landmarks on hands
        
        Returns:
        - processed image
        - list with information about detected hands
        """
        # Convert image to RGB (MediaPipe requires RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.hands_results = self.hands.process(rgb_image)
        all_hands = []
        
        height, width, _ = image.shape
        
        if self.hands_results.multi_hand_landmarks:
            for hand_id, hand_landmarks in enumerate(self.hands_results.multi_hand_landmarks):
                hand_info = {}
                landmark_points = []
                
                # Extract landmark coordinates
                for lm_id, lm in enumerate(hand_landmarks.landmark):
                    px, py = int(lm.x * width), int(lm.y * height)
                    landmark_points.append([lm_id, px, py])
                
                # Determine which hand (left or right)
                if self.hands_results.multi_handedness:
                    hand_info["type"] = self.hands_results.multi_handedness[hand_id].classification[0].label
                
                hand_info["landmarks"] = landmark_points
                all_hands.append(hand_info)
                
                # Draw landmarks and connections
                if draw:
                    self.mp_drawing.draw_landmarks(
                        image, 
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_styles.get_default_hand_landmarks_style(),
                        self.mp_styles.get_default_hand_connections_style()
                    )
        
        return image, all_hands
    
    def find_pose(self, image, draw=True):
        """
        Detect pose in the image.
        
        Parameters:
        - image: camera frame
        - draw: if True, draw pose landmarks
        
        Returns:
        - processed image
        - list with pose landmarks
        """
        # Convert image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.pose_results = self.pose.process(rgb_image)
        pose_landmarks = []
        
        height, width, _ = image.shape
        
        if self.pose_results.pose_landmarks:
            # Extract landmark coordinates
            for lm_id, lm in enumerate(self.pose_results.pose_landmarks.landmark):
                px, py = int(lm.x * width), int(lm.y * height)
                pose_landmarks.append([lm_id, px, py])
            
            # Draw landmarks and connections
            if draw:
                # Define custom style for connections
                connection_style = self.mp_drawing.DrawingSpec(
                    color=(0, 255, 0),  # Green color
                    thickness=2,        # Line thickness
                    circle_radius=1     # Circle radius at joints
                )
                
                self.mp_drawing.draw_landmarks(
                    image,
                    self.pose_results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_styles.get_default_pose_landmarks_style(),
                    connection_drawing_spec=connection_style
                )
                
        return image, pose_landmarks
    
    def calculate_fps(self):
        """
        Calculate frames per second.
        
        Returns:
        - FPS value
        """
        self.current_time = time.time()
        fps = 1 / (self.current_time - self.previous_time)
        self.previous_time = self.current_time
        return int(fps)
    
    def display_fps(self, image, fps):
        """
        Display FPS on the image.
        
        Parameters:
        - image: camera frame
        - fps: FPS value to display
        
        Returns:
        - image with FPS
        """
        cv2.putText(image, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return image
