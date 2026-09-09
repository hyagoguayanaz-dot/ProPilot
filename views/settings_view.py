"""
Settings View - Configurações (layout da versão anterior + paleta Spotify)
Aparência: tema claro/escuro via radio + 8 cores de destaque apenas aqui
"""
import customtkinter as ctk
from typing import Callable

ACCENTS = {
    "spotify": {"name":"Spotify Green","color":"#1DB954","hover":"#1ED760"},
    "ocean":   {"name":"Ocean Blue","color":"#3B82F6","hover":"#60A5FA"},
    "violet":  {"name":"Violet Haze","color":"#8B5CF6","hover":"#A78BFA"},
    "pink":    {"name":"Hot Pink","color":"#EC4899","hover":"#F472B6"},
    "sunset":  {"name":"Sunset Orange","color":"#F59E0B","hover":"#FBBF24"},
    "crimson": {"name":"Crimson Red","color":"#EF4444","hover":"#F87171"},
    "teal":    {"name":"Teal Wave","color":"#06B6D4","hover":"#22D3EE"},
    "lime":    {"name":"Lime Pulse","color":"#84CC16","hover":"#A3E635"},
}

def _cols(theme):
    if theme=="dark":
        return {"card":"#181818","hover":"#282828","line":"#2A2A2A","text":"#FFFFFF","sub":"#B3B3B3","bg":"#121212"}
    else:
        return {"card":"#FFFFFF","hover":"#F0F0F0","line":"#E0E0E0","text":"#121212","sub":"#6A6A6A","bg":"#F5F5F5"}

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, on_back: Callable = None, theme_manager=None):
        super().__init__(parent, fg_color="transparent")
        self.on_back = on_back
        self.theme_manager = theme_manager
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        cols = _cols(self.theme_manager.current_theme if self.theme_manager else "dark")
        acc = self.theme_manager.get_accent() if self.theme_manager else "#1DB954"
        hover = ACCENTS.get(self.theme_manager.current_accent, ACCENTS["spotify"])["hover"] if self.theme_manager else "#1ED760"

        # header - igual versão anterior
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0,column=0, sticky="ew", padx=10, pady=10); hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Configurações", font=ctk.CTkFont(size=20, weight="bold"), text_color=cols["text"]).grid(row=0,column=0, sticky="w", padx=10)
        ctk.CTkLabel(hdr, text="Personalize tema, cores e perfil do piloto", font=ctk.CTkFont(size=12), text_color=cols["sub"]).grid(row=1,column=0, sticky="w", padx=10)
        if self.on_back:
            ctk.CTkButton(hdr, text="← Voltar", width=90, height=28, corner_radius=20, fg_color=cols["card"], hover_color=cols["hover"], text_color=cols["text"], command=self.on_back).grid(row=0,column=1,rowspan=2, sticky="e", padx=6)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1,column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        # 1) Tema - radio igual versão anterior (Escuro/Claro)
        sec = ctk.CTkFrame(scroll, fg_color=cols["card"], corner_radius=12)
        sec.grid(row=0,column=0, sticky="ew", padx=10, pady=8); sec.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sec, text="Tema de exibição", font=ctk.CTkFont(size=14, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(14,2))
        ctk.CTkLabel(sec, text="Escolha claro ou escuro", font=ctk.CTkFont(size=12), text_color=cols["sub"]).pack(anchor="w", padx=16, pady=(0,8))
        self.theme_var = ctk.StringVar(value=self.theme_manager.current_theme if self.theme_manager else "dark")
        # radio buttons com accent
        for txt,val in [("Escuro (recomendado)","dark"),("Claro","light")]:
            rb = ctk.CTkRadioButton(sec, text=txt, variable=self.theme_var, value=val, command=self._toggle_theme, fg_color=acc, hover_color=hover, text_color=cols["text"])
            rb.pack(anchor="w", padx=22, pady=4)
        ctk.CTkLabel(sec, text="", height=4).pack()

        # 2) Cor de destaque - 8 opções, apenas aqui (pedido do usuário)
        pal_sec = ctk.CTkFrame(scroll, fg_color=cols["card"], corner_radius=12)
        pal_sec.grid(row=1,column=0, sticky="ew", padx=10, pady=8); pal_sec.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pal_sec, text="Cor de destaque", font=ctk.CTkFont(size=14, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(14,2))
        ctk.CTkLabel(pal_sec, text="Escolha uma cor — aplicada em botões, barras e destaques (estilo Spotify)", font=ctk.CTkFont(size=11), text_color=cols["sub"], wraplength=500, justify="left").pack(anchor="w", padx=16, pady=(0,8))
        grid = ctk.CTkFrame(pal_sec, fg_color="transparent")
        grid.pack(fill="x", padx=12, pady=6)
        grid.grid_columnconfigure((0,1,2,3), weight=1)
        self._accent_cards = {}
        for idx, (aid, info) in enumerate(ACCENTS.items()):
            is_sel = self.theme_manager and self.theme_manager.current_accent==aid
            card = ctk.CTkFrame(grid, fg_color=acc if is_sel else cols["hover"], corner_radius=10, border_width=2 if is_sel else 0, border_color=acc)
            card.grid(row=idx//4, column=idx%4, padx=6, pady=6, sticky="ew")
            # bolinha
            dot = ctk.CTkButton(card, text="", width=38, height=38, corner_radius=19, fg_color=info["color"], hover_color=info["hover"], command=lambda a=aid: self._set_accent(a))
            dot.pack(pady=(10,6))
            ctk.CTkLabel(card, text=info["name"], font=ctk.CTkFont(size=10, weight="bold"), text_color="white" if is_sel else cols["text"]).pack()
            ctk.CTkLabel(card, text=info["color"], font=ctk.CTkFont(size=9), text_color="white" if is_sel else cols["sub"]).pack(pady=(0,8))
            card.bind("<Button-1>", lambda e,a=aid: self._set_accent(a))
            for ch in card.winfo_children(): ch.bind("<Button-1>", lambda e,a=aid: self._set_accent(a))
            self._accent_cards[aid] = card
        # preview
        prev = ctk.CTkFrame(pal_sec, fg_color=cols["hover"], corner_radius=8)
        prev.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(prev, text="Prévia", font=ctk.CTkFont(size=11, weight="bold"), text_color=cols["sub"]).pack(anchor="w", padx=12, pady=(8,2))
        self._prev_btn = ctk.CTkButton(prev, text="▶  Botão com destaque", fg_color=acc, hover_color=hover, text_color="white", corner_radius=20, width=160)
        self._prev_btn.pack(anchor="w", padx=12, pady=4)
        self._prev_bar = ctk.CTkProgressBar(prev, height=6, progress_color=acc, fg_color=cols["line"]); self._prev_bar.set(0.65); self._prev_bar.pack(fill="x", padx=12, pady=(0,10))

        # 3) Perfil editável - igual versão anterior
        prof = ctk.CTkFrame(scroll, fg_color=cols["card"], corner_radius=12)
        prof.grid(row=2,column=0, sticky="ew", padx=10, pady=8); prof.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(prof, text="Perfil do piloto — personalizável", font=ctk.CTkFont(size=14, weight="bold"), text_color=cols["text"]).grid(row=0,column=0,columnspan=2, sticky="w", padx=16, pady=(14,6))
        ctk.CTkLabel(prof, text="Edite e clique em Salvar. Os dados aparecem no dashboard e cabeçalho.", font=ctk.CTkFont(size=11), text_color=cols["sub"], wraplength=500, justify="left").grid(row=1,column=0,columnspan=2, sticky="w", padx=16, pady=(0,10))
        def add_row(r, label, ph):
            ctk.CTkLabel(prof, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color=cols["text"]).grid(row=r,column=0, sticky="w", padx=16, pady=6)
            e = ctk.CTkEntry(prof, placeholder_text=ph, fg_color=cols["hover"], border_color=cols["line"], text_color=cols["text"])
            e.grid(row=r,column=1, sticky="ew", padx=16, pady=6)
            return e
        self.entry_name = add_row(2, "Nome do piloto:", "Ex: Cmte. Guayanaz")
        self.entry_school = add_row(3, "Escola / Aeroclube:", "Ex: Aeroclube de Pirassununga")
        ctk.CTkLabel(prof, text="Horas totais (h):", font=ctk.CTkFont(size=12), text_color=cols["text"]).grid(row=4,column=0, sticky="w", padx=16, pady=6)
        self.entry_hours = ctk.CTkEntry(prof, placeholder_text="0", width=120, fg_color=cols["hover"], border_color=cols["line"], text_color=cols["text"])
        self.entry_hours.grid(row=4,column=1, sticky="w", padx=16, pady=6)
        ctk.CTkLabel(prof, text="Horas solo (h):", font=ctk.CTkFont(size=12), text_color=cols["text"]).grid(row=5,column=0, sticky="w", padx=16, pady=6)
        self.entry_solo = ctk.CTkEntry(prof, placeholder_text="0", width=120, fg_color=cols["hover"], border_color=cols["line"], text_color=cols["text"])
        self.entry_solo.grid(row=5,column=1, sticky="w", padx=16, pady=6)
        ctk.CTkLabel(prof, text="Fase atual:", font=ctk.CTkFont(size=12), text_color=cols["text"]).grid(row=6,column=0, sticky="w", padx=16, pady=6)
        self.combo_phase = ctk.CTkOptionMenu(prof, values=["PS - Pré-Solo","AP - Aperfeiçoamento","NV - Navegação","NOT - Noturno"], width=200, fg_color=cols["hover"], button_color=acc, button_hover_color=hover, text_color=cols["text"])
        self.combo_phase.grid(row=6,column=1, sticky="w", padx=16, pady=6)
        ctk.CTkLabel(prof, text="Status:", font=ctk.CTkFont(size=12), text_color=cols["text"]).grid(row=7,column=0, sticky="w", padx=16, pady=6)
        self.combo_status = ctk.CTkOptionMenu(prof, values=["student - Aluno","solo - Solo","check - Check PX","licensed - Licenciado"], width=200, fg_color=cols["hover"], button_color=acc, button_hover_color=hover, text_color=cols["text"])
        self.combo_status.grid(row=7,column=1, sticky="w", padx=16, pady=6)
        btn_row = ctk.CTkFrame(prof, fg_color="transparent"); btn_row.grid(row=8,column=0,columnspan=2, sticky="ew", padx=16, pady=14); btn_row.grid_columnconfigure((0,1), weight=1)
        self._save_btn = ctk.CTkButton(btn_row, text="Salvar perfil", fg_color=acc, hover_color=hover, text_color="white", corner_radius=20, height=36, command=self._save_profile)
        self._save_btn.grid(row=0,column=0, padx=6, sticky="ew")
        ctk.CTkButton(btn_row, text="Restaurar padrão", fg_color=cols["hover"], hover_color=cols["line"], text_color=cols["text"], corner_radius=20, height=36, command=self._reset_profile).grid(row=0,column=1, padx=6, sticky="ew")
        self.save_msg = ctk.CTkLabel(prof, text="", font=ctk.CTkFont(size=11), text_color=acc)
        self.save_msg.grid(row=9,column=0,columnspan=2, pady=(0,10))

        # 4) Progresso por fase - igual versão anterior
        prog = ctk.CTkFrame(scroll, fg_color=cols["card"], corner_radius=12)
        prog.grid(row=3,column=0, sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(prog, text="Progresso por fase", font=ctk.CTkFont(size=14, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(14,6))
        self.bars = {}
        for code,label in [("PS","Pré-Solo (20h)"),("AP","Aperfeiçoamento (10h)"),("NV","Navegação (10h)"),("NOT","Noturno (3h)")]:
            row = ctk.CTkFrame(prog, fg_color="transparent"); row.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(row, text=label, width=160, anchor="w", font=ctk.CTkFont(size=12), text_color=cols["text"]).pack(side="left")
            bar = ctk.CTkProgressBar(row, height=8, progress_color=acc, fg_color=cols["line"]); bar.set(0); bar.pack(side="left", fill="x", expand=True, padx=8)
            ctk.CTkLabel(row, text="0/0", width=50, font=ctk.CTkFont(size=11), text_color=cols["sub"]).pack(side="left")
            self.bars[code] = bar
            bar._label_text = row.winfo_children()[-1]

        # 5) Sobre
        about = ctk.CTkFrame(scroll, fg_color=cols["card"], corner_radius=12); about.grid(row=4,column=0, sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(about, text="Sobre", font=ctk.CTkFont(size=14, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(14,4))
        ctk.CTkLabel(about, text="Pro Pilot v2.0 — Spotify Edition\nCurso de Piloto Privado de Avião (PPA) • Aeroclube de Pirassununga\n© Guayanaz Systems — Todos os direitos reservados.", justify="left", text_color=cols["sub"], font=ctk.CTkFont(size=12)).pack(anchor="w", padx=16, pady=(0,6))
        ctk.CTkLabel(about, text="© 2026 Guayanaz Systems", font=ctk.CTkFont(size=11, slant="italic"), text_color=cols["sub"]).pack(anchor="w", padx=16, pady=(0,14))

        self._load()

    def _toggle_theme(self):
        if self.theme_manager:
            new_theme = self.theme_var.get()
            self.theme_manager.set_theme(new_theme)
            # Reconstrói a view inteira para aplicar novas cores sem inversão
            # salva estado temporário dos campos
            try:
                cur_name = self.entry_name.get()
                cur_school = self.entry_school.get()
                cur_hours = self.entry_hours.get()
                cur_solo = self.entry_solo.get()
                cur_phase = self.combo_phase.get()
                cur_status = self.combo_status.get()
            except: cur_name = cur_school = cur_hours = cur_solo = cur_phase = cur_status = None
            for w in self.winfo_children():
                w.destroy()
            self._build()
            # restaura campos (evita perder digitação)
            try:
                if cur_name is not None:
                    self.entry_name.delete(0,"end"); self.entry_name.insert(0, cur_name)
                    self.entry_school.delete(0,"end"); self.entry_school.insert(0, cur_school)
                    self.entry_hours.delete(0,"end"); self.entry_hours.insert(0, cur_hours)
                    self.entry_solo.delete(0,"end"); self.entry_solo.insert(0, cur_solo)
                    self.combo_phase.set(cur_phase)
                    self.combo_status.set(cur_status)
                    self.theme_var.set(new_theme)
            except: pass
            # notifica app principal para atualizar sidebar/content
            try:
                app = self.winfo_toplevel()
                if hasattr(app, "theme_manager"):
                    cols = app.theme_manager.get_colors()
                    acc = app.theme_manager.get_accent()
                    app.configure(fg_color=cols["bg"])
                    if hasattr(app, "sidebar"): app.sidebar.configure(fg_color=cols["sidebar"])
                    if hasattr(app, "content_wrap"): app.content_wrap.configure(fg_color=cols["content"])
                    if hasattr(app, "topbar"): app.topbar.configure(fg_color=cols["content"])
                    if hasattr(app, "side_card"): app.side_card.configure(fg_color=cols["card"])
                    if hasattr(app, "_highlight_nav") and hasattr(app, "_active_nav"):
                        app._highlight_nav(app._active_nav)
                    if hasattr(app, "_update_phase"): app._update_phase()
                    # atualiza textos
                    if hasattr(app, "top_title"): app.top_title.configure(text_color=cols["text"])
                    if hasattr(app, "top_sub"): app.top_sub.configure(text_color=cols["subtext"])
                    if hasattr(app, "theme_btn"):
                        is_dark = app.theme_manager.current_theme=="dark"
                        app.theme_btn.configure(text="🌙" if is_dark else "☀️", fg_color=cols["card"], hover_color=cols["hover"])
            except: pass

    def _set_accent(self, aid):
        if self.theme_manager:
            self.theme_manager.set_accent(aid)
            acc = self.theme_manager.get_accent(); hover = ACCENTS[aid]["hover"]
            cols = _cols(self.theme_manager.current_theme)
            for k, card in self._accent_cards.items():
                is_sel = k==aid
                card.configure(fg_color=acc if is_sel else cols["hover"], border_width=2 if is_sel else 0, border_color=acc)
                for ch in card.winfo_children():
                    if isinstance(ch, ctk.CTkLabel):
                        ch.configure(text_color="white" if is_sel else (cols["text"] if "Spotify" in ch.cget("text") or "Ocean" in ch.cget("text") or "Violet" in ch.cget("text") or "Pink" in ch.cget("text") or "Sunset" in ch.cget("text") or "Crimson" in ch.cget("text") or "Teal" in ch.cget("text") or "Lime" in ch.cget("text") else cols["sub"]))
            self._prev_btn.configure(fg_color=acc, hover_color=hover)
            self._prev_bar.configure(progress_color=acc)
            self._save_btn.configure(fg_color=acc, hover_color=hover)
            try:
                self.combo_phase.configure(button_color=acc, button_hover_color=hover)
                self.combo_status.configure(button_color=acc, button_hover_color=hover)
            except: pass
            # notifica app para atualizar barras do dashboard/sidebar na próxima navegação
            try:
                app = self.winfo_toplevel()
                if hasattr(app, "side_progress"):
                    app.side_progress.configure(progress_color=acc)
            except: pass

    def _load(self):
        try:
            from database import get_database
            db = get_database()
            s = db.load_settings()
            self.theme_var.set(s.get("theme","dark"))
            p = db.load_progress().get("profile",{})
            name = p.get("display_name") or s.get("display_name","Piloto-Aluno")
            self.entry_name.delete(0,"end"); self.entry_name.insert(0, name)
            school = p.get("school") or s.get("school","Aeroclube de Pirassununga")
            self.entry_school.delete(0,"end"); self.entry_school.insert(0, school)
            self.entry_hours.delete(0,"end"); self.entry_hours.insert(0, str(p.get("total_flight_hours",0)))
            self.entry_solo.delete(0,"end"); self.entry_solo.insert(0, str(p.get("solo_hours",0)))
            phase_map = {"PS":"PS - Pré-Solo","AP":"AP - Aperfeiçoamento","NV":"NV - Navegação","NOT":"NOT - Noturno"}
            self.combo_phase.set(phase_map.get(p.get("current_phase","PS"), "PS - Pré-Solo"))
            status_map = {"student":"student - Aluno","solo":"solo - Solo","check":"check - Check PX","licensed":"licensed - Licenciado"}
            self.combo_status.set(status_map.get(p.get("pilot_license_status","student"), "student - Aluno"))
            for code, bar in self.bars.items():
                prog = db.load_progress().get("study_progress",{}).get(code,{"completed":0,"total":1})
                pct = prog.get("completed",0)/max(prog.get("total",1),1)
                bar.set(min(pct,1.0))
                try: bar._label_text.configure(text=f"{prog.get('completed',0)}/{prog.get('total',1)}")
                except: pass
        except Exception as e:
            print("load settings err", e)

    def _save_profile(self):
        try:
            from database import get_database
            db = get_database()
            prog = db.load_progress(); settings = db.load_settings()
            name = self.entry_name.get().strip() or "Piloto-Aluno"
            school = self.entry_school.get().strip() or "Aeroclube de Pirassununga"
            try: hours = float(self.entry_hours.get().strip() or 0)
            except: hours = 0
            try: solo = float(self.entry_solo.get().strip() or 0)
            except: solo = 0
            phase = self.combo_phase.get().split(" - ")[0].strip()
            status = self.combo_status.get().split(" - ")[0].strip()
            prog["profile"].update({"display_name":name,"school":school,"total_flight_hours":hours,"solo_hours":solo,"current_phase":phase,"pilot_license_status":status})
            db._save_progress(prog)
            settings.update({"display_name":name,"school":school})
            db.save_settings(settings)
            acc = self.theme_manager.get_accent() if self.theme_manager else "#1DB954"
            self.save_msg.configure(text="✓ Perfil salvo!", text_color=acc)
            self.after(2500, lambda: self.save_msg.configure(text=""))
        except Exception as e:
            self.save_msg.configure(text=f"Erro: {e}", text_color="#e74c3c")

    def _reset_profile(self):
        try:
            from database import get_database
            db = get_database()
            prog = db.load_progress()
            prog["profile"] = {"total_flight_hours":0,"solo_hours":0,"current_phase":"PS","pilot_license_status":"student","display_name":"Piloto-Aluno","school":"Aeroclube de Pirassununga"}
            db._save_progress(prog)
            s = db.load_settings(); s.update({"display_name":"Piloto-Aluno","school":"Aeroclube de Pirassununga"}); db.save_settings(s)
            self._load()
            self.save_msg.configure(text="↺ Restaurado", text_color="#f39c12")
            self.after(2000, lambda: self.save_msg.configure(text=""))
        except Exception as e:
            self.save_msg.configure(text=f"Erro: {e}", text_color="#e74c3c")
