# ActionMotion

ActionMotion is a gesture recognition application that allows you to control your computer using hand gestures and body poses. It uses computer vision to detect and recognize gestures, and then executes associated actions like keyboard shortcuts, mouse movements, or custom commands.

## Features

- Hand gesture recognition
- Pose detection
- Direction-aware gestures (up, down, left, right, forward)
- Gesture hold time security (prevents accidental actions)
- Customizable actions for each gesture
- Real-time feedback with visual progress indicators
- Scrollable sidebar with configuration options
- Ability to capture and save custom gestures

## Requirements

- Python 3.7 or higher
- Webcam or camera device
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ActionMotion.git
   cd ActionMotion
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

### Capturing Gestures

1. Click on "Capture Gesture" in the sidebar or select "Gestures > Capture Gesture" from the menu
2. Position your hand(s) or body in the desired pose
3. Click "Capture" button
4. Enter a name and description for the gesture
5. Click "Save"

### Associating Actions

1. Select "Gestures > Edit Actions" from the menu
2. Select a gesture from the list
3. Choose an action type (keyboard, mouse, or custom)
4. Configure the action parameters
5. Click "Save"

### Security Features

- Gesture Hold Time: Gestures must be held for a configurable amount of time before actions are executed
- Confidence Threshold: Adjust the similarity threshold to reduce false positives

## Building an Executable

To build a standalone executable:

### Windows
Double-click on `build.bat` or run:
```
python build.py
```

### Linux/Mac
Run:
```
chmod +x build.sh
./build.sh
```
or
```
python3 build.py
```

The executable will be created in the `dist/ActionMotion` directory.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
