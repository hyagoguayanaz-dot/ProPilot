"""
Database manager for Pro Pilot application.
Handles persistence of user progress, mission completion, notes, and settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DatabaseManager:
    """Manages user data persistence for the Pro Pilot application."""
    
    def __init__(self, data_dir: str = None):
        """Initialize database manager with path to data directory."""
        if data_dir is None:
            # Use same directory as this script
            data_dir = Path(__file__).parent / "data"
        
        self.data_dir = Path(data_dir)
        self.progress_file = self.data_dir / "user_progress.json"
        self.settings_file = self.data_dir / "user_settings.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data structures
        self._init_default_progress()
        self._init_default_settings()
    
    def _init_default_progress(self):
        """Initialize default user progress data."""
        default_progress = {
            "completed_missions": [],
            "mission_notes": {},
            "study_progress": {
                "PS": {"completed": 0, "total": 3, "exercises_mastered": []},
                "AP": {"completed": 0, "total": 1, "exercises_mastered": []},
                "NV": {"completed": 0, "total": 1, "exercises_mastered": []},
                "NOT": {"completed": 0, "total": 1, "exercises_mastered": []}
            },
            "last_updated": datetime.now().isoformat(),
            "profile": {
                "total_flight_hours": 0,
                "solo_hours": 0,
                "current_phase": "PS",
                "pilot_license_status": "student"
            }
        }
        
        if not self.progress_file.exists():
            self._save_progress(default_progress)
    
    def _init_default_settings(self):
        """Initialize default user settings."""
        default_settings = {
            "theme": "dark",
            "language": "pt-BR",
            "notifications": True,
            "study_reminders": True,
            "display_name": "Piloto-Aluno",
            "school": "Aeroclube de Pirassununga"
        }
        
        if not self.settings_file.exists():
            self._save_settings(default_settings)
    
    def _save_progress(self, data: Dict) -> None:
        """Save progress data to file."""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_settings(self, settings: Dict) -> None:
        """Save settings to file."""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    
    def load_progress(self) -> Dict:
        """Load user progress from file."""
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_default_progress()
            return self.load_progress()
    
    def load_settings(self) -> Dict:
        """Load user settings from file."""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_default_settings()
            return self.load_settings()
    
    def save_settings(self, settings: Dict) -> None:
        """Save settings to file."""
        self._save_settings(settings)
    
    def toggle_mission_completion(self, mission_id: str, completed: bool = None) -> bool:
        """
        Toggle or set completion status of a mission.
        
        Args:
            mission_id: The mission identifier (e.g., "PS-1", "NV-3")
            completed: True to mark complete, False to mark incomplete.
                      If None, toggles the current status.
        
        Returns:
            True if operation successful
        """
        progress = self.load_progress()
        
        # Toggle if not specified
        if completed is None:
            completed = mission_id not in progress["completed_missions"]
        
        if completed and mission_id not in progress["completed_missions"]:
            progress["completed_missions"].append(mission_id)
        elif not completed and mission_id in progress["completed_missions"]:
            progress["completed_missions"].remove(mission_id)
        
        self._save_progress(progress)
        return True
    
    def is_mission_completed(self, mission_id: str) -> bool:
        """Check if a mission is completed."""
        progress = self.load_progress()
        return mission_id in progress["completed_missions"]
    
    def add_mission_note(self, mission_id: str, note: str) -> None:
        """Add a note for a specific mission."""
        progress = self.load_progress()
        
        if mission_id not in progress["mission_notes"]:
            progress["mission_notes"][mission_id] = []
        
        progress["mission_notes"][mission_id].append({
            "timestamp": datetime.now().isoformat(),
            "note": note
        })
        
        self._save_progress(progress)
    
    def get_mission_notes(self, mission_id: str) -> List[Dict]:
        """Get all notes for a mission."""
        progress = self.load_progress()
        return progress["mission_notes"].get(mission_id, [])
    
    def update_study_progress(self, phase: str) -> None:
        """
        Update study progress for a phase when missions are completed.
        
        Args:
            phase: The phase identifier (PS, AP, NV, NOT)
        """
        progress = self.load_progress()
        
        # Count completed missions for this phase
        phase_missions = [m for m in progress["completed_missions"] if m.startswith(phase)]
        count = len(phase_missions)
        
        # Map phase to expected totals
        totals = {
            "PS": 20,  # 20+ hours worth of basic missions
            "AP": 10,
            "NV": 10,
            "NOT": 3
        }
        
        total_expected = totals.get(phase, 0)
        progress["study_progress"][phase] = {
            "completed": count,
            "total": total_expected,
            "exercises_mastered": phase_missions
        }
        
        # Update current phase if this is the highest completed
        phase_order = ["PS", "AP", "NV", "NOT"]
        current_idx = 0
        for i, p in enumerate(phase_order):
            if p in progress["study_progress"] and progress["study_progress"][p]["completed"] > 0:
                current_idx = i
        
        if phase in phase_order and current_idx > 0:
            completed_phases = [p for p in phase_order[:current_idx+1] 
                              if progress["study_progress"].get(p, {}).get("completed", 0) > 0]
            if completed_phases:
                progress["profile"]["current_phase"] = completed_phases[-1]
        
        self._save_progress(progress)
    
    def get_progress_summary(self) -> Dict:
        """Get overall progress summary."""
        progress = self.load_progress()
        
        total_missions = 0
        completed_missions = len(progress["completed_missions"])
        
        for phase, data in progress["study_progress"].items():
            total_missions += data["total"]
        
        progress_pct = (completed_missions / max(total_missions, 1)) * 100
        
        return {
            "completed_missions": completed_missions,
            "total_missions_estimated": total_missions,
            "progress_percentage": round(progress_pct, 1),
            "completed_phases": len([p for p, d in progress["study_progress"].items() 
                                    if d["completed"] > 0]),
            "total_phases": 4,
            "current_phase": progress["profile"]["current_phase"]
        }
    
    def get_phase_progress(self, phase: str) -> Dict:
        """Get progress for a specific phase."""
        progress = self.load_progress()
        return progress["study_progress"].get(phase, {
            "completed": 0, 
            "total": 0, 
            "exercises_mastered": []
        })
    
    def clear_completed_missions(self) -> None:
        """Clear all completed mission markers (reset progress)."""
        progress = self.load_progress()
        progress["completed_missions"] = []
        progress["study_progress"] = {
            "PS": {"completed": 0, "total": 20, "exercises_mastered": []},
            "AP": {"completed": 0, "total": 10, "exercises_mastered": []},
            "NV": {"completed": 0, "total": 10, "exercises_mastered": []},
            "NOT": {"completed": 0, "total": 3, "exercises_mastered": []}
        }
        self._save_progress(progress)


# Singleton instance
_db_instance = None

def get_database() -> DatabaseManager:
    """Get the singleton database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance