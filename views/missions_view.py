"""
Missões View - Displays mission list and progress tracking.
"""

import customtkinter as ctk
from typing import Callable, Dict, List, Any
import sys
import os
import json


def resource_path(relative_path):
    """Get path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


class MissionsView(ctk.CTkFrame):
    """View for displaying and managing mission tracking."""
    
    def __init__(self, parent, on_back: Callable = None, theme_manager=None):
        super().__init__(parent)
        self.on_back = on_back
        self.theme_manager = theme_manager
        self.db = None
        from database import get_database
        self.db = get_database()
        self.current_mission = None
        
        self.missions_data = {}
        self.setup_ui()
        self.refresh_missions()
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header frame
        self.create_header()
        
        # Search frame
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar missão...",
            justify="left"
        )
        self.search_entry.pack(fill="x", padx=10, pady=8)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Main content - split view
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Mission list
        self.left_panel = ctk.CTkFrame(content_frame, width=300)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Right panel - Mission details
        self.right_panel = ctk.CTkFrame(content_frame)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Initialize panels
        self.init_left_panel()
        self.init_right_panel()
    
    def create_header(self):
        """Create header with title and back button."""
        header_frame = ctk.CTkFrame(self, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="📋 Quadro de Missões & Progresso",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Back button
        if self.on_back:
            self.back_button = ctk.CTkButton(
                header_frame,
                text="← Voltar",
                width=100,
                command=self.on_back
            )
            self.back_button.grid(row=0, column=1, padx=20, pady=15, sticky="e")
    
    def init_left_panel(self):
        """Initialize the left panel with mission list."""
        # Scrollable canvas
        canvas = ctk.CTkCanvas(self.left_panel, bg=self.left_panel.cget("fg_color"))
        canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ctk.CTkScrollbar(self.left_panel, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.mission_list_container = ctk.CTkFrame(canvas)
        self.mission_list_container.grid_columnconfigure(0, weight=1)
        
        self.canvas_window = canvas.create_window((0, 0), window=self.mission_list_container, anchor="nw")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.mission_list_container.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
    
    def init_right_panel(self):
        """Initialize the right panel with mission details."""
        # Title
        detail_title = ctk.CTkLabel(
            self.right_panel,
            text="Selecione uma missão",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        detail_title.pack(anchor="w", padx=15, pady=15)
        
        # Content area with scroll
        detail_canvas = ctk.CTkCanvas(self.right_panel, bg=self.right_panel.cget("fg_color"))
        detail_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        detail_scrollbar = ctk.CTkScrollbar(self.right_panel, command=detail_canvas.yview)
        detail_scrollbar.pack(side="right", fill="y")
        
        detail_canvas.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_container = ctk.CTkFrame(detail_canvas)
        self.detail_container.grid_columnconfigure(0, weight=1)
        
        self.detail_window = detail_canvas.create_window((0, 0), window=self.detail_container, anchor="nw")
        
        def on_detail_frame_configure(event):
            detail_canvas.configure(scrollregion=detail_canvas.bbox("all"))
        
        def on_detail_canvas_configure(event):
            detail_canvas.itemconfig(self.detail_window, width=event.width)
        
        self.detail_container.bind("<Configure>", on_detail_frame_configure)
        detail_canvas.bind("<Configure>", on_detail_canvas_configure)
        
        self.detail_title_label = ctk.CTkLabel(self.detail_container, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.detail_title_label.pack(anchor="w", padx=15, pady=10)
    
    def on_search(self, event=None):
        """Filter missions based on search text."""
        search_term = self.search_entry.get().lower()
        self.refresh_missions(search_term)
    
    def refresh_missions(self, search_filter: str = ""):
        """Refresh and display missions."""
        # Load data using resource_path for PyInstaller compatibility
        if not self.missions_data:
            try:
                data_path = resource_path(os.path.join("data", "missions.json"))
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.missions_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Could not load missions data: {e}")
                return
        
        # Clear existing content
        for widget in self.mission_list_container.winfo_children():
            widget.destroy()
        for widget in self.detail_container.winfo_children():
            if widget != self.detail_title_label:
                widget.destroy()
        
        # Get progress
        progress = self.db.load_progress()
        
        # Display missions by phase
        phases = ["PS", "AP", "NV", "NOT"]
        phase_names = {
            "PS": "Pré-Solo",
            "AP": "Aperfeiçoamento",
            "NV": "Navegação",
            "NOT": "Noturno"
        }
        
        for phase in phases:
            if phase in self.missions_data.get("missions", {}):
                phase_data = self.missions_data["missions"][phase]
                
                # Phase header
                phase_label = ctk.CTkLabel(
                    self.mission_list_container,
                    text=f"{phase_data['name']}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.get_phase_color(phase)
                )
                phase_label.pack(anchor="w", padx=10, pady=(15, 5))
                
                # Display missions for this phase
                if "missions" in phase_data:
                    for mission in phase_data["missions"]:
                        self.create_mission_item(mission, phase, phase_data, progress, search_filter)
    
    def get_phase_color(self, phase: str) -> str:
        """Get color for phase."""
        colors = {
            "PS": "#3498db",
            "AP": "#2ecc71",
            "NV": "#9b59b6",
            "NOT": "#e74c3c"
        }
        return colors.get(phase, "#95a5a6")
    
    def create_mission_item(self, mission: Dict, phase: str, phase_data: Dict, progress: Dict, search_filter: str):
        """Create a mission item in the list."""
        # Filter by search
        if search_filter:
            if search_filter.lower() not in mission["name"].lower():
                if search_filter.lower() not in mission.get("description", "").lower():
                    return
        
        is_completed = mission["id"] in progress.get("completed_missions", [])
        
        # Mission card
        card = ctk.CTkFrame(
            self.mission_list_container,
            corner_radius=8,
            border_width=1,
            border_color="#3498db"
        )
        card.grid_columnconfigure(0, weight=1)
        
        # Header with name and checkbox
        header = ctk.CTkFrame(card)
        header.pack(fill="x", padx=10, pady=5)
        header.grid_columnconfigure(1, weight=1)
        
        # Checkbox
        checkbox_var = ctk.BooleanVar(value=is_completed)
        
        def toggle_complete():
            self.db.toggle_mission_completion(mission["id"], checkbox_var.get())
            self.refresh_missions()
        
        checkbox = ctk.CTkCheckBox(card, variable=checkbox_var, command=toggle_complete)
        checkbox.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        # Mission name
        name_label = ctk.CTkLabel(
            card,
            text=mission["name"],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Click handler
        card.bind("<Button-1>", lambda e, m=mission: self.show_mission_details(m))
        
        # Mission description
        desc_label = ctk.CTkLabel(
            card,
            text=mission.get("description", ""),
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray50"),
            wraplength=400
        )
        desc_label.pack(anchor="w", padx=15, pady=(0, 10))
    
    def get_level_for_exercise(self, mission_id: str, exercise_name: str) -> str:
        """Get the required level for an exercise from the mission requirements."""
        # Check if we have requirements data for this mission
        requirements_key = f"requirements_{mission_id.lower()}"
        if requirements_key in self.missions_data:
            req_data = self.missions_data[requirements_key]
            if isinstance(req_data, dict) and exercise_name in req_data:
                return req_data[exercise_name]
        return "M"  # Default level
    
    def show_mission_details(self, mission: Dict):
        """Show detailed information about a mission."""
        self.current_mission = mission
        
        # Clear details (keep title label)
        children = list(self.detail_container.winfo_children())
        for widget in children:
            if widget != self.detail_title_label:
                widget.destroy()
        
        # Update title
        phase_letter = mission["id"].split("-")[0]
        phase_data = self.missions_data.get("missions", {}).get(phase_letter, {})
        self.detail_title_label.configure(text=f"{mission['name']} - {phase_data.get('name', '')}")
        self.detail_title_label.pack(anchor="w", padx=15, pady=10)
        
        # Mission header info
        info_frame = ctk.CTkFrame(self.detail_container)
        info_frame.pack(fill="x", padx=15, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(info_frame, text=f"💪 Nível: {mission.get('level', 'M')}", 
                     font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(info_frame, text=f"⏱️ Duração: {mission.get('duration', 'N/A')}", 
                     font=ctk.CTkFont(size=13)).grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Section: Objetivo
        obj_frame = ctk.CTkFrame(self.detail_container, corner_radius=8)
        obj_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(obj_frame, text="🎯 Objetivo da Missão", 
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=10)
        
        ctk.CTkLabel(
            obj_frame,
            text=mission.get("description", ""),
            font=ctk.CTkFont(size=13),
            wraplength=500,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Section: Exercícios Necessários
        exo_frame = ctk.CTkFrame(self.detail_container, corner_radius=8)
        exo_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(exo_frame, text="📋 Exercícios Necessários", 
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=10)
        
        # List of exercises with levels from requirements
        exercises_list = ctk.CTkScrollableFrame(exo_frame, height=250)
        exercises_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add exercises with their specific levels
        exercises = mission.get("exercises", [])
        for i, exercise in enumerate(exercises, 1):
            exercise_row = ctk.CTkFrame(exercises_list)
            exercise_row.pack(fill="x", pady=3)
            
            # Get the specific level for this exercise
            level = self.get_level_for_exercise(mission["id"], exercise)
            
            exercise_label = ctk.CTkLabel(
                exercise_row,
                text=f"{i}. {exercise}",
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            exercise_label.pack(side="left")
            
            level_label = ctk.CTkLabel(
                exercise_row,
                text=f"Nível: {level}",
                font=ctk.CTkFont(size=11),
                text_color=("gray60", "gray50")
            )
            level_label.pack(side="right")
        
        # Section: Critérios de Aprovação
        crit_frame = ctk.CTkFrame(self.detail_container, corner_radius=8)
        crit_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(crit_frame, text="✅ Critérios de Aprovação", 
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=10)
        
        ctk.CTkLabel(
            crit_frame,
            text="• Aprovado se obter Grau 3 ou superior em todos os exercícios\n" +
                 "• Grau 1 (Perigoso) ou 2 (Deficiente) em qualquer exercício resulta em reprovação\n" +
                 "• Revisão obrigatória em caso de falha",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray50"),
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Section: Tipo de Voo
        flight_type_label = ctk.CTkLabel(
            self.detail_container,
            text=f"Tipo de Voo: {mission.get('type', 'DC')}",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray50")
        )
        flight_type_label.pack(anchor="w", padx=15, pady=5)
    
    def update_theme(self):
        """Update UI for theme changes."""
        self.refresh_missions(self.search_entry.get())