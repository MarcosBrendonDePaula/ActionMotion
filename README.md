# ActionMotion

A gesture recognition system that allows users to capture and recognize hand and body gestures, and associate actions with them (keyboard, mouse, etc.).

## Features

- Detect and track hand and body movements using computer vision
- Capture custom gestures and associate actions with them
- Execute keyboard and mouse actions based on recognized gestures
- Hand-specific gesture detection (left hand vs. right hand)
- User-friendly interface for managing gestures and actions
- Configurable detection options (toggle hand/pose detection)

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- NumPy
- pynput

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/ActionMotion.git
cd ActionMotion
```

2. Install the required packages:
```
pip install -r requirements.txt
```

## Usage

Run the application:
```
python main.py
```

### Controls

- **r**: Capture a new gesture
- **a**: Manage gesture actions
- **l**: List registered gestures
- **d**: Remove a gesture
- **c**: Change camera
- **h**: Toggle hand detection on/off
- **p**: Toggle pose detection on/off
- **s**: Show/hide action information
- **f**: Show/hide FPS display
- **m**: Show/hide landmarks
- **+**: Increase confidence threshold
- **-**: Decrease confidence threshold
- **q**: Quit

### Capturing Gestures

1. Press 'r' to enter capture mode
2. Position your hands/body in the desired pose
3. Press 'r' again to capture the gesture
4. Enter a name and description for the gesture
5. Optionally associate an action with the gesture

### Managing Actions

Actions can be associated with gestures to perform various tasks:

- **Keyboard actions**: Press keys, type text, or use predefined key combinations
- **Mouse actions**: Click, move the cursor, scroll, etc.

## Project Structure

```
ActionMotion/
├── main.py                  # Main entry point
├── requirements.txt         # Project dependencies
├── gestos/                  # Gesture data storage
│   └── gestos.json          # Saved gestures
└── src/                     # Source code
    ├── main.py              # Main application logic
    ├── __init__.py          # Package initialization
    ├── actions/             # Action execution modules
    │   ├── __init__.py
    │   └── executor.py      # Action executor
    ├── core/                # Core functionality
    │   ├── __init__.py
    │   └── tracker.py       # Movement tracker
    ├── gestures/            # Gesture detection modules
    │   ├── __init__.py
    │   └── detector.py      # Gesture detector
    ├── ui/                  # User interface modules
    │   ├── __init__.py
    │   └── action_editor.py # Action editor interface
    └── utils/               # Utility functions
        ├── __init__.py
        └── helpers.py       # Helper functions
```

## Configuration Options

The application includes several configuration options that can be toggled during runtime:

### Confidence Threshold System
The application includes an adjustable confidence threshold to reduce false positives:
- Higher threshold (closer to 1.0): Only very confident matches will trigger actions (fewer false positives)
- Lower threshold (closer to 0.5): More lenient matching (may have more false positives)
- Adjustable in real-time using the '+' and '-' keys
- Visual indicator in the status panel shows the current threshold with color coding
- Gestures are detected at the similarity threshold but only trigger actions at the confidence threshold

### Hand-Specific Gesture Detection
The system now properly distinguishes between left and right hand gestures. This means:
- A gesture captured with the left hand will only be recognized when performed with the left hand
- A gesture captured with the right hand will only be recognized when performed with the right hand
- The UI displays which hand (left or right) is being used for each detected gesture

### Detection Options
- **Hand Detection**: Toggle hand tracking on/off (press 'h')
- **Pose Detection**: Toggle body pose tracking on/off (press 'p')

### Display Options
- **Landmarks Display**: Toggle visibility of hand and pose landmarks (press 'm')
- **FPS Display**: Toggle FPS counter on/off (press 'f')
- **Action Information**: Toggle display of action information (press 's')

### Window Options
- **Resizable Window**: The application window can be resized by dragging its borders

## Customization

### Adding Custom Keys

The system allows users to define custom keys during action association. When prompted, you can:

1. Select from predefined actions
2. Type custom text
3. Specify a custom key to be pressed

### Adding Custom Mouse Actions

For mouse actions, you can:

1. Select from predefined actions (click, right-click, etc.)
2. Define custom mouse movements with absolute or relative coordinates

## License

This project is licensed under the MIT License - see the LICENSE file for details.
