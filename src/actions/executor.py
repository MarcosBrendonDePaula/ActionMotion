import time
import threading
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

class ActionExecutor:
    """
    Class responsible for executing keyboard and mouse actions.
    """
    def __init__(self):
        """
        Initialize the action executor.
        """
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        
        # Dictionary of predefined actions
        self.predefined_actions = {
            # Keyboard actions
            "key_enter": self._key_enter,
            "key_space": self._key_space,
            "key_esc": self._key_esc,
            "key_ctrl_c": self._key_ctrl_c,
            "key_ctrl_v": self._key_ctrl_v,
            "key_alt_tab": self._key_alt_tab,
            
            # Slide controls
            "slide_next": self._slide_next,
            "slide_previous": self._slide_previous,
            "slide_start": self._slide_start,
            "slide_end": self._slide_end,
            
            # Mouse actions
            "left_click": self._left_click,
            "right_click": self._right_click,
            "double_click": self._double_click,
            "scroll_up": self._scroll_up,
            "scroll_down": self._scroll_down,
        }
        
        # Registry of custom actions
        self.custom_actions = {}
        
        # Flag to control continuous execution
        self.executing_continuous = False
    
    # === Keyboard actions ===
    def _key_enter(self):
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
    
    def _key_space(self):
        self.keyboard.press(Key.space)
        self.keyboard.release(Key.space)
    
    def _key_esc(self):
        self.keyboard.press(Key.esc)
        self.keyboard.release(Key.esc)
    
    def _key_ctrl_c(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press('c')
        self.keyboard.release('c')
        self.keyboard.release(Key.ctrl)
    
    def _key_ctrl_v(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press('v')
        self.keyboard.release('v')
        self.keyboard.release(Key.ctrl)
    
    def _key_alt_tab(self):
        self.keyboard.press(Key.alt)
        self.keyboard.press(Key.tab)
        self.keyboard.release(Key.tab)
        self.keyboard.release(Key.alt)
    
    # === Slide presentation controls ===
    def _slide_next(self):
        """
        Move to the next slide (right arrow, Page Down, space, or N)
        """
        # Option 1: Right arrow
        self.keyboard.press(Key.right)
        self.keyboard.release(Key.right)
    
    def _slide_previous(self):
        """
        Move to the previous slide (left arrow, Page Up, or P)
        """
        # Option 1: Left arrow
        self.keyboard.press(Key.left)
        self.keyboard.release(Key.left)
    
    def _slide_start(self):
        """
        Go to the first slide (Home)
        """
        self.keyboard.press(Key.home)
        self.keyboard.release(Key.home)
    
    def _slide_end(self):
        """
        Go to the last slide (End)
        """
        self.keyboard.press(Key.end)
        self.keyboard.release(Key.end)
    
    # === Mouse actions ===
    def _left_click(self):
        self.mouse.click(Button.left)
    
    def _right_click(self):
        self.mouse.click(Button.right)
    
    def _double_click(self):
        self.mouse.click(Button.left, 2)
    
    def _scroll_up(self):
        self.mouse.scroll(0, 2)
    
    def _scroll_down(self):
        self.mouse.scroll(0, -2)
    
    def type_text(self, text):
        """
        Type text character by character.
        
        Parameters:
        - text: text to be typed
        """
        for char in text:
            self.keyboard.press(char)
            self.keyboard.release(char)
            time.sleep(0.01)  # Small delay to simulate real typing
    
    def press_key(self, key):
        """
        Press a specific key.
        
        Parameters:
        - key: the key to press (can be a string or a Key object)
        """
        # Handle special keys in string format
        if isinstance(key, str):
            # Check for special key names
            special_keys = {
                'Key.alt': Key.alt,
                'Key.alt_l': Key.alt_l,
                'Key.alt_r': Key.alt_r,
                'Key.alt_gr': Key.alt_gr,
                'Key.backspace': Key.backspace,
                'Key.caps_lock': Key.caps_lock,
                'Key.cmd': Key.cmd,
                'Key.cmd_l': Key.cmd_l,
                'Key.cmd_r': Key.cmd_r,
                'Key.ctrl': Key.ctrl,
                'Key.ctrl_l': Key.ctrl_l,
                'Key.ctrl_r': Key.ctrl_r,
                'Key.delete': Key.delete,
                'Key.down': Key.down,
                'Key.end': Key.end,
                'Key.enter': Key.enter,
                'Key.esc': Key.esc,
                'Key.f1': Key.f1,
                'Key.f2': Key.f2,
                'Key.f3': Key.f3,
                'Key.f4': Key.f4,
                'Key.f5': Key.f5,
                'Key.f6': Key.f6,
                'Key.f7': Key.f7,
                'Key.f8': Key.f8,
                'Key.f9': Key.f9,
                'Key.f10': Key.f10,
                'Key.f11': Key.f11,
                'Key.f12': Key.f12,
                'Key.home': Key.home,
                'Key.insert': Key.insert,
                'Key.left': Key.left,
                'Key.menu': Key.menu,
                'Key.num_lock': Key.num_lock,
                'Key.page_down': Key.page_down,
                'Key.page_up': Key.page_up,
                'Key.pause': Key.pause,
                'Key.print_screen': Key.print_screen,
                'Key.right': Key.right,
                'Key.scroll_lock': Key.scroll_lock,
                'Key.shift': Key.shift,
                'Key.shift_l': Key.shift_l,
                'Key.shift_r': Key.shift_r,
                'Key.space': Key.space,
                'Key.tab': Key.tab,
                'Key.up': Key.up
            }
            
            if key in special_keys:
                # It's a special key
                self.keyboard.press(special_keys[key])
                self.keyboard.release(special_keys[key])
            elif key.startswith('Key.'):
                # Try to get it as a special key
                try:
                    key_name = key[4:]  # Remove 'Key.' prefix
                    key_obj = getattr(Key, key_name)
                    self.keyboard.press(key_obj)
                    self.keyboard.release(key_obj)
                except (AttributeError, KeyError):
                    print(f"Unknown special key: {key}")
            elif len(key) > 1:
                # If it's a multi-character string but not a special key,
                # press each character individually
                for char in key:
                    self.keyboard.press(char)
                    self.keyboard.release(char)
                    time.sleep(0.05)
            else:
                # Single character
                self.keyboard.press(key)
                self.keyboard.release(key)
        else:
            # Already a Key object or other type
            self.keyboard.press(key)
            self.keyboard.release(key)
    
    def move_mouse(self, x, y, absolute=False):
        """
        Move the mouse cursor to a position.
        
        Parameters:
        - x, y: destination coordinates
        - absolute: if True, move to absolute screen position;
                   if False, move relative to current position
        """
        if absolute:
            self.mouse.position = (x, y)
        else:
            current_x, current_y = self.mouse.position
            self.mouse.position = (current_x + x, current_y + y)
    
    def register_custom_action(self, name, function):
        """
        Register a custom action.
        
        Parameters:
        - name: action name
        - function: function to execute
        """
        self.custom_actions[name] = function
    
    def execute_action(self, action_type, parameters=None):
        """
        Execute an action based on type and parameters.
        
        Parameters:
        - action_type: string identifying the action type
        - parameters: additional action parameters
        
        Returns:
        - True if the action was executed successfully, False otherwise
        """
        # If no parameters, initialize as empty dictionary
        if parameters is None:
            parameters = {}
        
        try:
            # Check action type
            if action_type == "keyboard":
                # Keyboard action
                key = parameters.get("key", "")
                if key:
                    if key in self.predefined_actions:
                        # Predefined action
                        self.predefined_actions[key]()
                    else:
                        # Custom key press
                        self.press_key(key)
                
                # If there's text to type
                text = parameters.get("text", "")
                if text:
                    self.type_text(text)
                
            elif action_type == "slide":
                # Slide control action
                action = parameters.get("action", "")
                command = f"slide_{action}" if action else ""
                if command in self.predefined_actions:
                    self.predefined_actions[command]()
                else:
                    # Custom key for slide control
                    key = parameters.get("key", "")
                    if key:
                        self.press_key(key)
            
            elif action_type == "mouse":
                # Mouse action
                action = parameters.get("action", "")
                if action in self.predefined_actions:
                    self.predefined_actions[action]()
                
                # If there's a position to move to
                if "x" in parameters and "y" in parameters:
                    absolute = parameters.get("absolute", False)
                    self.move_mouse(parameters["x"], parameters["y"], absolute)
            
            elif action_type == "custom":
                # Custom action
                action_name = parameters.get("name", "")
                if action_name in self.custom_actions:
                    self.custom_actions[action_name]()
            
            else:
                print(f"Unknown action type: {action_type}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error executing action {action_type}: {e}")
            return False
    
    def start_continuous_execution(self, action_type, parameters=None, interval=1.0):
        """
        Start continuous execution of an action in a loop.
        
        Parameters:
        - action_type: string identifying the action type
        - parameters: additional action parameters
        - interval: time in seconds between executions
        """
        # Stop previous execution if it exists
        self.stop_continuous_execution()
        
        # Start new execution
        self.executing_continuous = True
        
        # Create thread for continuous execution
        def execution_loop():
            while self.executing_continuous:
                self.execute_action(action_type, parameters)
                time.sleep(interval)
        
        # Start thread
        thread = threading.Thread(target=execution_loop)
        thread.daemon = True
        thread.start()
    
    def stop_continuous_execution(self):
        """
        Stop continuous execution of actions.
        """
        self.executing_continuous = False
    
    def list_available_actions(self):
        """
        List all available predefined actions.
        
        Returns:
        - dictionary with action groups
        """
        actions = {
            "keyboard": [
                {"id": "key_enter", "name": "Enter Key"},
                {"id": "key_space", "name": "Space Key"},
                {"id": "key_esc", "name": "ESC Key"},
                {"id": "key_ctrl_c", "name": "Ctrl+C (Copy)"},
                {"id": "key_ctrl_v", "name": "Ctrl+V (Paste)"},
                {"id": "key_alt_tab", "name": "Alt+Tab (Switch windows)"}
            ],
            "slides": [
                {"id": "slide_next", "name": "Next Slide (Right Arrow)"},
                {"id": "slide_previous", "name": "Previous Slide (Left Arrow)"},
                {"id": "slide_start", "name": "First Slide (Home)"},
                {"id": "slide_end", "name": "Last Slide (End)"}
            ],
            "mouse": [
                {"id": "left_click", "name": "Left Click"},
                {"id": "right_click", "name": "Right Click"},
                {"id": "double_click", "name": "Double Click"},
                {"id": "scroll_up", "name": "Scroll Up"},
                {"id": "scroll_down", "name": "Scroll Down"}
            ]
        }
        
        # Add custom actions
        if self.custom_actions:
            actions["custom"] = [
                {"id": name, "name": name} for name in self.custom_actions.keys()
            ]
        
        return actions
