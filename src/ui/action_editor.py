from src.gestures.detector import GestureDetector
from src.utils.keyboard_listener import get_key_press

def edit_actions(detector, gesture_name=None):
    """
    Command-line interface for managing gesture actions.
    
    Parameters:
    - detector: GestureDetector instance
    - gesture_name: name of the gesture to edit (if None, allows choosing)
    
    Returns:
    - True if an edit was made, False otherwise
    """
    # If no gesture was specified, show list for selection
    if gesture_name is None:
        print("\n=== Action Editor ===")
        
        # List available gestures
        gestures = detector.list_gestures()
        if not gestures:
            print("No gestures registered. Register a gesture first.")
            return False
        
        print("\nAvailable gestures:")
        for i, (name, description) in enumerate(gestures):
            # Check if it has an associated action
            has_action = "acao" in detector.gestures[name] and detector.gestures[name]["acao"] is not None
            action_status = "With action" if has_action else "No action"
            print(f"{i+1}. {name}: {description} [{action_status}]")
        
        # Request user selection
        try:
            choice = int(input("\nEnter the number of the gesture to edit (0 to cancel): "))
            if choice == 0:
                return False
            
            if 1 <= choice <= len(gestures):
                gesture_name = gestures[choice - 1][0]
            else:
                print("Invalid gesture number.")
                return False
        except ValueError:
            print("Invalid input.")
            return False
    
    # Check if the gesture exists
    if gesture_name not in detector.gestures:
        print(f"Gesture '{gesture_name}' not found.")
        return False
    
    # Options menu for the selected gesture
    while True:
        print(f"\n=== Editing Actions for Gesture: {gesture_name} ===")
        
        # Check if it already has an associated action
        has_action = "acao" in detector.gestures[gesture_name] and detector.gestures[gesture_name]["acao"] is not None
        
        if has_action:
            action = detector.gestures[gesture_name]["acao"]
            action_type = action.get("tipo", "")
            parameters = action.get("parametros", {})
            
            print(f"Current action: {action_type}")
            print(f"Parameters: {parameters}")
            
            print("\nOptions:")
            print("1. Edit action")
            print("2. Remove action")
            print("3. Back")
            
            try:
                option = int(input("\nChoose an option: "))
                
                if option == 1:
                    # Edit existing action
                    if _define_new_action(detector, gesture_name):
                        return True
                elif option == 2:
                    # Remove action
                    if detector.remove_action(gesture_name):
                        return True
                elif option == 3:
                    # Return to previous menu
                    return False
                else:
                    print("Invalid option.")
            except ValueError:
                print("Invalid input.")
        else:
            print("This gesture has no associated action.")
            
            print("\nOptions:")
            print("1. Add action")
            print("2. Back")
            
            try:
                option = int(input("\nChoose an option: "))
                
                if option == 1:
                    # Add new action
                    if _define_new_action(detector, gesture_name):
                        return True
                elif option == 2:
                    # Return to previous menu
                    return False
                else:
                    print("Invalid option.")
            except ValueError:
                print("Invalid input.")


def _define_new_action(detector, gesture_name):
    """
    Interface for defining a new action for a gesture.
    
    Parameters:
    - detector: GestureDetector instance
    - gesture_name: name of the gesture to associate the action with
    
    Returns:
    - True if the action was defined, False otherwise
    """
    print("\n=== Define New Action ===")
    print("Available action types:")
    print("1. Keyboard action")
    print("2. Mouse action")
    print("3. Back")
    
    try:
        selected_type = int(input("\nChoose action type: "))
        
        if selected_type == 1:
            # Keyboard action
            keyboard_actions = detector.list_available_actions()["keyboard"]
            
            print("\nAvailable keyboard actions:")
            for i, action in enumerate(keyboard_actions):
                print(f"{i+1}. {action['name']}")
            print(f"{len(keyboard_actions)+1}. Type text")
            print(f"{len(keyboard_actions)+2}. Custom key")
            
            action_choice = int(input("\nChoose action: "))
            
            if 1 <= action_choice <= len(keyboard_actions):
                # Predefined action
                key = keyboard_actions[action_choice-1]["id"]
                parameters = {"key": key}
                return detector.associate_action(gesture_name, "keyboard", parameters)
                
            elif action_choice == len(keyboard_actions)+1:
                # Type text
                text = input("\nEnter the text to be typed: ")
                parameters = {"text": text}
                return detector.associate_action(gesture_name, "keyboard", parameters)
                
            elif action_choice == len(keyboard_actions)+2:
                # Custom key
                print("\nPress the key you want to associate with this gesture...")
                key = get_key_press()
                parameters = {"key": key}
                return detector.associate_action(gesture_name, "keyboard", parameters)
                
            else:
                print("Invalid option.")
                return False
                
        elif selected_type == 2:
            # Mouse action
            mouse_actions = detector.list_available_actions()["mouse"]
            
            print("\nAvailable mouse actions:")
            for i, action in enumerate(mouse_actions):
                print(f"{i+1}. {action['name']}")
            print(f"{len(mouse_actions)+1}. Move mouse to position")
            
            action_choice = int(input("\nChoose action: "))
            
            if 1 <= action_choice <= len(mouse_actions):
                # Predefined action
                mouse_action = mouse_actions[action_choice-1]["id"]
                parameters = {"action": mouse_action}
                return detector.associate_action(gesture_name, "mouse", parameters)
                
            elif action_choice == len(mouse_actions)+1:
                # Move mouse
                try:
                    x = int(input("\nEnter X coordinate: "))
                    y = int(input("Enter Y coordinate: "))
                    move_type = input("Absolute (a) or relative (r) movement? ").lower()
                    
                    absolute = move_type == "a"
                    parameters = {"x": x, "y": y, "absolute": absolute}
                    return detector.associate_action(gesture_name, "mouse", parameters)
                except ValueError:
                    print("Invalid coordinates.")
                    return False
            else:
                print("Invalid option.")
                return False
                
        elif selected_type == 3:
            # Back
            return False
            
        else:
            print("Invalid option.")
            return False
            
    except ValueError:
        print("Invalid input.")
        return False
