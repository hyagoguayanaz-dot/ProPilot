"""
Central de Estudos View - Displays study materials and maneuver details.
"""

import customtkinter as ctk
from typing import Callable, Dict, List, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json


class StudyCenterView(ctk.CTkFrame):
    """View for displaying study materials and maneuver details."""
    
    def __init__(self, parent, on_maneuver_select: Callable = None, 
                 on_back: Callable = None, theme_manager=None):
        super().__init__(parent)
        self.on_maneuver_select = on_maneuver_select
        self.on_back = on_back
        self.theme_manager = theme_manager
        self.current_filter = ""
        self.current_category = "all"
        
        self.setup_ui()
        self.load_data()
        self.refresh_maneuvers()
    
    def setup_ui(self):
        """Set up the user interface components."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(self, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="📚 Central de Estudos",
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
        
        # Search and filter frame
        filter_frame = ctk.CTkFrame(header_frame)
        filter_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        filter_frame.grid_columnconfigure(0, weight=1)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="🔍 Buscar manobra, missão ou termo...",
            justify="left"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Category filter buttons
        category_frame = ctk.CTkFrame(filter_frame)
        category_frame.pack(side="right", fill="y", padx=5, pady=5)
        
        categories = ["Todos", "Básico", "Navegação"]
        for cat in categories:
            btn = ctk.CTkButton(
                category_frame,
                text=cat,
                width=80,
                command=lambda c=cat: self._filter_category(c)
            )
            btn.pack(side="left", padx=2)
        
        # Main content frame with paned window
        paned = ctk.CTkFrame(self)
        paned.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        paned.grid_rowconfigure(0, weight=1)
        paned.grid_columnconfigure(0, weight=1)
        
        # Left panel - Categories & List
        self.left_panel = ctk.CTkFrame(paned)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Categories label
        cat_label = ctk.CTkLabel(
            self.left_panel,
            text="📂 Categorias",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        cat_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Category scroll
        self.cat_canvas = ctk.CTkCanvas(self.left_panel, bg=self.cget("fg_color"), height=200)
        self.cat_canvas.pack(fill="both", expand=True, padx=10, pady=5)
        
        cat_scrollbar = ctk.CTkScrollbar(self.left_panel, command=self.cat_canvas.yview)
        cat_scrollbar.pack(side="right", fill="y")
        
        self.cat_canvas.configure(yscrollcommand=cat_scrollbar.set)
        
        self.cat_scrollable = ctk.CTkFrame(self.cat_canvas)
        self.cat_scrollable.grid_columnconfigure(0, weight=1)
        
        self.cat_window = self.cat_canvas.create_window((0, 0), window=self.cat_scrollable, anchor="nw")
        
        # Right panel - Details
        self.right_panel = ctk.CTkFrame(paned)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Details header
        detail_header = ctk.CTkFrame(self.right_panel)
        detail_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        detail_header.grid_columnconfigure(0, weight=1)
        
        self.detail_title = ctk.CTkLabel(
            detail_header,
            text="Selecione uma manobra",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.detail_title.pack(anchor="w", padx=15, pady=10)
        
        # Details content
        self.detail_content = ctk.CTkTextbox(
            self.right_panel,
            wrap="word",
            font=ctk.CTkFont(size=14)
        )
        self.detail_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.detail_content.configure(state="disabled")
        
        # Add paned window to main container
        self.paned_window = paned
        self.paned_window.grid_rowconfigure(0, weight=1)
        self.paned_window.grid_columnconfigure(0, weight=1)
    
    def _on_frame_configure(self, event):
        """Update canvas scroll region when frame size changes."""
        self.cat_canvas.configure(scrollregion=self.cat_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Resize canvas window when canvas size changes."""
        canvas_width = event.width
        self.cat_canvas.itemconfig(self.cat_window, width=canvas_width)
    
    def _go_back(self):
        """Navigate back to previous view."""
        if self.on_back:
            self.on_back()
    
    def load_data(self):
        """Load maneuver data from JSON file."""
        try:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "missions.json")
            with open(data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"maneuvers": {"basic": [], "navigation": []}, "phases": {}}
    
    def on_search(self, event=None):
        """Filter maneuvers based on search text."""
        self.current_filter = self.search_entry.get()
        self.refresh_maneuvers()
    
    def _filter_category(self, category: str):
        """Filter by category."""
        if category == "Todos":
            self.current_category = "all"
        else:
            self.current_category = category.lower()
        self.refresh_maneuvers()
    
    def refresh_maneuvers(self):
        """Refresh and display maneuvers list."""
        # Clear categories
        for widget in self.cat_scrollable.winfo_children():
            widget.destroy()
        
        # Get maneuvers
        maneuvers = []
        
        if self.current_category in ["all", "basic"]:
            maneuvers.extend(self.data.get("maneuvers", {}).get("basic", []))
        
        if self.current_category in ["all", "navigation"]:
            maneuvers.extend(self.data.get("maneuvers", {}).get("navigation", []))
        
        # Filter by search
        if self.current_filter:
            filter_lower = self.current_filter.lower()
            maneuvers = [m for m in maneuvers 
                        if filter_lower in m.get("name", "").lower() or
                           filter_lower in m.get("description", "").lower()]
        
        # Display maneuvers
        for i, maneuver in enumerate(maneuvers):
            card = self._create_maneuver_card(maneuver)
            card.pack(fill="x", padx=10, pady=3)
        
        # Update canvas
        self.cat_canvas.configure(scrollregion=self.cat_canvas.bbox("all"))
    
    def _create_maneuver_card(self, maneuver: Dict) -> ctk.CTkFrame:
        """Create a maneuver card widget."""
        card = ctk.CTkFrame(
            self.cat_scrollable,
            corner_radius=8,
            border_width=1,
            border_color=("gray60", "gray40")
        )
        card.grid_columnconfigure(0, weight=1)
        
        # Maneuver name
        name_label = ctk.CTkLabel(
            card,
            text=maneuver.get("name", "Sem nome"),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w", padx=15, pady=10)
        
        # Category and phase info
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(fill="x", padx=15, pady=(0, 10))
        info_frame.grid_columnconfigure(1, weight=1)
        
        cat_label = ctk.CTkLabel(
            info_frame,
            text=maneuver.get("category", "Geral"),
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray50")
        )
        cat_label.grid(row=0, column=0, sticky="w")
        
        phase_label = ctk.CTkLabel(
            info_frame,
            text=maneuver.get("phase", ""),
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray50")
        )
        phase_label.grid(row=0, column=1, sticky="e")
        
        # Click handler
        card.bind("<Button-1", lambda e, m=maneuver: self._select_maneuver(m))
        
        return card
    
    def _select_maneuver(self, maneuver: Dict):
        """Handle maneuver selection and show details."""
        if self.on_maneuver_select:
            self.on_maneuver_select(maneuver)
        self.show_maneuver_details(maneuver)
    
    def show_maneuver_details(self, maneuver: Dict):
        """Display detailed information about a maneuver."""
        self.detail_title.configure(text=maneuver.get("name", "Detalhes"))
        
        details = []
        details.append(f"📋 **{maneuver.get('name', 'Sem nome')}**\n\n")
        details.append(f"**Categoria:** {maneuver.get('category', 'N/A')}\n\n")
        details.append(f"**Fase:** {maneuver.get('phase', 'N/A')}\n\n")
        details.append(f"**Descrição:** {maneuver.get('description', 'Sem descrição')}\n\n")
        
        # Steps
        steps = maneuver.get("steps", [])
        if steps:
            details.append("**Passos de Execução:**\n")
            for i, step in enumerate(steps, 1):
                details.append(f"  {i}. {step}\n")
            details.append("\n")
        
        # Prerequisites
        prereq = maneuver.get("prerequisites", "")
        if prereq or maneuver.get("common_errors"):
            details.append("**Pré-requisitos:** ")
            details.append(f"{prereq if prereq else 'Conhecimento básico'}\n\n")
        
        # Common errors
        errors = maneuver.get("common_errors", [])
        if errors:
            details.append("**Erros Comuns a Evitar:**\n")
            for error in errors:
                details.append(f"  • {error}\n")
        
        # Safety note
        details.append("\n**⚠️ Nota de Segurança:**\n")
        details.append("Sempre execute manobras sob supervisão de instrutor durante a fase de treinamento.")
        
        # Set content
        content = "".join(details)
        self.detail_content.configure(state="normal")
        self.detail_content.delete("1.0", "end")
        self.detail_content.insert("1.0", content)
        self.detail_content.configure(state="disabled")
    
    def update_theme(self):
        """Update UI for theme changes."""
        self.detail_content.configure(state="normal")
        self.detail_content.delete("1.0", "end")
        self.detail_content.insert("1.0", "")
        self.detail_content.configure(state="disabled")
        self.refresh_maneuvers()