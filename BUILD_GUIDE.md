# Pro Pilot - Build Instructions

## Quick Start

```bash
# 1. Install dependencies
pip install customtkinter Pillow

# 2. Run the application
python main.py
```

## Building the Executable

### Option 1: Use the build script
```bash
python build.py
```

### Option 2: Use PyInstaller directly
```bash
pyinstaller --onefile --windowed --name=ProPilot main.py
```

### Option 3: Detailed build command
```bash
pyinstaller ^
    --noconfirm ^
    --windowed ^
    --onefile ^
    --name=ProPilot ^
    --add-data="data/missions.json;data" ^
    main.py
```

The executable will be created in the `dist/` folder.

## Project Structure

```
ProPilot/
├── main.py              # Entry point
├── database.py          # Data persistence
├── build.py             # Build script
├── requirements.txt     # Dependencies
├── README.md            # Documentation
├── data/
│   └── missions.json        # Training data
├── views/
│   ├── __init__.py
│   ├── missions_view.py
│   ├── study_center_view.py
│   ├── settings_view.py
│   └── CTkEditableLabel.py
└── assets/
```

## Features

- **Mission Tracking**: Checklist for all PPA training missions
- **Study Center**: Detailed maneuver instructions and study materials
- **Theme Toggle**: Dark/Light mode
- **Progress Tracking**: Visual indicators by phase
- **Data Persistence**: Saves progress to user_progress.json