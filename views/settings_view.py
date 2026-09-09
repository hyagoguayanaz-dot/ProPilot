"""
Settings View - Displays application settings and theme configuration.
"""

import customtkinter as ctk
from typing import Callable, Dict
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SettingsView(ctk.CTkFrame):
    """View for application settings and theme configuration."""
    
    def __init__(self, parent, on_back: Callable = None, theme_manager=None):
        super().__init__(parent)
        self.on_back = on_back
        self.theme_manager = theme_manager
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface components."""
        self.grid_columnconfigure(0, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(self, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ Configurações",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Back button
        self.back_button = ctk.CTkButton(
            header_frame,
            text="← Voltar",
            width=100,
            command=self._go_back
        )
        self.back_button.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # Settings content
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Theme settings section
        theme_section = ctk.CTkFrame(content_frame, corner_radius=8)
        theme_section.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        theme_section.grid_columnconfigure(0, weight=1)
        
        theme_title = ctk.CTkLabel(
            theme_section,
            text="🎨 Tema de Exibição",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        theme_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        theme_desc = ctk.CTkLabel(
            theme_section,
            text="Escolha o modo de exibição da interface",
            font=ctk.CTkFont(size=13),
            text_color=("gray60", "gray50")
        )
        theme_desc.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Theme toggle
        self.theme_var = ctk.StringVar(value="dark")
        
        dark_radio = ctk.CTkRadioButton(
            theme_section,
            text="Escuro (Recomendado)",
            variable=self.theme_var,
            value="dark",
            command=self._toggle_theme
        )
        dark_radio.pack(anchor="w", padx=30, pady=5)
        
        light_radio = ctk.CTkRadioButton(
            theme_section,
            text="Claro",
            variable=self.theme_var,
            value="light",
            command=self._toggle_theme
        )
        light_radio.pack(anchor="w", padx=30, pady=(0, 15))
        
        # Profile settings section
        profile_section = ctk.CTkFrame(content_frame, corner_radius=8)
        profile_section.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        profile_section.grid_columnconfigure(0, weight=1)
        
        profile_title = ctk.CTkLabel(
            profile_section,
            text="👤 Perfil do Piloto",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        profile_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        profile_desc = ctk.CTkLabel(
            profile_section,
            text="Informações do seu progresso",
            font=ctk.CTkFont(size=13),
            text_color=("gray60", "gray50")
        )
        profile_desc.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Profile info display
        self.profile_frame = ctk.CTkFrame(profile_section, fg_color=("gray90", "gray20"))
        self.profile_frame.pack(fill="x", padx=30, pady=5)
        
        self.display_name_label = ctk.CTkLabel(self.profile_frame, text="Nome: Piloto-Aluno")
        self.display_name_label.pack(anchor="w", padx=15, pady=5)
        
        self.current_phase_label = ctk.CTkLabel(self.profile_frame, text="Fase Atual: Pré-Solo")
        self.current_phase_label.pack(anchor="w", padx=15, pady=5)
        
        self.total_hours_label = ctk.CTkLabel(self.profile_frame, text="Horas Registradas: 0h")
        self.total_hours_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Study goals section
        goals_section = ctk.CTkFrame(content_frame, corner_radius=8)
        goals_section.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        goals_section.grid_columnconfigure(0, weight=1)
        
        goals_title = ctk.CTkLabel(
            goals_section,
            text="🎯 Objetivos de Estudo",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        goals_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        goals_desc = ctk.CTkLabel(
            goals_section,
            text="Fases do curso de piloto privado",
            font=ctk.CTkFont(size=13),
            text_color=("gray60", "gray50")
        )
        goals_desc.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Phase progress bars
        phases = ["PS", "AP", "NV", "NOT"]
        phase_names = {
            "PS": "Pré-Solo (20h)",
            "AP": "Aperfeiçoamento (10h)",
            "NV": "Navegação (10h)",
            "NOT": "Noturno (3h)"
        }
        
        self.progress_bars = {}
        
        for phase in phases:
            bar_frame = ctk.CTkFrame(goals_section)
            bar_frame.pack(fill="x", padx=30, pady=5)
            
            phase_label = ctk.CTkLabel(bar_frame, text=phase_names[phase], font=ctk.CTkFont(size=12))
            phase_label.pack(anchor="w")
            
            progress = 0
            progress_bar = ctk.CTkProgressBar(bar_frame, height=8)
            progress_bar.set(progress)
            progress_bar.pack(fill="x", pady=5)
            
            self.progress_bars[phase] = progress_bar
        
        # About section
        about_section = ctk.CTkFrame(content_frame, corner_radius=8)
        about_section.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 20))
        about_section.grid_columnconfigure(0, weight=1)
        
        about_title = ctk.CTkLabel(
            about_section,
            text="ℹ️ Sobre o Aplicativo",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        about_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        about_text = """
**Pro Pilot v1.0**

Aplicativo de estudo e acompanhamento para o Curso de Piloto Privado de Avião (PPA).

Baseado no Programa de Instrução do Aeroclube de Pirassununga.

Desenvolvido para auxiliar no progresso dos estudos e missões práticas.
        """.strip()
        
        about_label = ctk.CTkLabel(
            about_section,
            text=about_text,
            font=ctk.CTkFont(size=13),
            justify="left",
            text_color=("gray60", "gray50")
        )
        about_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Version info
        version_label = ctk.CTkLabel(
            about_section,
            text="© 2026 - Pro Pilot - Desenvolvido por Engenheiros de Software",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=("gray60", "gray50")
        )
        version_label.pack(anchor="s", padx=15, pady=(0, 15))
        
        # Load settings
        self.load_settings()
    
    def _go_back(self):
        """Navigate back to previous view."""
        if self.on_back:
            self.on_back()
    
    def _toggle_theme(self):
        """Toggle between dark and light themes."""
        if self.theme_manager and hasattr(self.theme_manager, 'set_theme'):
            theme = self.theme_var.get()
            self.theme_manager.set_theme(theme)
    
    def load_settings(self):
        """Load current settings and update UI."""
        try:
            from database import get_database
            db = get_database()
            settings = db.load_settings()
            
            self.theme_var.set(settings.get("theme", "dark"))
            
            # Update profile info
            progress = db.load_progress()
            profile = progress.get("profile", {})
            
            self.display_name_label.configure(
                text=f"Nome: {profile.get('display_name', 'Piloto-Aluno')}"
            )
            self.current_phase_label.configure(
                text=f"Fase Atual: {self._get_phase_name(profile.get('current_phase', 'PS'))}"
            )
            self.total_hours_label.configure(
                text=f"Horas Registradas: {profile.get('total_flight_hours', 0)}h"
            )
            
            # Update progress bars
            for phase, bar in self.progress_bars.items():
                phase_progress = progress.get("study_progress", {}).get(phase, {})
                total = phase_progress.get("total", 1)
                completed = phase_progress.get("completed", 0)
                progress_pct = completed / max(total, 1)
                bar.set(min(progress_pct, 1.0))
                
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def _get_phase_name(self, phase_code: str) -> str:
        """Get the display name for a phase code."""
        phase_names = {
            "PS": "Pré-Solo",
            "AP": "Aperfeiçoamento",
            "NV": "Navegação",
            "NOT": "Noturno"
        }
        return phase_names.get(phase_code, "Pré-Solo")