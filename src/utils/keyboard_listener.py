import threading
from pynput import keyboard

class KeyboardListener:
    """
    Class for listening to keyboard events and capturing key presses.
    """
    def __init__(self):
        """
        Initialize the keyboard listener.
        """
        self.current_key = None
        self.is_listening = False
        self.listener = None
        self.callback = None
    
    def on_press(self, key):
        """
        Callback function for key press events.
        
        Parameters:
        - key: the key that was pressed
        """
        try:
            # For regular keys
            key_char = key.char
        except AttributeError:
            # For special keys
            key_char = str(key)
        
        self.current_key = key_char
        
        # Call the callback function if one is set
        if self.callback:
            self.callback(key_char)
    
    def start_listening(self, callback=None):
        """
        Start listening for keyboard events.
        
        Parameters:
        - callback: function to call when a key is pressed
        """
        if self.is_listening:
            return
        
        self.callback = callback
        self.is_listening = True
        
        # Start the listener in a separate thread
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.daemon = True
        self.listener.start()
    
    def stop_listening(self):
        """
        Stop listening for keyboard events.
        """
        if not self.is_listening:
            return
        
        self.is_listening = False
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def get_key(self, prompt="Press any key: ", timeout=None):
        """
        Wait for a key press and return the key.
        
        Parameters:
        - prompt: message to display
        - timeout: time to wait for a key press (in seconds)
        
        Returns:
        - the key that was pressed, or None if timeout
        """
        print(prompt, end='', flush=True)
        
        self.current_key = None
        self.start_listening()
        
        # Wait for a key press or timeout
        if timeout:
            timer = threading.Timer(timeout, self.stop_listening)
            timer.start()
        
        # Wait for a key press
        while self.is_listening and self.current_key is None:
            pass
        
        # Stop the timer if it's still running
        if timeout and timer.is_alive():
            timer.cancel()
        
        self.stop_listening()
        print(self.current_key if self.current_key else "Timeout")
        
        return self.current_key

def get_key_press(prompt="Press a key: "):
    """
    Utility function to get a single key press.
    
    Parameters:
    - prompt: message to display
    
    Returns:
    - the key that was pressed
    """
    listener = KeyboardListener()
    return listener.get_key(prompt)
