#!/usr/bin/env python3
"""
Pro Pilot - Aviation Training Application
A desktop application for Private Pilot License (PPL) training tracking and study.

Author: Pro Pilot Team
Version: 1.0.0
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
import sys
import os
import json

# Set app version
__version__ = "1.0.0"

# Import views
try:
    from views.missions_view import MissionsView
    from views.study_center_view import StudyCenterView
    from views.settings_view import SettingsView
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from views.missions_view import MissionsView
    from views.study_center_view import StudyCenterView
    from views.settings_view import SettingsView

# Import database
try:
    from database import get_database
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from database import get_database


class ThemeManager:
    """Manages application theme (dark/light mode)."""
    
    THEMES = {
        "dark": {
            "mode": "Dark",
            "colors": {
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "card": "#2d2d2d",
                "border": "#3d3d3d",
                "accent": "#3498db"
            }
        },
        "light": {
            "mode": "Light",
            "colors": {
                "primary": "#2c3e50",
                "secondary": "#27ae60",
                "background": "#ffffff",
                "foreground": "#1a1a1a",
                "card": "#f8f8f8",
                "border": "#e0e0e0",
                "accent": "#3498db"
            }
        }
    }
    
    def __init__(self):
        self.current_theme = "dark"
        self._load_saved_theme()
    
    def _load_saved_theme(self):
        """Load saved theme from settings."""
        try:
            db = get_database()
            settings = db.load_settings()
            saved_theme = settings.get("theme", "dark")
            if saved_theme in self.THEMES:
                self.current_theme = saved_theme
        except Exception:
            pass
    
    def apply_theme(self, app: ctk.CTk):
        """Apply theme to the application."""
        ctk.set_appearance_mode(self.current_theme)
    
    def set_theme(self, theme: str):
        """Change the application theme."""
        if theme in self.THEMES:
            self.current_theme = theme
            ctk.set_appearance_mode(theme)
            
            # Save preference
            try:
                db = get_database()
                settings = db.load_settings()
                settings["theme"] = theme
                db.save_settings(settings)
            except Exception:
                pass


class ProPilotApp(ctk.CTk):
    """Main application class for Pro Pilot."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.theme_manager = ThemeManager()
        self.db = get_database()
        
        # Configure window
        self._configure_window()
        
        # Setup theme
        self.theme_manager.apply_theme(self)
        
        # Setup UI
        self._setup_ui()
        
        # Load initial view
        self.show_dashboard()
    
    def _configure_window(self):
        """Configure main window properties."""
        self.title("✈️ Pro Pilot - Piloto Privado de Avião")
        self.geometry("1000x700")
        self.minsize(900, 600)
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def _setup_ui(self):
        """Set up the main user interface."""
        # Main container
        main_container = ctk.CTkFrame(self, corner_radius=0)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # Header with theme toggle
        header_frame = ctk.CTkFrame(main_container, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # App title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="✈️ Pro Pilot",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Current phase indicator
        self.phase_indicator = ctk.CTkLabel(
            header_frame,
            text="Fase: Pré-Solo",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray50")
        )
        self.phase_indicator.grid(row=0, column=1, padx=10, sticky="e")
        
        # Theme toggle button
        self.theme_button = ctk.CTkButton(
            header_frame,
            text="🌙",
            width=50,
            command=self._toggle_theme
        )
        self.theme_button.grid(row=0, column=2, padx=10, sticky="e")
        
        # Navigation sidebar
        nav_frame = ctk.CTkFrame(main_container, width=200, corner_radius=0)
        nav_frame.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=(0, 15))
        nav_frame.grid_rowconfigure(6, weight=1)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", "dashboard"),
            ("📋 Missões & Progresso", "missions"),
            ("📚 Central de Estudos", "study"),
            ("⚙️ Configurações", "settings")
        ]
        
        for i, (text, key) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=lambda k=key: self._navigate_to(k),
                anchor="w",
                height=40
            )
            btn.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
        
        # Content area - will be replaced
        self.content_frame = ctk.CTkFrame(main_container)
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 15), pady=(0, 15))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
    
    def _toggle_theme(self):
        """Toggle between dark and light themes."""
        current = self.theme_manager.current_theme
        new_theme = "light" if current == "dark" else "dark"
        self.theme_manager.set_theme(new_theme)
        
        # Update button icon
        self.theme_button.configure(text="☀️" if new_theme == "light" else "🌙")
    
    def _navigate_to(self, section: str):
        """Navigate to a specific section."""
        sections = {
            "dashboard": self.show_dashboard,
            "missions": self.show_missions,
            "study": self.show_study_center,
            "settings": self.show_settings
        }
        
        if section in sections:
            sections[section]()
    
    def show_dashboard(self):
        """Show the dashboard view."""
        self._clear_content()
        self._render_dashboard()
    
    def show_missions(self):
        """Show the missions view."""
        self._clear_content()
        
        self.missions_view = MissionsView(
            self.content_frame,
            on_back=self.show_dashboard,
            theme_manager=self.theme_manager
        )
        self.missions_view.grid(row=0, column=0, sticky="nsew")
        
        self._update_phase_indicator()
    
    def show_study_center(self):
        """Show the study center view."""
        self._clear_content()
        
        self.study_view = StudyCenterView(
            self.content_frame,
            on_maneuver_select=self._show_maneuver_details,
            on_back=self.show_dashboard,
            theme_manager=self.theme_manager
        )
        self.study_view.grid(row=0, column=0, sticky="nsew")
    
    def show_settings(self):
        """Show the settings view."""
        self._clear_content()
        
        self.settings_view = SettingsView(
            self.content_frame,
            on_back=self.show_dashboard,
            theme_manager=self.theme_manager
        )
        self.settings_view.grid(row=0, column=0, sticky="nsew")
    
    def _clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _render_dashboard(self):
        """Render the dashboard content."""
        dashboard_frame = ctk.CTkFrame(self.content_frame, corner_radius=12)
        dashboard_frame.pack(fill="both", expand=True, padx=20, pady=20)
        dashboard_frame.grid_columnconfigure(0, weight=1)
        dashboard_frame.grid_rowconfigure(3, weight=1)
        
        # Welcome header
        welcome_label = ctk.CTkLabel(
            dashboard_frame,
            text="Bem-vindo ao Pro Pilot",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        welcome_label.pack(pady=(20, 5))
        
        welcome_sub = ctk.CTkLabel(
            dashboard_frame,
            text="Sua jornada rumo ao voo solo começa aqui",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray50")
        )
        welcome_sub.pack(pady=(0, 20))
        
        # Stats cards
        stats_frame = ctk.CTkFrame(dashboard_frame)
        stats_frame.pack(fill="x", padx=30, pady=10)
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        
        # Get progress data
        summary = self.db.get_progress_summary()
        study_progress = self.db.load_progress().get("study_progress", {})
        
        # Progress card
        progress_card = ctk.CTkFrame(stats_frame, corner_radius=8)
        progress_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(progress_card, text="Progresso", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15, pady=(15, 5))
        
        progress_value = ctk.CTkLabel(progress_card, text=f"{summary['progress_percentage']}%", 
                                      font=ctk.CTkFont(size=28, weight="bold"))
        progress_value.pack(pady=10)
        
        ctk.CTkLabel(progress_card, text=f"{summary['completed_missions']} missões concluídas", 
                     font=ctk.CTkFont(size=12), text_color=("gray60", "gray50")).pack(pady=(0, 15))
        
        # Current phase card
        phase_card = ctk.CTkFrame(stats_frame, corner_radius=8)
        phase_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(phase_card, text="Fase Atual", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15, pady=(15, 5))
        
        phase_name = self._get_phase_name(summary.get("current_phase", "PS"))
        phase_value = ctk.CTkLabel(phase_card, text=phase_name, 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        phase_value.pack(pady=10)
        
        hours_to_next = "20+ horas" if summary["current_phase"] == "PS" else "Próxima fase"
        ctk.CTkLabel(phase_card, text=hours_to_next, 
                     font=ctk.CTkFont(size=12), text_color=("gray60", "gray50")).pack(pady=(0, 15))
        
        # Quick actions
        actions_frame = ctk.CTkFrame(dashboard_frame)
        actions_frame.pack(fill="x", padx=30, pady=20)
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        missions_btn = ctk.CTkButton(
            actions_frame,
            text="📋 Ver Missões",
            command=self.show_missions,
            height=50
        )
        missions_btn.grid(row=0, column=0, padx=10, pady=10)
        
        study_btn = ctk.CTkButton(
            actions_frame,
            text="📚 Estudar Manobras",
            command=self.show_study_center,
            height=50
        )
        study_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Phase progress bars
        progress_title = ctk.CTkLabel(dashboard_frame, text="Progresso por Fase", 
                                      font=ctk.CTkFont(size=16, weight="bold"))
        progress_title.pack(anchor="w", padx=30, pady=(20, 10))
        
        phase_bars_frame = ctk.CTkFrame(dashboard_frame)
        phase_bars_frame.pack(fill="x", padx=30, pady=10)
        
        phases = [("PS", "Pré-Solo"), ("AP", "Aperfeiçoamento"), ("NV", "Navegação"), ("NOT", "Noturno")]
        phase_colors = {"PS": "#3498db", "AP": "#2ecc71", "NV": "#9b59b6", "NOT": "#e74c3c"}
        
        for phase, name in phases:
            phase_info = study_progress.get(phase, {})
            total = phase_info.get("total", 1)
            completed = phase_info.get("completed", 0)
            pct = min(completed / max(total, 1), 1.0)
            
            bar_frame = ctk.CTkFrame(phase_bars_frame)
            bar_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(bar_frame, text=f"{name}", font=ctk.CTkFont(size=12), width=120).pack(side="left")
            
            progress_bar = ctk.CTkProgressBar(bar_frame, height=10)
            progress_bar.set(pct)
            progress_bar.pack(fill="x", expand=True, padx=10)
        
        # Recent missions section
        recent_frame = ctk.CTkFrame(dashboard_frame)
        recent_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        recent_title = ctk.CTkLabel(recent_frame, text="Missões Recentes", 
                                    font=ctk.CTkFont(size=16, weight="bold"))
        recent_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        recent_list = ctk.CTkScrollableFrame(recent_frame, height=200)
        recent_list.pack(fill="both", expand=True, padx=15, pady=10)
        
        completed = summary.get("completed_missions", [])
        if completed:
            for mission in completed[:5]:
                ctk.CTkLabel(
                    recent_list,
                    text=f"✓ {mission}",
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                ).pack(fill="x", pady=2)
        else:
            ctk.CTkLabel(
                recent_list,
                text="Nenhuma missão concluída ainda",
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray50")
            ).pack(pady=20)
    
    def _update_phase_indicator(self):
        """Update the phase indicator in the header."""
        progress = self.db.load_progress()
        current_phase = progress.get("profile", {}).get("current_phase", "PS")
        phase_name = self._get_phase_name(current_phase)
        self.phase_indicator.configure(text=f"Fase: {phase_name}")
    
    def _get_phase_name(self, phase_code: str) -> str:
        """Get the display name for a phase code."""
        phase_names = {
            "PS": "Pré-Solo",
            "AP": "Aperfeiçoamento",
            "NV": "Navegação",
            "NOT": "Noturno"
        }
        return phase_names.get(phase_code, "Pré-Solo")


def main():
    """Main entry point for the application."""
    # Initialize customtkinter
    ctk.set_default_color_theme("blue")
    
    # Create and run app
    app = ProPilotApp()
    app.mainloop()


if __name__ == "__main__":
    main()