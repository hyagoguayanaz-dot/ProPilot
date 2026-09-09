# Pro Pilot - Aviation Training Application

A desktop application for Private Pilot License (PPL) training tracking and study, based on the Brazilian Aeroclube de Pirassununga curriculum.

## Features

- **Quadro de Missões & Progresso**: Track all training missions with interactive checklist
- **Central de Estudos**: Study maneuvers and procedures with detailed instructions
- **Progress Tracking**: Visual indicators for completion percentage by phase
- **Theme Toggle**: Switch between dark and light modes
- **Data Persistence**: Saves user progress automatically

## Requirements

- Python 3.10 or higher
- customtkinter >= 5.2.0
- Pillow >= 10.0.0

## Installation

1. Open terminal/command prompt in the project directory

2. Create virtual environment (optional but recommended):
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Building the Executable

### Using the build script:
```bash
python build.py
```

### Using PyInstaller directly:
```bash
pyinstaller --onefile --windowed --name=ProPilot main.py
```

The executable will be created in the `dist/` folder.

## Project Structure

```
ProPilot/
├── main.py              # Application entry point
├── database.py          # Data persistence manager
├── build.py             # Build script for PyInstaller
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── data/
│   ├── missions.json        # Training missions data
│   ├── user_progress.json   # User progress (auto-created)
│   └── user_settings.json   # User settings (auto-created)
├── views/
│   ├── __init__.py
│   ├── missions_view.py     # Missions listing view
│   ├── study_center_view.py # Study materials view
│   ├── settings_view.py     # Settings view
│   └── CTkEditableLabel.py  # Editable label widget
└── assets/
    └── icon.ico      # Application icon
```

## Training Phases

Based on the PPA curriculum from Aeroclube de Pirassununga:

1. **Pré-Solo (PS)**: 20+ hours of basic flight training
2. **Aperfeiçoamento (AP)**: 10 hours of skill refinement
3. **Navegação (NV)**: 10 hours of navigation training
4. **Noturno (NOT)**: 3 hours of night flight operations

## License

This project is for educational purposes. Based on the official PPA curriculum from IS 141-OO7 (ANAC).

## Version History

- v1.0.0: Initial release with complete mission tracking, study center, and settings