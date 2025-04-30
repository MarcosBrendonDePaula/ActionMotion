import tkinter as tk
from tkinter import ttk, messagebox
from src.utils.config import config

class GestureDialogs:
    """
    Class to handle all gesture-related dialogs.
    """
    def __init__(self, root, detector):
        """
        Initialize the gesture dialogs.
        
        Parameters:
        - root: Tkinter root window
        - detector: GestureDetector instance
        """
        self.root = root
        self.detector = detector
    
    def show_capture_dialog(self, capture):
        """
        Show dialog to capture a gesture.
        
        Parameters:
        - capture: captured gesture data
        """
        # Create dialog
        capture_dialog = tk.Toplevel(self.root)
        capture_dialog.title("Capture Gesture")
        capture_dialog.geometry("400x300")
        capture_dialog.transient(self.root)
        capture_dialog.grab_set()
        
        ttk.Label(capture_dialog, text="Gesture Information", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(capture_dialog, text="Name (no spaces):").pack(anchor=tk.W, padx=20)
        name_entry = ttk.Entry(capture_dialog, width=40)
        name_entry.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(capture_dialog, text="Description:").pack(anchor=tk.W, padx=20)
        desc_entry = ttk.Entry(capture_dialog, width=40)
        desc_entry.pack(fill=tk.X, padx=20, pady=5)
        
        def save_gesture():
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            
            if not name:
                messagebox.showerror("Input Error", "Name cannot be empty")
                return
            
            if " " in name:
                messagebox.showerror("Input Error", "Name cannot contain spaces")
                return
            
            if not description:
                messagebox.showerror("Input Error", "Description cannot be empty")
                return
            
            # Save the gesture
            if self.detector.save_gesture(name, description, capture):
                messagebox.showinfo("Success", f"Gesture '{name}' saved successfully!")
                
                # Ask if want to associate an action
                if messagebox.askyesno("Associate Action", 
                                      "Do you want to associate an action with this gesture?"):
                    capture_dialog.destroy()
                    self.show_edit_dialog(name)
                else:
                    capture_dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save gesture")
        
        button_frame = ttk.Frame(capture_dialog)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Save", command=save_gesture).pack(side=tk.LEFT, padx=20)
        ttk.Button(button_frame, text="Cancel", 
                  command=capture_dialog.destroy).pack(side=tk.RIGHT, padx=20)
    
    def show_list_dialog(self):
        """Show dialog to list all registered gestures."""
        gestures = self.detector.list_gestures()
        
        if not gestures:
            messagebox.showinfo("Gestures", "No gestures registered.")
            return
        
        # Create gesture list dialog
        gesture_dialog = tk.Toplevel(self.root)
        gesture_dialog.title("Registered Gestures")
        gesture_dialog.geometry("500x400")
        gesture_dialog.transient(self.root)
        
        ttk.Label(gesture_dialog, text="Registered Gestures", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create scrollable frame
        container = ttk.Frame(gesture_dialog)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        container.pack(fill="both", expand=True, padx=10, pady=10)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add gesture information
        for i, (name, description) in enumerate(gestures):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5)
            
            # Check if it has an associated action
            has_action = "acao" in self.detector.gestures[name] and self.detector.gestures[name]["acao"] is not None
            action_status = "With action" if has_action else "No action"
            
            ttk.Label(frame, text=f"{i+1}. {name}", 
                     font=("Arial", 12, "bold")).pack(anchor=tk.W)
            
            ttk.Label(frame, text=f"Description: {description}").pack(anchor=tk.W)
            ttk.Label(frame, text=f"Status: {action_status}").pack(anchor=tk.W)
            
            # If it has an action, show details
            if has_action:
                action = self.detector.gestures[name]["acao"]
                ttk.Label(frame, 
                         text=f"Action: {action['tipo']} - {str(action['parametros'])}",
                         foreground="purple").pack(anchor=tk.W)
            
            # Determine hand type and direction if available
            hand_info = []
            for hand_data in self.detector.gestures.get(name, {}).get("captura", {}).get("hands", []):
                hand_type = hand_data.get("type", "Unknown")
                direction = hand_data.get("direction", "unknown")
                hand_info.append(f"{hand_type} hand ({direction})")
            
            if hand_info:
                ttk.Label(frame, 
                         text=f"Hand info: {', '.join(hand_info)}").pack(anchor=tk.W)
            
            ttk.Separator(scrollable_frame).pack(fill=tk.X, pady=5)
        
        # Add buttons at the bottom
        button_frame = ttk.Frame(gesture_dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Close", 
                  command=gesture_dialog.destroy).pack(side=tk.RIGHT, padx=10)
    
    def show_edit_dialog(self, gesture_name=None):
        """
        Show dialog to edit actions for a gesture.
        
        Parameters:
        - gesture_name: name of the gesture to edit (if None, allows choosing)
        """
        # If no gesture was specified, show list for selection
        if gesture_name is None:
            gestures = self.detector.list_gestures()
            
            if not gestures:
                messagebox.showinfo("Edit Actions", "No gestures registered. Register a gesture first.")
                return
            
            # Create gesture selection dialog
            selection_dialog = tk.Toplevel(self.root)
            selection_dialog.title("Select Gesture")
            selection_dialog.geometry("400x300")
            selection_dialog.transient(self.root)
            selection_dialog.grab_set()
            
            ttk.Label(selection_dialog, text="Select a Gesture to Edit", 
                     font=("Arial", 14, "bold")).pack(pady=10)
            
            # Create scrollable frame
            container = ttk.Frame(selection_dialog)
            canvas = tk.Canvas(container)
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            container.pack(fill="both", expand=True, padx=10, pady=10)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add gesture options
            for i, (name, description) in enumerate(gestures):
                # Check if it has an associated action
                has_action = "acao" in self.detector.gestures[name] and self.detector.gestures[name]["acao"] is not None
                action_status = "With action" if has_action else "No action"
                
                frame = ttk.Frame(scrollable_frame)
                frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(frame, text=f"{name}: {description} [{action_status}]").pack(side=tk.LEFT, padx=5)
                
                # Button frame for edit and delete buttons
                button_frame = ttk.Frame(frame)
                button_frame.pack(side=tk.RIGHT)
                
                # Edit button
                ttk.Button(button_frame, text="Edit", 
                          command=lambda n=name: [selection_dialog.destroy(), self.show_edit_dialog(n)]).pack(side=tk.LEFT, padx=2)
                
                # Delete button (only shown if the gesture has an action)
                if has_action:
                    def remove_action_func(gesture_name=name):
                        if messagebox.askyesno("Confirm Removal", 
                                              f"Are you sure you want to remove the action from gesture '{gesture_name}'?"):
                            if self.detector.remove_action(gesture_name):
                                messagebox.showinfo("Success", f"Action removed from gesture '{gesture_name}'")
                                selection_dialog.destroy()
                                self.show_edit_dialog()  # Refresh the dialog
                            else:
                                messagebox.showerror("Error", f"Failed to remove action from gesture '{gesture_name}'")
                    
                    ttk.Button(button_frame, text="Delete", 
                              command=lambda n=name: remove_action_func(n)).pack(side=tk.LEFT, padx=2)
            
            # Add cancel button
            button_frame = ttk.Frame(selection_dialog)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="Cancel", 
                      command=selection_dialog.destroy).pack(side=tk.RIGHT, padx=10)
            
            return
        
        # Check if the gesture exists
        if gesture_name not in self.detector.gestures:
            messagebox.showerror("Edit Actions", f"Gesture '{gesture_name}' not found.")
            return
        
        # Create action editor dialog
        action_dialog = tk.Toplevel(self.root)
        action_dialog.title(f"Edit Actions for {gesture_name}")
        action_dialog.geometry("500x400")
        action_dialog.transient(self.root)
        action_dialog.grab_set()
        
        ttk.Label(action_dialog, text=f"Editing Actions for: {gesture_name}", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Check if it already has an associated action
        has_action = "acao" in self.detector.gestures[gesture_name] and self.detector.gestures[gesture_name]["acao"] is not None
        
        if has_action:
            action = self.detector.gestures[gesture_name]["acao"]
            action_type = action.get("tipo", "")
            parameters = action.get("parametros", {})
            
            # Show current action
            current_frame = ttk.LabelFrame(action_dialog, text="Current Action")
            current_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Label(current_frame, text=f"Type: {action_type}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(current_frame, text=f"Parameters: {parameters}").pack(anchor=tk.W, padx=5, pady=2)
            
            # Add buttons for edit/remove
            button_frame = ttk.Frame(current_frame)
            button_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(button_frame, text="Edit Action", 
                      command=lambda: self._define_new_action(action_dialog, gesture_name)).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(button_frame, text="Remove Action", 
                      command=lambda: [
                          self.detector.remove_action(gesture_name),
                          messagebox.showinfo("Success", f"Action removed from gesture '{gesture_name}'"),
                          action_dialog.destroy()
                      ]).pack(side=tk.RIGHT, padx=5)
        else:
            # No action, show add button
            ttk.Label(action_dialog, text="This gesture has no associated action.").pack(pady=10)
            
            ttk.Button(action_dialog, text="Add Action", 
                      command=lambda: self._define_new_action(action_dialog, gesture_name)).pack(pady=10)
        
        # Add close button
        ttk.Button(action_dialog, text="Close", 
                  command=action_dialog.destroy).pack(side=tk.BOTTOM, pady=10)
    
    def _define_new_action(self, parent_dialog, gesture_name):
        """
        Define a new action for a gesture.
        
        Parameters:
        - parent_dialog: parent dialog to close
        - gesture_name: name of the gesture to associate the action with
        """
        # Close parent dialog
        parent_dialog.destroy()
        
        # Create action type selection dialog
        action_dialog = tk.Toplevel(self.root)
        action_dialog.title("Define New Action")
        action_dialog.geometry("400x300")
        action_dialog.transient(self.root)
        action_dialog.grab_set()
        
        ttk.Label(action_dialog, text="Select Action Type", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Action type selection
        action_type_frame = ttk.Frame(action_dialog)
        action_type_frame.pack(fill=tk.X, pady=10)
        
        action_type_var = tk.StringVar()
        
        ttk.Radiobutton(action_type_frame, text="Keyboard Action", 
                       variable=action_type_var, value="keyboard").pack(anchor=tk.W, padx=20, pady=2)
        
        ttk.Radiobutton(action_type_frame, text="Mouse Action", 
                       variable=action_type_var, value="mouse").pack(anchor=tk.W, padx=20, pady=2)
        
        # Set default
        action_type_var.set("keyboard")
        
        # Button to proceed
        def select_action_type():
            action_type = action_type_var.get()
            action_dialog.destroy()
            
            if action_type == "keyboard":
                self._define_keyboard_action(gesture_name)
            elif action_type == "mouse":
                self._define_mouse_action(gesture_name)
        
        ttk.Button(action_dialog, text="Next", 
                  command=select_action_type).pack(pady=10)
        
        ttk.Button(action_dialog, text="Cancel", 
                  command=action_dialog.destroy).pack(pady=5)
    
    def _define_keyboard_action(self, gesture_name):
        """
        Define a keyboard action for a gesture.
        
        Parameters:
        - gesture_name: name of the gesture to associate the action with
        """
        # Get available keyboard actions
        keyboard_actions = self.detector.list_available_actions()["keyboard"]
        
        # Create keyboard action dialog
        keyboard_dialog = tk.Toplevel(self.root)
        keyboard_dialog.title("Define Keyboard Action")
        keyboard_dialog.geometry("400x400")
        keyboard_dialog.transient(self.root)
        keyboard_dialog.grab_set()
        
        ttk.Label(keyboard_dialog, text="Select Keyboard Action", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create scrollable frame
        container = ttk.Frame(keyboard_dialog)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        container.pack(fill="both", expand=True, padx=10, pady=10)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action selection variable
        action_var = tk.StringVar()
        
        # Add predefined actions
        for i, action in enumerate(keyboard_actions):
            ttk.Radiobutton(scrollable_frame, text=action['name'], 
                           variable=action_var, value=f"predefined:{action['id']}").pack(anchor=tk.W, padx=5, pady=2)
        
        # Add custom options
        ttk.Separator(scrollable_frame).pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(scrollable_frame, text="Type text", 
                       variable=action_var, value="text").pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(scrollable_frame, text="Custom key", 
                       variable=action_var, value="custom").pack(anchor=tk.W, padx=5, pady=2)
        
        # Set default
        action_var.set("predefined:key_enter")
        
        # Text entry for custom text (initially hidden)
        text_frame = ttk.Frame(keyboard_dialog)
        text_label = ttk.Label(text_frame, text="Text to type:")
        text_entry = ttk.Entry(text_frame, width=30)
        
        # Key capture for custom key (initially hidden)
        key_frame = ttk.Frame(keyboard_dialog)
        key_label = ttk.Label(key_frame, text="Press a key:")
        key_value = ttk.Label(key_frame, text="No key pressed", foreground="gray")
        key_button = ttk.Button(key_frame, text="Capture Key")
        
        # Variable to store the captured key
        captured_key = [None]
        
        def capture_key():
            """Open a dialog to capture a key press."""
            key_dialog = tk.Toplevel(keyboard_dialog)
            key_dialog.title("Press a Key")
            key_dialog.geometry("300x150")
            key_dialog.transient(keyboard_dialog)
            key_dialog.grab_set()
            
            ttk.Label(key_dialog, text="Press any key on your keyboard", 
                     font=("Arial", 12)).pack(pady=20)
            
            key_result = ttk.Label(key_dialog, text="Waiting for key press...", 
                                  font=("Arial", 10, "italic"))
            key_result.pack(pady=10)
            
            # Use the keyboard listener from utils
            from src.utils.keyboard_listener import get_key_press
            
            def capture_thread():
                # Run in a separate thread to not block the UI
                key_name = get_key_press("")  # Empty prompt to avoid console output
                
                # Update UI in the main thread
                key_dialog.after(0, lambda: update_key_result(key_name))
            
            def update_key_result(key_name):
                captured_key[0] = key_name
                key_result.config(text=f"Captured: {key_name}")
                key_value.config(text=key_name, foreground="black")
                key_dialog.after(1000, key_dialog.destroy)
            
            # Start capture in a separate thread
            import threading
            capture_thread = threading.Thread(target=capture_thread)
            capture_thread.daemon = True
            capture_thread.start()
            
            # Also keep the original event binding as a fallback
            def on_key_press(event):
                key_name = event.keysym
                captured_key[0] = key_name
                key_result.config(text=f"Captured: {key_name}")
                key_value.config(text=key_name, foreground="black")
                key_dialog.after(1000, key_dialog.destroy)
            
            key_dialog.bind("<Key>", on_key_press)
            key_dialog.focus_set()
        
        key_button.config(command=capture_key)
        
        # Function to update UI based on selection
        def update_ui():
            action_choice = action_var.get()
            
            # Hide all custom frames
            text_frame.pack_forget()
            key_frame.pack_forget()
            
            # Show appropriate frame based on selection
            if action_choice == "text":
                text_frame.pack(fill=tk.X, padx=10, pady=10)
                text_label.pack(side=tk.LEFT, padx=5)
                text_entry.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
            elif action_choice == "custom":
                key_frame.pack(fill=tk.X, padx=10, pady=10)
                key_label.pack(side=tk.LEFT, padx=5)
                key_value.pack(side=tk.LEFT, padx=5)
                key_button.pack(side=tk.RIGHT, padx=5)
        
        # Trace the variable to update UI
        action_var.trace_add("write", lambda *args: update_ui())
        
        # Button to save action
        def save_action():
            action_choice = action_var.get()
            
            if action_choice.startswith("predefined:"):
                # Predefined action
                key = action_choice.split(":", 1)[1]
                parameters = {"key": key}
                if self.detector.associate_action(gesture_name, "keyboard", parameters):
                    messagebox.showinfo("Success", f"Action associated with gesture '{gesture_name}'")
                    keyboard_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to associate action")
            
            elif action_choice == "text":
                # Type text
                text = text_entry.get().strip()
                if not text:
                    messagebox.showerror("Input Error", "Text cannot be empty")
                    return
                
                parameters = {"text": text}
                if self.detector.associate_action(gesture_name, "keyboard", parameters):
                    messagebox.showinfo("Success", f"Action associated with gesture '{gesture_name}'")
                    keyboard_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to associate action")
            
            elif action_choice == "custom":
                # Custom key
                if not captured_key[0]:
                    messagebox.showerror("Input Error", "No key captured")
                    return
                
                parameters = {"key": captured_key[0]}
                if self.detector.associate_action(gesture_name, "keyboard", parameters):
                    messagebox.showinfo("Success", f"Action associated with gesture '{gesture_name}'")
                    keyboard_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to associate action")
        
        button_frame = ttk.Frame(keyboard_dialog)
        button_frame.pack(fill=tk.X, pady=10, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="Save", command=save_action).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=keyboard_dialog.destroy).pack(side=tk.RIGHT, padx=10)
        
        # Initial UI update
        update_ui()
    
    def _define_mouse_action(self, gesture_name):
        """
        Define a mouse action for a gesture.
        
        Parameters:
        - gesture_name: name of the gesture to associate the action with
        """
        # Get available mouse actions
        mouse_actions = self.detector.list_available_actions()["mouse"]
        
        # Create mouse action dialog
        mouse_dialog = tk.Toplevel(self.root)
        mouse_dialog.title("Define Mouse Action")
        mouse_dialog.geometry("400x400")
        mouse_dialog.transient(self.root)
        mouse_dialog.grab_set()
        
        ttk.Label(mouse_dialog, text="Select Mouse Action", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create scrollable frame
        container = ttk.Frame(mouse_dialog)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        container.pack(fill="both", expand=True, padx=10, pady=10)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action selection variable
        action_var = tk.StringVar()
        
        # Add predefined actions
        for i, action in enumerate(mouse_actions):
            ttk.Radiobutton(scrollable_frame, text=action['name'], 
                           variable=action_var, value=f"predefined:{action['id']}").pack(anchor=tk.W, padx=5, pady=2)
        
        # Add custom options
        ttk.Separator(scrollable_frame).pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(scrollable_frame, text="Move mouse to position", 
                       variable=action_var, value="move").pack(anchor=tk.W, padx=5, pady=2)
        
        # Set default
        action_var.set("predefined:left_click")
        
        # Move mouse frame (initially hidden)
        move_frame = ttk.Frame(mouse_dialog)
        
        x_frame = ttk.Frame(move_frame)
        x_frame.pack(fill=tk.X, pady=2)
        ttk.Label(x_frame, text="X coordinate:").pack(side=tk.LEFT, padx=5)
        x_entry = ttk.Entry(x_frame, width=10)
        x_entry.pack(side=tk.RIGHT, padx=5)
        
        y_frame = ttk.Frame(move_frame)
        y_frame.pack(fill=tk.X, pady=2)
        ttk.Label(y_frame, text="Y coordinate:").pack(side=tk.LEFT, padx=5)
        y_entry = ttk.Entry(y_frame, width=10)
        y_entry.pack(side=tk.RIGHT, padx=5)
        
        move_type_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(move_frame, text="Absolute position (unchecked = relative)", 
                       variable=move_type_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Function to update UI based on selection
        def update_ui():
            action_choice = action_var.get()
            
            # Hide all custom frames
            move_frame.pack_forget()
            
            # Show appropriate frame based on selection
            if action_choice == "move":
                move_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Trace the variable to update UI
        action_var.trace_add("write", lambda *args: update_ui())
        
        # Button to save action
        def save_action():
            action_choice = action_var.get()
            
            if action_choice.startswith("predefined:"):
                # Predefined action
                mouse_action = action_choice.split(":", 1)[1]
                parameters = {"action": mouse_action}
                if self.detector.associate_action(gesture_name, "mouse", parameters):
                    messagebox.showinfo("Success", f"Action associated with gesture '{gesture_name}'")
                    mouse_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to associate action")
            
            elif action_choice == "move":
                # Move mouse
                try:
                    x = int(x_entry.get())
                    y = int(y_entry.get())
                    absolute = move_type_var.get()
                    
                    parameters = {"x": x, "y": y, "absolute": absolute}
                    if self.detector.associate_action(gesture_name, "mouse", parameters):
                        messagebox.showinfo("Success", f"Action associated with gesture '{gesture_name}'")
                        mouse_dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to associate action")
                except ValueError:
                    messagebox.showerror("Input Error", "Coordinates must be integers")
        
        button_frame = ttk.Frame(mouse_dialog)
        button_frame.pack(fill=tk.X, pady=10, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="Save", command=save_action).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=mouse_dialog.destroy).pack(side=tk.RIGHT, padx=10)
        
        # Initial UI update
        update_ui()
    
    def show_remove_dialog(self):
        """Show dialog to remove a gesture."""
        gestures = self.detector.list_gestures()
        
        if not gestures:
            messagebox.showinfo("Remove Gesture", "No gestures registered.")
            return
        
        # Create gesture selection dialog
        remove_dialog = tk.Toplevel(self.root)
        remove_dialog.title("Remove Gesture")
        remove_dialog.geometry("400x300")
        remove_dialog.transient(self.root)
        remove_dialog.grab_set()
        
        ttk.Label(remove_dialog, text="Select a Gesture to Remove", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create scrollable frame
        container = ttk.Frame(remove_dialog)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        container.pack(fill="both", expand=True, padx=10, pady=10)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add gesture options
        for i, (name, description) in enumerate(gestures):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=f"{name}: {description}").pack(side=tk.LEFT, padx=5)
            
            def remove_gesture_func(gesture_name=name):
                if messagebox.askyesno("Confirm Removal", 
                                      f"Are you sure you want to remove gesture '{gesture_name}'?"):
                    if self.detector.remove_gesture(gesture_name):
                        messagebox.showinfo("Success", f"Gesture '{gesture_name}' removed successfully!")
                        remove_dialog.destroy()
                    else:
                        messagebox.showerror("Error", f"Failed to remove gesture '{gesture_name}'")
            
            ttk.Button(frame, text="Remove", 
                      command=lambda n=name: remove_gesture_func(n)).pack(side=tk.RIGHT, padx=5)
        
        # Add cancel button
        button_frame = ttk.Frame(remove_dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=remove_dialog.destroy).pack(side=tk.RIGHT, padx=10)
    
    def show_threshold_dialog(self):
        """Show dialog to adjust confidence threshold."""
        threshold_dialog = tk.Toplevel(self.root)
        threshold_dialog.title("Adjust Confidence Threshold")
        threshold_dialog.geometry("400x200")
        threshold_dialog.transient(self.root)
        threshold_dialog.grab_set()
        
        ttk.Label(threshold_dialog, text="Adjust Confidence Threshold", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(threshold_dialog, 
                 text="Higher values reduce false positives but may miss some gestures.").pack(pady=5)
        
        threshold_var = tk.DoubleVar(value=config.confidence_threshold)
        
        scale_frame = ttk.Frame(threshold_dialog)
        scale_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(scale_frame, text="0.5").pack(side=tk.LEFT)
        ttk.Scale(scale_frame, from_=0.5, to=1.0, 
                 variable=threshold_var, 
                 length=300).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Label(scale_frame, text="1.0").pack(side=tk.LEFT)
        
        value_label = ttk.Label(threshold_dialog, 
                               text=f"Current value: {config.confidence_threshold:.2f}")
        value_label.pack(pady=5)
        
        # Update label when slider moves
        threshold_var.trace_add("write", 
                               lambda *args: value_label.config(
                                   text=f"Current value: {threshold_var.get():.2f}"))
        
        button_frame = ttk.Frame(threshold_dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_threshold():
            config.set_confidence_threshold(threshold_var.get())
            threshold_dialog.destroy()
        
        ttk.Button(button_frame, text="Save", 
                  command=save_threshold).pack(side=tk.LEFT, padx=20)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=threshold_dialog.destroy).pack(side=tk.RIGHT, padx=20)
    
    def show_about_dialog(self):
        """Show about dialog."""
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About ActionMotion")
        about_dialog.geometry("400x300")
        about_dialog.transient(self.root)
        
        ttk.Label(about_dialog, text="ActionMotion", 
                 font=("Arial", 18, "bold")).pack(pady=10)
        
        ttk.Label(about_dialog, 
                 text="A gesture recognition system for controlling your computer").pack()
        
        ttk.Label(about_dialog, 
                 text="Version 1.0").pack(pady=5)
        
        ttk.Label(about_dialog, 
                 text="© 2025 ActionMotion Team").pack(pady=20)
        
        ttk.Button(about_dialog, text="Close", 
                  command=about_dialog.destroy).pack(pady=10)
    
    def show_shortcuts_dialog(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_dialog = tk.Toplevel(self.root)
        shortcuts_dialog.title("Keyboard Shortcuts")
        shortcuts_dialog.geometry("400x300")
        shortcuts_dialog.transient(self.root)
        
        ttk.Label(shortcuts_dialog, text="Keyboard Shortcuts", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create scrollable frame
        container = ttk.Frame(shortcuts_dialog)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        container.pack(fill="both", expand=True, padx=10, pady=10)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add shortcuts
        shortcuts = [
            ("r", "Capture a new gesture"),
            ("a", "Manage gesture actions"),
            ("l", "List registered gestures"),
            ("d", "Remove a gesture"),
            ("c", "Change camera"),
            ("h", "Toggle hand detection on/off"),
            ("p", "Toggle pose detection on/off"),
            ("s", "Show/hide action information"),
            ("f", "Show/hide FPS display"),
            ("m", "Show/hide landmarks"),
            ("+", "Increase confidence threshold"),
            ("-", "Decrease confidence threshold"),
            ("q", "Quit")
        ]
        
        for key, description in shortcuts:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=key, width=5, 
                     font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
            ttk.Label(frame, text=description).pack(side=tk.LEFT, padx=5)
        
        # Add close button
        button_frame = ttk.Frame(shortcuts_dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Close", 
                  command=shortcuts_dialog.destroy).pack(side=tk.RIGHT, padx=10)
