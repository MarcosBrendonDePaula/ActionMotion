import os
import json
import numpy as np
import cv2
import time
from src.actions.executor import ActionExecutor
from src.utils.config import config

class GestureDetector:
    """
    Class responsible for detecting and managing gestures.
    """
    def __init__(self, gestures_directory="gestos"):
        """
        Initialize the gesture detector.
        
        Parameters:
        - gestures_directory: directory where gestures will be saved
        """
        self.gestures_directory = gestures_directory
        self.gestures_file = os.path.join(gestures_directory, "gestos.json")
        self.gestures = {}
        
        # Initialize action executor
        self.executor = ActionExecutor()
        
        # Registry of actions being executed
        self.actions_in_execution = {}
        
        # Minimum time between executions of the same action (in seconds)
        self.min_time_between_actions = config.time_between_actions
        self.last_execution = {}
        
        # Create directory if it doesn't exist
        if not os.path.exists(gestures_directory):
            os.makedirs(gestures_directory)
            
        # Load saved gestures if they exist
        if os.path.exists(self.gestures_file):
            try:
                with open(self.gestures_file, 'r', encoding='utf-8') as f:
                    self.gestures = json.load(f)
                print(f"Loaded {len(self.gestures)} gestures from file.")
            except Exception as e:
                print(f"Error loading gestures: {e}")
                self.gestures = {}
    
    def capture_gesture(self, hands, pose):
        """
        Capture the current state of hands and pose to create a new gesture.
        
        Parameters:
        - hands: list with information about detected hands
        - pose: list with pose landmarks
        
        Returns:
        - dictionary with the captured state
        """
        capture = {
            "hands": [],
            "pose": []
        }
        
        # Capture hands state
        for hand in hands:
            capture["hands"].append({
                "type": hand.get("type", "Unknown"),
                "landmarks": hand["landmarks"]
            })
        
        # Capture pose
        if pose:
            capture["pose"] = pose
            
        return capture
    
    def save_gesture(self, name, description, capture, action=None):
        """
        Save a new gesture to the file.
        
        Parameters:
        - name: gesture name
        - description: gesture description
        - capture: captured gesture data
        - action: dictionary with action information (optional)
        
        Returns:
        - True if saved successfully, False otherwise
        """
        try:
            # Add the new gesture to the dictionary
            self.gestures[name] = {
                "descricao": description,
                "captura": capture,
                "acao": action
            }
            
            # Save to file
            with open(self.gestures_file, 'w', encoding='utf-8') as f:
                json.dump(self.gestures, f, indent=2, ensure_ascii=False)
            
            print(f"Gesture '{name}' saved successfully!")
            return True
        except Exception as e:
            print(f"Error saving gesture: {e}")
            return False
    
    def remove_gesture(self, name):
        """
        Remove a gesture from the file.
        
        Parameters:
        - name: name of the gesture to remove
        
        Returns:
        - True if removed successfully, False otherwise
        """
        if name in self.gestures:
            try:
                del self.gestures[name]
                
                # Update file
                with open(self.gestures_file, 'w', encoding='utf-8') as f:
                    json.dump(self.gestures, f, indent=2, ensure_ascii=False)
                
                print(f"Gesture '{name}' removed successfully!")
                return True
            except Exception as e:
                print(f"Error removing gesture: {e}")
                return False
        else:
            print(f"Gesture '{name}' not found.")
            return False
    
    def associate_action(self, gesture_name, action_type, parameters):
        """
        Associate an action with an already registered gesture.
        
        Parameters:
        - gesture_name: gesture name
        - action_type: action type (keyboard, mouse, custom)
        - parameters: action parameters
        
        Returns:
        - True if associated successfully, False otherwise
        """
        if gesture_name not in self.gestures:
            print(f"Gesture '{gesture_name}' not found.")
            return False
            
        try:
            # Create action object
            action = {
                "tipo": action_type,
                "parametros": parameters
            }
            
            # Associate with the gesture
            self.gestures[gesture_name]["acao"] = action
            
            # Save to file
            with open(self.gestures_file, 'w', encoding='utf-8') as f:
                json.dump(self.gestures, f, indent=2, ensure_ascii=False)
            
            print(f"Action associated with gesture '{gesture_name}' successfully!")
            return True
        except Exception as e:
            print(f"Error associating action: {e}")
            return False
    
    def remove_action(self, gesture_name):
        """
        Remove the action associated with a gesture.
        
        Parameters:
        - gesture_name: gesture name
        
        Returns:
        - True if removed successfully, False otherwise
        """
        if gesture_name not in self.gestures:
            print(f"Gesture '{gesture_name}' not found.")
            return False
            
        if "acao" not in self.gestures[gesture_name]:
            print(f"Gesture '{gesture_name}' has no associated action.")
            return False
            
        try:
            # Remove action
            del self.gestures[gesture_name]["acao"]
            
            # Save to file
            with open(self.gestures_file, 'w', encoding='utf-8') as f:
                json.dump(self.gestures, f, indent=2, ensure_ascii=False)
            
            print(f"Action removed from gesture '{gesture_name}' successfully!")
            return True
        except Exception as e:
            print(f"Error removing action: {e}")
            return False
    
    def calculate_similarity(self, landmarks1, landmarks2, type="hand"):
        """
        Calculate similarity between two sets of landmarks.
        
        Parameters:
        - landmarks1: first set of landmarks
        - landmarks2: second set of landmarks
        - type: landmark type ('hand' or 'pose')
        
        Returns:
        - similarity value (0 to 1, where 1 is identical)
        """
        if not landmarks1 or not landmarks2:
            return 0
        
        # Extract coordinates
        points1 = np.array([[lm[1], lm[2]] for lm in landmarks1])
        points2 = np.array([[lm[1], lm[2]] for lm in landmarks2])
        
        # Check if they have the same number of points
        if len(points1) != len(points2):
            # If the number of points is different, one hand might have more detected landmarks than the other
            # We'll use the common landmarks
            min_points = min(len(points1), len(points2))
            points1 = points1[:min_points]
            points2 = points2[:min_points]
        
        # Normalize to remove scale and position effects
        points1 = self._normalize_points(points1)
        points2 = self._normalize_points(points2)
        
        # Calculate average distance between corresponding points
        distances = np.sqrt(np.sum((points1 - points2) ** 2, axis=1))
        average_distance = np.mean(distances)
        
        # Convert distance to similarity (1 - normalized distance)
        # The smaller the distance, the higher the similarity
        similarity = max(0, 1 - (average_distance / 2.0))
        
        return similarity
    
    def _normalize_points(self, points):
        """
        Normalize a set of points to remove scale and position effects.
        
        Parameters:
        - points: numpy array with coordinates (x, y)
        
        Returns:
        - normalized points
        """
        # Remove translation: subtract the centroid
        center = np.mean(points, axis=0)
        centered_points = points - center
        
        # Remove scale effect: divide by average distance to center
        distances = np.sqrt(np.sum(centered_points ** 2, axis=1))
        average_distance = np.mean(distances)
        
        # Avoid division by zero
        if average_distance < 0.0001:
            return centered_points
        
        return centered_points / average_distance
    
    def detect_gestures(self, hands, pose, similarity_threshold=0.85):
        """
        Detect which gestures are being performed based on current landmarks.
        
        Parameters:
        - hands: list with information about detected hands
        - pose: list with pose landmarks
        - similarity_threshold: minimum similarity value to consider a gesture detected
        
        Returns:
        - dictionary with detected gestures and their similarities
        """
        detected_gestures = {}
        
        # If we have no registered gestures, return empty
        if not self.gestures:
            return detected_gestures
        
        # For each registered gesture
        for gesture_name, gesture_info in self.gestures.items():
            capture = gesture_info.get("captura", {})
            best_similarity = 0
            has_match = False
            
            # Check hand similarity if the gesture requires hands
            if "hands" in capture and capture["hands"]:
                # If the gesture requires hands but no hands are detected, skip this gesture
                if not hands:
                    continue
                    
                for current_hand in hands:
                    for captured_hand in capture["hands"]:
                        # Check if they are the same type (left/right)
                        current_hand_type = current_hand.get("type", "")
                        captured_hand_type = captured_hand.get("type", "")
                        
                        # Only compare if hand types match (Left with Left, Right with Right)
                        if current_hand_type == captured_hand_type:
                            similarity = self.calculate_similarity(
                                current_hand["landmarks"], 
                                captured_hand["landmarks"],
                                "hand"
                            )
                            # Store the similarity score if it's above the threshold
                            if similarity >= similarity_threshold:
                                best_similarity = max(best_similarity, similarity)
                                # Only consider it a match if it's above the confidence threshold
                                if similarity >= config.confidence_threshold:
                                    has_match = True
                                    print(f"Hand match: {gesture_name} - {current_hand_type} hand - similarity: {similarity:.2f}")
                                else:
                                    print(f"Low confidence match: {gesture_name} - {current_hand_type} hand - similarity: {similarity:.2f}")
            
            # Check pose similarity if the gesture requires pose
            if "pose" in capture and capture["pose"]:
                # If the gesture requires pose but no pose is detected, skip this gesture
                if not pose:
                    continue
                    
                pose_similarity = self.calculate_similarity(
                    pose, 
                    capture["pose"],
                    "pose"
                )
                # Store the similarity score if it's above the threshold
                if pose_similarity >= similarity_threshold:
                    best_similarity = max(best_similarity, pose_similarity)
                    # Only consider it a match if it's above the confidence threshold
                    if pose_similarity >= config.confidence_threshold:
                        has_match = True
                        print(f"Pose match: {gesture_name} - similarity: {pose_similarity:.2f}")
                    else:
                        print(f"Low confidence pose match: {gesture_name} - similarity: {pose_similarity:.2f}")
            
            # Only consider the gesture detected if we have a match
            if has_match and best_similarity >= similarity_threshold:
                detected_gestures[gesture_name] = {
                    "descricao": gesture_info["descricao"],
                    "similaridade": best_similarity,
                    "acao": gesture_info.get("acao", None)
                }
                
                # Execute associated action, if it exists
                self._execute_gesture_action(gesture_name, gesture_info.get("acao", None))
        
        return detected_gestures
    
    def _execute_gesture_action(self, gesture_name, action):
        """
        Execute the action associated with a detected gesture.
        
        Parameters:
        - gesture_name: name of the detected gesture
        - action: action information to execute
        """
        # If no action, do nothing
        if not action:
            return
            
        # Check minimum time between executions
        current_time = time.time()
        if gesture_name in self.last_execution:
            time_since_last = current_time - self.last_execution[gesture_name]
            if time_since_last < self.min_time_between_actions:
                # Too soon to execute again
                return
        
        # Execute the action
        action_type = action.get("tipo", "")
        parameters = action.get("parametros", {})
        
        if action_type:
            success = self.executor.execute_action(action_type, parameters)
            if success:
                # Register execution time
                self.last_execution[gesture_name] = current_time
                print(f"Executed action for gesture '{gesture_name}'")
    
    def list_available_actions(self):
        """
        List all available actions for association.
        
        Returns:
        - dictionary with available actions
        """
        return self.executor.list_available_actions()
    
    def list_gestures(self):
        """
        List all registered gestures.
        
        Returns:
        - list of tuples (name, description)
        """
        return [(name, info["descricao"]) for name, info in self.gestures.items()]
