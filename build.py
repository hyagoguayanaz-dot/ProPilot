#!/usr/bin/env python3
"""
Build script for Pro Pilot application.
Compiles the application into a standalone Windows executable using PyInstaller.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def build_exe():
    """Build the Pro Pilot executable using PyInstaller."""
    app_dir = Path(__file__).parent
    
    # Ensure we're in the right directory
    os.chdir(str(app_dir))
    
    # Create build command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--onefile",
        "--name=ProPilot",
        "--add-data=data/missions.json;data",
        "main.py"
    ]
    
    print("Building Pro Pilot executable...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {app_dir}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print(result.stdout)
    print("\nBuild completed successfully!")
    
    # Check for executable
    dist_path = app_dir / "dist"
    exe_path = dist_path / "ProPilot.exe"
    
    if exe_path.exists():
        print(f"Executable created at: {exe_path}")
        return True
    else:
        print("Executable not found in dist folder")
        return False


def clean_build():
    """Clean build artifacts."""
    app_dir = Path(__file__).parent
    
    dirs_to_remove = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_remove:
        dir_path = app_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(str(dir_path))
            print(f"Removed: {dir_path}")
    
    # Remove spec file
    spec_file = app_dir / "ProPilot.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"Removed: {spec_file}")
    
    print("Clean completed!")


def main():
    """Main entry point for build script."""
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_build()
    else:
        success = build_exe()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()