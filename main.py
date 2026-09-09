#!/usr/bin/env python3
"""
Pro Pilot - Spotify Edition
UI moderna inspirada no Spotify com paleta de cores selecionável
"""
import customtkinter as ctk
import sys, os
from pathlib import Path

__version__ = "2.0.0"

try:
    from views.missions_view import MissionsView
    from views.study_center_view import StudyCenterView
    from views.settings_view import SettingsView
    from views.manuals_view import ManualsView
    from views.sop_view import SOPView
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from views.missions_view import MissionsView
    from views.study_center_view import StudyCenterView
    from views.settings_view import SettingsView
    from views.manuals_view import ManualsView
    from views.sop_view import SOPView

try:
    from database import get_database
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from database import get_database

# Paleta Spotify + variantes
ACCENTS = {
    "spotify": {"name":"Spotify Green","color":"#1DB954","hover":"#1ED760","light":"#1DB954"},
    "ocean":   {"name":"Ocean Blue","color":"#3B82F6","hover":"#60A5FA","light":"#2563EB"},
    "violet":  {"name":"Violet Haze","color":"#8B5CF6","hover":"#A78BFA","light":"#7C3AED"},
    "pink":    {"name":"Hot Pink","color":"#EC4899","hover":"#F472B6","light":"#DB2777"},
    "sunset":  {"name":"Sunset Orange","color":"#F59E0B","hover":"#FBBF24","light":"#D97706"},
    "crimson": {"name":"Crimson Red","color":"#EF4444","hover":"#F87171","light":"#DC2626"},
    "teal":    {"name":"Teal Wave","color":"#06B6D4","hover":"#22D3EE","light":"#0891B2"},
    "lime":    {"name":"Lime Pulse","color":"#84CC16","hover":"#A3E635","light":"#65A30D"},
}

# Cores Spotify
SPOTIFY_DARK = {
    "bg": "#000000",
    "sidebar": "#000000",
    "content": "#121212",
    "card": "#181818",
    "card_hover": "#282828",
    "elevated": "#242424",
    "text": "#FFFFFF",
    "subtext": "#B3B3B3",
    "line": "#2A2A2A",
}
SPOTIFY_LIGHT = {
    "bg": "#F5F5F5",
    "sidebar": "#FFFFFF",
    "content": "#FFFFFF",
    "card": "#F0F0F0",
    "card_hover": "#E8E8E8",
    "elevated": "#E5E5E5",
    "text": "#121212",
    "subtext": "#6A6A6A",
    "line": "#E0E0E0",
}

class ThemeManager:
    def __init__(self):
        self.current_theme = "dark"
        self.current_accent = "spotify"
        self._load()
    def _load(self):
        try:
            db = get_database()
            s = db.load_settings()
            t = s.get("theme","dark")
            if t in ("dark","light"): self.current_theme = t
            a = s.get("accent","spotify")
            if a in ACCENTS: self.current_accent = a
        except: pass
    def get_accent(self): return ACCENTS[self.current_accent]["color"]
    def get_accent_hover(self): return ACCENTS[self.current_accent]["hover"]
    def get_colors(self): return SPOTIFY_DARK if self.current_theme=="dark" else SPOTIFY_LIGHT
    def apply(self, app=None):
        ctk.set_appearance_mode(self.current_theme)
        if app: app.configure(fg_color=self.get_colors()["bg"])
    def set_theme(self, theme):
        if theme in ("dark","light"):
            self.current_theme = theme
            ctk.set_appearance_mode(theme)
            self._save()
            # força reload visual: precisa reiniciar? apenas salva, main troca bg
    def set_accent(self, accent):
        if accent in ACCENTS:
            self.current_accent = accent
            self._save()
    def _save(self):
        try:
            db = get_database()
            s = db.load_settings()
            s["theme"] = self.current_theme
            s["accent"] = self.current_accent
            db.save_settings(s)
        except: pass

# singleton para views
_theme_instance = None
def get_theme_manager():
    global _theme_instance
    if _theme_instance is None:
        _theme_instance = ThemeManager()
    return _theme_instance

class ProPilotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.theme_manager = get_theme_manager()
        global _theme_instance; _theme_instance = self.theme_manager
        self.db = get_database()
        self._active_nav = "dashboard"
        self.nav_buttons = {}
        self._configure_window()
        self.theme_manager.apply(self)
        self._setup_ui()
        self.show_dashboard()

    def _configure_window(self):
        self.title("Pro Pilot")
        self.geometry("1240x760")
        self.minsize(1100, 640)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        try:
            ico = Path(__file__).parent / "assets" / "icon.ico"
            png = Path(__file__).parent / "assets" / "icon.png"
            if ico.exists():
                self.iconbitmap(str(ico))
            elif png.exists():
                from PIL import Image, ImageTk
                im = Image.open(png).resize((32,32))
                self._icon_img = ImageTk.PhotoImage(im)
                self.iconphoto(True, self._icon_img)
        except: pass

    def _setup_ui(self):
        cols = self.theme_manager.get_colors()
        acc = self.theme_manager.get_accent()
        # root bg
        self.configure(fg_color=cols["bg"])
        # container com gap 8 como Spotify
        root = ctk.CTkFrame(self, fg_color=cols["bg"], corner_radius=0)
        root.grid(row=0,column=0, sticky="nsew", padx=8, pady=8)
        root.grid_columnconfigure(0, weight=0)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        # SIDEBAR - estilo Spotify (preto, cantos arredondados)
        self.sidebar = ctk.CTkFrame(root, fg_color=cols["sidebar"], corner_radius=8, width=232)
        self.sidebar.grid(row=0,column=0, sticky="ns", padx=(0,8), pady=0)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(99, weight=1)

        # Logo
        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.pack(fill="x", padx=16, pady=(18,10))
        # ícone + texto
        try:
            from PIL import Image, ImageTk
            png = Path(__file__).parent / "assets" / "icon.png"
            if png.exists():
                im = Image.open(png).resize((28,28))
                self._logo_img = ImageTk.PhotoImage(im)
                ctk.CTkLabel(logo, image=self._logo_img, text="").pack(side="left")
        except: pass
        ctk.CTkLabel(logo, text="Pro Pilot", font=ctk.CTkFont(size=18, weight="bold"), text_color=cols["text"]).pack(side="left", padx=8)
        ctk.CTkLabel(self.sidebar, text="PILOTO PRIVADO • PPA", font=ctk.CTkFont(size=10), text_color=cols["subtext"]).pack(anchor="w", padx=16, pady=(0,14))

        # Nav items - estilo Spotify
        nav_items = [
            ("⌂","Dashboard","dashboard"),
            ("◫","Missões","missions"),
            ("▤","Central de Estudos","study"),
            ("▭","QRH / Manuais","manuals"),
            ("≡","SOP","sop"),
            ("⚙","Configurações","settings"),
        ]
        for icon, label, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {icon}  {label}",
                anchor="w", height=36, corner_radius=4,
                fg_color="transparent", hover_color=cols["card_hover"],
                text_color=cols["subtext"], font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda k=key: self._navigate_to(k)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_buttons[key] = btn

        # separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color=cols["line"]).pack(fill="x", padx=16, pady=10)

        # Card de fase no sidebar (estilo playlist)
        self.side_card = ctk.CTkFrame(self.sidebar, fg_color=cols["card"], corner_radius=8)
        self.side_card.pack(fill="x", padx=8, pady=6)
        ctk.CTkLabel(self.side_card, text="Sua fase", font=ctk.CTkFont(size=11, weight="bold"), text_color=cols["subtext"]).pack(anchor="w", padx=12, pady=(10,2))
        self.side_phase_label = ctk.CTkLabel(self.side_card, text="Pré-Solo", font=ctk.CTkFont(size=14, weight="bold"), text_color=cols["text"])
        self.side_phase_label.pack(anchor="w", padx=12)
        self.side_progress = ctk.CTkProgressBar(self.side_card, height=4, progress_color=acc, fg_color=cols["line"])
        self.side_progress.pack(fill="x", padx=12, pady=8)
        self.side_progress.set(0)
        self.side_sub = ctk.CTkLabel(self.side_card, text="0/0 missões", font=ctk.CTkFont(size=11), text_color=cols["subtext"])
        self.side_sub.pack(anchor="w", padx=12, pady=(0,10))

        # Footer sidebar
        ctk.CTkLabel(self.sidebar, text="© Guayanaz Systems", font=ctk.CTkFont(size=10), text_color=cols["subtext"]).pack(side="bottom", pady=10)

        # CONTENT - caixa principal arredondada (como feed do Spotify)
        self.content_wrap = ctk.CTkFrame(root, fg_color=cols["content"], corner_radius=8)
        self.content_wrap.grid(row=0,column=1, sticky="nsew")
        self.content_wrap.grid_columnconfigure(0, weight=1)
        self.content_wrap.grid_rowconfigure(0, weight=0)
        self.content_wrap.grid_rowconfigure(1, weight=1)
        # top bar inside content (estilo Spotify header com gradiente)
        self.topbar = ctk.CTkFrame(self.content_wrap, fg_color=cols["content"], corner_radius=8, height=56)
        self.topbar.grid(row=0,column=0, sticky="ew", padx=0, pady=0)
        self.topbar.grid_columnconfigure(0, weight=1)
        self.topbar.grid_propagate(False)
        self.top_title = ctk.CTkLabel(self.topbar, text="Boa tarde, piloto", font=ctk.CTkFont(size=16, weight="bold"), text_color=cols["text"])
        self.top_title.pack(side="left", padx=20, pady=14)
        self.top_sub = ctk.CTkLabel(self.topbar, text="", font=ctk.CTkFont(size=12), text_color=cols["subtext"])
        self.top_sub.pack(side="left", padx=6, pady=14)
        # actions topbar - apenas tema
        self.theme_btn = ctk.CTkButton(self.topbar, text="🌙" if self.theme_manager.current_theme=="dark" else "☀️", width=36, height=32, corner_radius=16, fg_color=cols["card"], hover_color=cols["card_hover"], command=self._toggle_theme)
        self.theme_btn.pack(side="right", padx=12, pady=12)

        # content frame (scrollable views entram aqui)
        self.content_frame = ctk.CTkFrame(self.content_wrap, fg_color="transparent")
        self.content_frame.grid(row=1,column=0, sticky="nsew", padx=0, pady=(0,8))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self._highlight_nav("dashboard")

    def _quick_accent(self, aid):
        # mantido apenas para ser chamado pela aba Configurações
        self.theme_manager.set_accent(aid)
        acc = self.theme_manager.get_accent()
        self.side_progress.configure(progress_color=acc)
        self._highlight_nav(self._active_nav)
        if self._active_nav in ("dashboard","settings"):
            self._navigate_to(self._active_nav)

    def _toggle_theme(self):
        new = "light" if self.theme_manager.current_theme=="dark" else "dark"
        self.theme_manager.set_theme(new)
        cols = self.theme_manager.get_colors()
        acc = self.theme_manager.get_accent()
        self.configure(fg_color=cols["bg"])
        self.sidebar.configure(fg_color=cols["sidebar"])
        self.content_wrap.configure(fg_color=cols["content"])
        self.topbar.configure(fg_color=cols["content"])
        self.side_card.configure(fg_color=cols["card"])
        # atualiza textos da sidebar e topbar para não ficarem brancos no modo claro
        try:
            # sidebar texts
            for w in self.sidebar.winfo_children():
                if isinstance(w, ctk.CTkLabel):
                    # PILOTO PRIVADO e copyright
                    w.configure(text_color=cols["subtext"])
            # side_card labels
            for w in self.side_card.winfo_children():
                if isinstance(w, ctk.CTkLabel):
                    txt = str(w.cget("text"))
                    if "Sua fase" in txt or "missões" in txt:
                        w.configure(text_color=cols["subtext"])
                    else:
                        w.configure(text_color=cols["text"])
            self.side_progress.configure(progress_color=acc, fg_color=cols["line"])
        except: pass
        self.theme_btn.configure(text="☀️" if new=="light" else "🌙", fg_color=cols["card"], hover_color=cols["card_hover"], text_color=cols["text"])
        self.top_title.configure(text_color=cols["text"])
        self.top_sub.configure(text_color=cols["subtext"])
        self._highlight_nav(self._active_nav)
        self._update_phase()
        # recarrega view atual para recriar cards com cores corretas (evita itens brancos)
        try:
            cur = self._active_nav
            # evita loop se já estiver reconstruindo settings (que já se reconstrói sozinho)
            if cur != "settings":
                self._navigate_to(cur)
        except: pass

    def _highlight_nav(self, active):
        cols = self.theme_manager.get_colors()
        acc = self.theme_manager.get_accent()
        for k, btn in self.nav_buttons.items():
            if k==active:
                btn.configure(fg_color=cols["card"], text_color=cols["text"], border_width=0)
                # left accent indicator via fg - usar hover como destaque não tem borda lateral no CTk, então usa cor de fundo
                btn.configure(fg_color=acc if self.theme_manager.current_theme=="dark" else acc)
                btn.configure(text_color="white" if self.theme_manager.current_theme=="dark" else "white")
                # para Spotify-like, volta a card com accent left: simula com darker
                # mantém contraste: se accent claro, texto branco ok
            else:
                btn.configure(fg_color="transparent", text_color=cols["subtext"], hover_color=cols["card_hover"], border_width=0)
        self._active_nav = active

    def _navigate_to(self, section):
        self._highlight_nav(section)
        titles = {"dashboard":"Boa tarde, piloto","missions":"Suas missões","study":"Central de Estudos","manuals":"QRH / Manuais","sop":"SOP","settings":"Configurações"}
        self.top_title.configure(text=titles.get(section,"Pro Pilot"))
        subs = {"dashboard":"Organize seu progresso","missions":"Toque no card para detalhes","study":"Toque na manobra para passo-a-passo","manuals":"Manuais por aeronave","sop":"Procedimentos padronizados ACP 2023","settings":"Tema, cores e perfil"}
        self.top_sub.configure(text=subs.get(section,""))
        {"dashboard": self.show_dashboard, "missions": self.show_missions, "study": self.show_study_center, "manuals": self.show_manuals, "sop": self.show_sop, "settings": self.show_settings}[section]()

    def show_dashboard(self):
        self._clear(); self._render_dashboard(); self._update_phase()
    def show_missions(self):
        self._clear(); MissionsView(self.content_frame, on_back=self.show_dashboard, theme_manager=self.theme_manager).grid(row=0,column=0,sticky="nsew", padx=8, pady=8); self._update_phase()
    def show_study_center(self):
        self._clear(); StudyCenterView(self.content_frame, on_back=self.show_dashboard, theme_manager=self.theme_manager).grid(row=0,column=0,sticky="nsew", padx=8, pady=8)
    def show_manuals(self):
        self._clear(); ManualsView(self.content_frame, on_back=self.show_dashboard, theme_manager=self.theme_manager).grid(row=0,column=0,sticky="nsew", padx=8, pady=8)
    def show_sop(self):
        self._clear(); SOPView(self.content_frame, on_back=self.show_dashboard, theme_manager=self.theme_manager).grid(row=0,column=0,sticky="nsew", padx=8, pady=8)
    def show_settings(self):
        self._clear(); SettingsView(self.content_frame, on_back=self.show_dashboard, theme_manager=self.theme_manager).grid(row=0,column=0,sticky="nsew", padx=8, pady=8)
    def _clear(self):
        for w in self.content_frame.winfo_children(): w.destroy()

    def _render_dashboard(self):
        cols = self.theme_manager.get_colors()
        acc = self.theme_manager.get_accent()
        acc_hover = self.theme_manager.get_accent_hover()
        f = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        f.grid(row=0,column=0,sticky="nsew", padx=4, pady=4)

        # Saudação personalizada por horário + nome do piloto
        from datetime import datetime
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greet = "Bom dia"
        elif 12 <= hour < 18:
            greet = "Boa tarde"
        else:
            greet = "Boa noite"
        prof_name = self.db.load_progress().get("profile",{}).get("display_name","Piloto-Aluno") or "Piloto-Aluno"
        # usa primeiro nome para saudação mais pessoal, mas mantém completo no subtítulo
        first = prof_name.split()[0]

        # Hero card (gradiente simulado com frame color)
        hero = ctk.CTkFrame(f, fg_color=cols["card"], corner_radius=12)
        hero.pack(fill="x", padx=12, pady=12)
        hero.grid_columnconfigure(0, weight=1)
        inner = ctk.CTkFrame(hero, fg_color=acc, corner_radius=12)
        inner.pack(fill="x", padx=0, pady=0)
        # faixa superior com accent
        ctk.CTkLabel(inner, text="", height=4, fg_color=acc).pack(fill="x")
        # conteúdo hero
        ctk.CTkLabel(hero, text=f"{greet}, {first}!", font=ctk.CTkFont(size=13), text_color=cols["subtext"]).pack(anchor="w", padx=18, pady=(14,2))
        ctk.CTkLabel(hero, text=prof_name, font=ctk.CTkFont(size=22, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=18)
        ctk.CTkLabel(hero, text="Sua jornada rumo ao voo solo continua — escolha uma missão ou revise uma manobra", font=ctk.CTkFont(size=12), text_color=cols["subtext"], wraplength=700, justify="left").pack(anchor="w", padx=18, pady=(4,14))
        btns = ctk.CTkFrame(hero, fg_color="transparent"); btns.pack(fill="x", padx=18, pady=(0,14))
        ctk.CTkButton(btns, text="▶  Ver Missões", fg_color=acc, hover_color=acc_hover, text_color="white", corner_radius=20, height=36, width=150, command=self.show_missions).pack(side="left", padx=(0,8))
        ctk.CTkButton(btns, text="Estudar manobras", fg_color=cols["elevated"], hover_color=cols["card_hover"], text_color=cols["text"], corner_radius=20, height=36, command=self.show_study_center).pack(side="left")

        summary = self.db.get_progress_summary()
        study = self.db.load_progress().get("study_progress",{})
        # Cards grid - estilo Spotify "Made for you"
        ctk.CTkLabel(f, text="Seu progresso", font=ctk.CTkFont(size=18, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(8,8))
        grid = ctk.CTkFrame(f, fg_color="transparent"); grid.pack(fill="x", padx=12, pady=0)
        grid.grid_columnconfigure((0,1,2), weight=1)
        # card template
        def card(parent, title, big, sub, col):
            c = ctk.CTkFrame(parent, fg_color=cols["card"], corner_radius=8)
            c.pack_propagate(False)
            # hover effect simula via bind
            def on_enter(e): c.configure(fg_color=cols["card_hover"])
            def on_leave(e): c.configure(fg_color=cols["card"])
            c.bind("<Enter>", on_enter); c.bind("<Leave>", on_leave)
            ctk.CTkLabel(c, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=cols["subtext"]).pack(anchor="w", padx=14, pady=(14,4))
            ctk.CTkLabel(c, text=big, font=ctk.CTkFont(size=24, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=14)
            ctk.CTkLabel(c, text=sub, font=ctk.CTkFont(size=11), text_color=cols["subtext"]).pack(anchor="w", padx=14, pady=(0,14))
            return c
        total_est = sum(v.get("total",0) for v in study.values()) or 7
        card(grid, "Progresso geral", f"{summary['progress_percentage']}%", f"{summary['completed_missions']}/{total_est} missões", acc).grid(row=0,column=0, padx=6, sticky="ew")
        card(grid, "Fase atual", self._phase_name(summary.get("current_phase","PS")), f"{study.get(summary.get('current_phase','PS'),{}).get('completed',0)} concluídas", acc).grid(row=0,column=1, padx=6, sticky="ew")
        card(grid, "Horas estimadas", "43h voo", "20 PS + 10 AP + 10 NV + 3 NOT", acc).grid(row=0,column=2, padx=6, sticky="ew")
        # Ajusta altura
        for ch in grid.winfo_children():
            ch.configure(height=110)

        # Progresso por fase - barras estilo Spotify
        ctk.CTkLabel(f, text="Progresso por fase", font=ctk.CTkFont(size=16, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(16,6))
        bars = ctk.CTkFrame(f, fg_color=cols["card"], corner_radius=8); bars.pack(fill="x", padx=12, pady=0)
        phases = [("PS","Pré-Solo"),("AP","Aperfeiçoamento"),("NV","Navegação"),("NOT","Noturno")]
        phase_cols = {"PS": acc, "AP": acc, "NV": acc, "NOT": acc}
        # cada barra usa accent mas com opacidade diferente? usa mesmo accent
        for code, name in phases:
            info = study.get(code, {"completed":0,"total":1})
            pct = min(info.get("completed",0)/max(info.get("total",1),1),1.0)
            row = ctk.CTkFrame(bars, fg_color="transparent"); row.pack(fill="x", padx=14, pady=8)
            ctk.CTkLabel(row, text=name, width=150, anchor="w", font=ctk.CTkFont(size=12), text_color=cols["text"]).pack(side="left")
            pb = ctk.CTkProgressBar(row, height=6, corner_radius=3, progress_color=acc, fg_color=cols["elevated"]); pb.set(pct); pb.pack(side="left", fill="x", expand=True, padx=8)
            ctk.CTkLabel(row, text=f"{info.get('completed',0)}/{info.get('total',1)}", width=50, font=ctk.CTkFont(size=11), text_color=cols["subtext"]).pack(side="left")

        # Tocadas recentemente (estilo Spotify "Recently played")
        ctk.CTkLabel(f, text="Tocadas recentemente", font=ctk.CTkFont(size=16, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(16,6))
        recent_wrap = ctk.CTkFrame(f, fg_color="transparent"); recent_wrap.pack(fill="x", padx=12, pady=(0,12))
        done = self.db.load_progress().get("completed_missions",[])
        if done:
            # grid 2 col
            recent_wrap.grid_columnconfigure((0,1), weight=1)
            for idx, mid in enumerate(done[:6]):
                r = ctk.CTkFrame(recent_wrap, fg_color=cols["card"], corner_radius=6)
                r.grid(row=idx//2, column=idx%2, padx=6, pady=6, sticky="ew")
                ctk.CTkLabel(r, text="✓", width=32, height=32, corner_radius=16, fg_color=acc, text_color="white", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
                ctk.CTkLabel(r, text=mid, font=ctk.CTkFont(weight="bold"), text_color=cols["text"], anchor="w").pack(side="left")
                ctk.CTkLabel(r, text="Concluída", font=ctk.CTkFont(size=11), text_color=cols["subtext"]).pack(side="right", padx=10)
        else:
            box = ctk.CTkFrame(f, fg_color=cols["card"], corner_radius=8); box.pack(fill="x", padx=12, pady=6)
            ctk.CTkLabel(box, text="Nenhuma missão concluída ainda", font=ctk.CTkFont(size=13, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(14,2))
            ctk.CTkLabel(box, text="Marque uma missão no Quadro de Missões para ver seu progresso aqui.", text_color=cols["subtext"], wraplength=600, justify="left").pack(anchor="w", padx=16, pady=(0,14))

    def _update_phase(self):
        try:
            prog = self.db.load_progress()
            cur = prog.get("profile",{}).get("current_phase","PS")
            self.side_phase_label.configure(text=self._phase_name(cur))
            study = prog.get("study_progress",{}).get(cur,{"completed":0,"total":1})
            pct = study.get("completed",0)/max(study.get("total",1),1)
            self.side_progress.set(min(pct,1.0))
            self.side_sub.configure(text=f"{study.get('completed',0)}/{study.get('total',1)} missões")
            # topbar phase
            try: self.phase_indicator.configure(text=f"Fase: {self._phase_name(cur)}")
            except: pass
        except: pass

    def _phase_name(self,c): return {"PS":"Pré-Solo","AP":"Aperfeiçoamento","NV":"Navegação","NOT":"Noturno"}.get(c,c)
    def _show_maneuver_details(self,m): pass

def main():
    app = ProPilotApp()
    app.mainloop()

if __name__ == "__main__":
    main()
