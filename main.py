#!/usr/bin/env python3
"""
Pro Pilot - Aviation Training Application
Piloto Privado de Avião - PPA
"""
import customtkinter as ctk
import sys
import os

__version__ = "1.0.0"

try:
    from views.missions_view import MissionsView
    from views.study_center_view import StudyCenterView
    from views.settings_view import SettingsView
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from views.missions_view import MissionsView
    from views.study_center_view import StudyCenterView
    from views.settings_view import SettingsView

try:
    from database import get_database
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from database import get_database


class ThemeManager:
    THEMES = {"dark": {"mode": "Dark"}, "light": {"mode": "Light"}}
    def __init__(self):
        self.current_theme = "dark"
        try:
            db = get_database()
            t = db.load_settings().get("theme", "dark")
            if t in self.THEMES:
                self.current_theme = t
        except Exception:
            pass
    def apply_theme(self, app):
        ctk.set_appearance_mode(self.current_theme)
    def set_theme(self, theme):
        if theme in self.THEMES:
            self.current_theme = theme
            ctk.set_appearance_mode(theme)
            try:
                db = get_database()
                s = db.load_settings()
                s["theme"] = theme
                db.save_settings(s)
            except Exception:
                pass


class ProPilotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.db = get_database()
        self._configure_window()
        self.theme_manager.apply_theme(self)
        self._setup_ui()
        self.show_dashboard()

    def _configure_window(self):
        self.title("Pro Pilot - Piloto Privado de Aviao")
        self.geometry("1120x720")
        self.minsize(1000, 620)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _setup_ui(self):
        # root container
        main_container = ctk.CTkFrame(self, corner_radius=0)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=0)  # sidebar fixed
        main_container.grid_columnconfigure(1, weight=1)  # content expands
        main_container.grid_rowconfigure(0, weight=0)  # header
        main_container.grid_rowconfigure(1, weight=1)  # body

        # Header
        header = ctk.CTkFrame(main_container, corner_radius=0, height=64)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Pro Pilot", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, padx=16, pady=12, sticky="w")
        self.phase_indicator = ctk.CTkLabel(header, text="Fase: Pre-Solo", font=ctk.CTkFont(size=13), text_color=("gray40","gray60"))
        self.phase_indicator.grid(row=0, column=1, padx=10, sticky="e")
        self.theme_btn = ctk.CTkButton(header, text="🌙" if self.theme_manager.current_theme=="dark" else "☀️", width=48, command=self._toggle_theme)
        self.theme_btn.grid(row=0, column=2, padx=10, sticky="e")

        # Sidebar
        nav = ctk.CTkFrame(main_container, width=210, corner_radius=10)
        nav.grid(row=1, column=0, sticky="ns", padx=(10,5), pady=(0,10))
        nav.grid_propagate(False)
        for t,k in [("Dashboard","dashboard"),("Missoes & Progresso","missions"),("Central de Estudos","study"),("Configuracoes","settings")]:
            ctk.CTkButton(nav, text=t, anchor="w", height=42, command=lambda kk=k: self._navigate_to(kk)).pack(fill="x", padx=10, pady=6)
        ctk.CTkLabel(nav, text="Aeroclube de\nPirassununga", font=ctk.CTkFont(size=11), text_color=("gray50","gray60"), justify="center").pack(side="bottom", pady=14)

        # Content
        self.content_frame = ctk.CTkFrame(main_container, corner_radius=10)
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=(5,10), pady=(0,10))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def _toggle_theme(self):
        new = "light" if self.theme_manager.current_theme=="dark" else "dark"
        self.theme_manager.set_theme(new)
        self.theme_btn.configure(text="☀️" if new=="light" else "🌙")

    def _navigate_to(self, section):
        {"dashboard": self.show_dashboard, "missions": self.show_missions, "study": self.show_study_center, "settings": self.show_settings}[section]()

    def show_dashboard(self):
        self._clear()
        self._render_dashboard()
        self._update_phase()

    def show_missions(self):
        self._clear()
        MissionsView(self.content_frame, on_back=self.show_dashboard, theme_manager=self.theme_manager).grid(row=0,column=0,sticky="nsew", padx=8, pady=8)
        self._update_phase()

    def show_study_center(self):
        self._clear()
        StudyCenterView(self.content_frame, on_back=self.show_dashboard, theme_manager=self.theme_manager).grid(row=0,column=0,sticky="nsew", padx=8, pady=8)

    def show_settings(self):
        self._clear()
        SettingsView(self.content_frame, on_back=self.show_dashboard, theme_manager=self.theme_manager).grid(row=0,column=0,sticky="nsew", padx=8, pady=8)

    def _clear(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def _render_dashboard(self):
        f = ctk.CTkScrollableFrame(self.content_frame, corner_radius=10)
        f.grid(row=0,column=0,sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(f, text="Bem-vindo ao Pro Pilot", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(18,2))
        ctk.CTkLabel(f, text="Sua jornada rumo ao voo solo comeca aqui", font=ctk.CTkFont(size=13), text_color=("gray50","gray60")).pack(pady=(0,14))

        summary = self.db.get_progress_summary()
        prog = self.db.load_progress().get("study_progress", {})

        cards = ctk.CTkFrame(f, fg_color="transparent")
        cards.pack(fill="x", padx=16, pady=6)
        cards.grid_columnconfigure((0,1,2), weight=1)
        # card 1
        c1 = ctk.CTkFrame(cards); c1.grid(row=0,column=0, padx=6, sticky="ew")
        ctk.CTkLabel(c1, text="Progresso geral", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(10,0))
        ctk.CTkLabel(c1, text=f"{summary['progress_percentage']}%", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=6)
        total_est = sum(v.get("total",0) for v in prog.values()) or 43
        ctk.CTkLabel(c1, text=f"{summary['completed_missions']}/{total_est} missoes", text_color=("gray50","gray60")).pack(pady=(0,10))
        # card 2
        c2 = ctk.CTkFrame(cards); c2.grid(row=0,column=1, padx=6, sticky="ew")
        ctk.CTkLabel(c2, text="Fase atual", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(10,0))
        ctk.CTkLabel(c2, text=self._phase_name(summary.get("current_phase","PS")), font=ctk.CTkFont(size=18, weight="bold")).pack(pady=6)
        ctk.CTkLabel(c2, text=f"{prog.get(summary.get('current_phase','PS'),{}).get('completed',0)} concluidas", text_color=("gray50","gray60")).pack(pady=(0,10))
        # card 3
        c3 = ctk.CTkFrame(cards); c3.grid(row=0,column=2, padx=6, sticky="ew")
        ctk.CTkLabel(c3, text="Horas estimadas", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(10,0))
        ctk.CTkLabel(c3, text="43h voo", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=6)
        ctk.CTkLabel(c3, text="20 PS + 10 AP + 10 NV + 3 NOT", text_color=("gray50","gray60"), font=ctk.CTkFont(size=11)).pack(pady=(0,10))

        btns = ctk.CTkFrame(f, fg_color="transparent"); btns.pack(fill="x", padx=16, pady=12)
        btns.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(btns, text="Ver Missoes", height=46, command=self.show_missions).grid(row=0,column=0, padx=6, sticky="ew")
        ctk.CTkButton(btns, text="Estudar Manobras", height=46, fg_color=("gray70","gray25"), hover_color=("gray60","gray30"), command=self.show_study_center).grid(row=0,column=1, padx=6, sticky="ew")

        ctk.CTkLabel(f, text="Progresso por fase", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=18, pady=(10,4))
        bars = ctk.CTkFrame(f); bars.pack(fill="x", padx=16, pady=6)
        for code, name, col in [("PS","Pre-Solo","#3498db"),("AP","Aperfeicoamento","#2ecc71"),("NV","Navegacao","#9b59b6"),("NOT","Noturno","#e74c3c")]:
            info = prog.get(code, {"completed":0,"total":1})
            pct = min(info.get("completed",0)/max(info.get("total",1),1),1.0)
            row = ctk.CTkFrame(bars, fg_color="transparent"); row.pack(fill="x", pady=5, padx=8)
            ctk.CTkLabel(row, text=name, width=140, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left")
            pb = ctk.CTkProgressBar(row, height=10, progress_color=col); pb.set(pct); pb.pack(side="left", fill="x", expand=True, padx=8)
            ctk.CTkLabel(row, text=f"{info.get('completed',0)}/{info.get('total',1)}", width=70, font=ctk.CTkFont(size=11), text_color=("gray50","gray60")).pack(side="left")

        recent = ctk.CTkFrame(f); recent.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(recent, text="Missoes recentes", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(10,4))
        done = self.db.load_progress().get("completed_missions", [])
        if done:
            for m in done[:6]:
                ctk.CTkLabel(recent, text=f"  ✓  {m}", anchor="w").pack(fill="x", padx=12, pady=2)
        else:
            ctk.CTkLabel(recent, text="Nenhuma missao concluida ainda — marque no quadro de missoes.", text_color=("gray50","gray60")).pack(pady=12)

    def _update_phase(self):
        try:
            cur = self.db.load_progress().get("profile",{}).get("current_phase","PS")
            self.phase_indicator.configure(text=f"Fase: {self._phase_name(cur)}")
        except: pass
    def _phase_name(self, c):
        return {"PS":"Pre-Solo","AP":"Aperfeicoamento","NV":"Navegacao","NOT":"Noturno"}.get(c, c)
    def _show_maneuver_details(self, m): pass

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ProPilotApp()
    app.mainloop()

if __name__ == "__main__":
    main()
