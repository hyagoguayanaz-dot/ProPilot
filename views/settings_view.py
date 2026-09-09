"""
Settings - Spotify Edition com paleta de cores
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
# helper para pegar cores atuais do tema
def _cols(theme):
    if theme=="dark":
        return {"bg":"#000000","card":"#181818","hover":"#282828","line":"#2A2A2A","text":"#FFFFFF","sub":"#B3B3B3"}
    else:
        return {"bg":"#F5F5F5","card":"#FFFFFF","hover":"#E8E8E8","line":"#E0E0E0","text":"#121212","sub":"#6A6A6A"}

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, on_back: Callable=None, theme_manager=None):
        super().__init__(parent, fg_color="transparent")
        self.on_back = on_back
        self.theme_manager = theme_manager
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        cols = _cols(self.theme_manager.current_theme if self.theme_manager else "dark")
        acc = self.theme_manager.get_accent() if self.theme_manager else "#1DB954"

        # header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0,column=0, sticky="ew", padx=4, pady=(4,8)); hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Configurações", font=ctk.CTkFont(size=22, weight="bold"), text_color=cols["text"]).grid(row=0,column=0, sticky="w")
        ctk.CTkLabel(hdr, text="Personalize sua experiência Pro Pilot", font=ctk.CTkFont(size=12), text_color=cols["sub"]).grid(row=1,column=0, sticky="w")
        if self.on_back:
            ctk.CTkButton(hdr, text="← Voltar", width=90, height=28, corner_radius=20, fg_color=cols["card"], hover_color=cols["hover"], text_color=cols["text"], command=self.on_back).grid(row=0,column=1,rowspan=2, sticky="e")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1,column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        # APARÊNCIA - tema + paleta
        sec = ctk.CTkFrame(scroll, fg_color=cols["card"], corner_radius=12)
        sec.grid(row=0,column=0, sticky="ew", padx=4, pady=8); sec.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sec, text="Aparência", font=ctk.CTkFont(size=16, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(14,2))
        ctk.CTkLabel(sec, text="Escolha o modo e a cor de destaque — estilo Spotify", font=ctk.CTkFont(size=12), text_color=cols["sub"]).pack(anchor="w", padx=16, pady=(0,10))

        # Tema dark/light como segmented
        self.theme_var = ctk.StringVar(value=self.theme_manager.current_theme if self.theme_manager else "dark")
        seg = ctk.CTkSegmentedButton(sec, values=["Escuro","Claro"], selected_color=acc, selected_hover_color=ACCENTS.get(self.theme_manager.current_accent, ACCENTS["spotify"])["hover"] if self.theme_manager else acc,
                                       unselected_color=cols["hover"], unselected_hover_color=cols["hover"], text_color=cols["text"],
                                       command=lambda v: self._set_theme("dark" if v=="Escuro" else "light"))
        # set initial
        seg.set("Escuro" if self.theme_var.get()=="dark" else "Claro")
        seg.pack(anchor="w", padx=16, pady=6)
        self._seg = seg

        # Paleta de cores
        ctk.CTkLabel(sec, text="Cor de destaque", font=ctk.CTkFont(size=13, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(14,4))
        ctk.CTkLabel(sec, text="Toque em uma cor para aplicar instantaneamente", font=ctk.CTkFont(size=11), text_color=cols["sub"]).pack(anchor="w", padx=16, pady=(0,6))
        pal = ctk.CTkFrame(sec, fg_color="transparent"); pal.pack(fill="x", padx=16, pady=6)
        pal.grid_columnconfigure((0,1,2,3), weight=1)
        self._accent_btns = {}
        for idx, (aid, info) in enumerate(ACCENTS.items()):
            card = ctk.CTkFrame(pal, fg_color=cols["hover"] if aid!=self.theme_manager.current_accent else acc, corner_radius=10, border_width=2, border_color=acc if aid==self.theme_manager.current_accent else "transparent")
            card.grid(row=idx//4, column=idx%4, padx=6, pady=6, sticky="ew")
            card.grid_columnconfigure(0, weight=1)
            # dot
            dot = ctk.CTkButton(card, text="", width=44, height=44, corner_radius=22, fg_color=info["color"], hover_color=info["hover"], command=lambda a=aid: self._set_accent(a))
            dot.pack(pady=(10,6))
            ctk.CTkLabel(card, text=info["name"], font=ctk.CTkFont(size=10, weight="bold"), text_color=cols["text"] if aid!=self.theme_manager.current_accent else "white").pack()
            ctk.CTkLabel(card, text=info["color"], font=ctk.CTkFont(size=9), text_color=cols["sub"] if aid!=self.theme_manager.current_accent else "white").pack(pady=(0,8))
            # click whole card
            card.bind("<Button-1>", lambda e,a=aid: self._set_accent(a))
            for ch in card.winfo_children(): ch.bind("<Button-1>", lambda e,a=aid: self._set_accent(a))
            self._accent_btns[aid] = card

        # Preview
        prev = ctk.CTkFrame(sec, fg_color=cols["hover"], corner_radius=8); prev.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(prev, text="Prévia", font=ctk.CTkFont(size=11, weight="bold"), text_color=cols["sub"]).pack(anchor="w", padx=12, pady=(8,2))
        self._preview_btn = ctk.CTkButton(prev, text="▶  Botão com destaque", fg_color=acc, hover_color=ACCENTS[self.theme_manager.current_accent]["hover"], text_color="white", corner_radius=20, width=160)
        self._preview_btn.pack(anchor="w", padx=12, pady=(0,4))
        self._preview_bar = ctk.CTkProgressBar(prev, height=6, progress_color=acc); self._preview_bar.set(0.65); self._preview_bar.pack(fill="x", padx=12, pady=(0,10))

        # Perfil editável (mantido mas com estilo Spotify)
        prof = ctk.CTkFrame(scroll, fg_color=cols["card"], corner_radius=12)
        prof.grid(row=1,column=0, sticky="ew", padx=4, pady=8); prof.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(prof, text="Perfil do piloto", font=ctk.CTkFont(size=16, weight="bold"), text_color=cols["text"]).grid(row=0,column=0,columnspan=2, sticky="w", padx=16, pady=(14,2))
        ctk.CTkLabel(prof, text="Seus dados aparecem no dashboard e são salvos automaticamente", font=ctk.CTkFont(size=11), text_color=cols["sub"]).grid(row=1,column=0,columnspan=2, sticky="w", padx=16, pady=(0,10))

        def add_row(r, label, placeholder, width=None):
            ctk.CTkLabel(prof, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color=cols["text"]).grid(row=r,column=0, sticky="w", padx=16, pady=6)
            e = ctk.CTkEntry(prof, placeholder_text=placeholder, fg_color=cols["hover"], border_color=cols["line"], text_color=cols["text"])
            e.grid(row=r,column=1, sticky="ew", padx=16, pady=6)
            if width: e.configure(width=width)
            return e

        self.entry_name = add_row(2, "Nome", "Ex: Cmte. Guayanaz")
        self.entry_school = add_row(3, "Escola / Aeroclube", "Ex: Aeroclube de Pirassununga")
        self.entry_hours = add_row(4, "Horas totais", "0")
        self.entry_solo = add_row(5, "Horas solo", "0")
        ctk.CTkLabel(prof, text="Fase atual", font=ctk.CTkFont(size=12, weight="bold"), text_color=cols["text"]).grid(row=6,column=0, sticky="w", padx=16, pady=6)
        self.combo_phase = ctk.CTkOptionMenu(prof, values=["PS - Pré-Solo","AP - Aperfeiçoamento","NV - Navegação","NOT - Noturno"], fg_color=cols["hover"], button_color=acc, button_hover_color=ACCENTS[self.theme_manager.current_accent]["hover"], text_color=cols["text"], width=200)
        self.combo_phase.grid(row=6,column=1, sticky="w", padx=16, pady=6)
        ctk.CTkLabel(prof, text="Status", font=ctk.CTkFont(size=12, weight="bold"), text_color=cols["text"]).grid(row=7,column=0, sticky="w", padx=16, pady=6)
        self.combo_status = ctk.CTkOptionMenu(prof, values=["student - Aluno","solo - Solo","check - Check PX","licensed - Licenciado"], fg_color=cols["hover"], button_color=acc, button_hover_color=ACCENTS[self.theme_manager.current_accent]["hover"], text_color=cols["text"], width=200)
        self.combo_status.grid(row=7,column=1, sticky="w", padx=16, pady=6)

        btn_row = ctk.CTkFrame(prof, fg_color="transparent"); btn_row.grid(row=8,column=0,columnspan=2, sticky="ew", padx=16, pady=14); btn_row.grid_columnconfigure((0,1), weight=1)
        self._save_btn = ctk.CTkButton(btn_row, text="Salvar perfil", fg_color=acc, hover_color=ACCENTS[self.theme_manager.current_accent]["hover"], text_color="white", corner_radius=20, height=36, command=self._save_profile)
        self._save_btn.grid(row=0,column=0, padx=6, sticky="ew")
        ctk.CTkButton(btn_row, text="Restaurar padrão", fg_color=cols["hover"], hover_color=cols["line"], text_color=cols["text"], corner_radius=20, height=36, command=self._reset_profile).grid(row=0,column=1, padx=6, sticky="ew")
        self.save_msg = ctk.CTkLabel(prof, text="", font=ctk.CTkFont(size=11), text_color=acc)
        self.save_msg.grid(row=9,column=0,columnspan=2, pady=(0,10))

        # Sobre
        about = ctk.CTkFrame(scroll, fg_color=cols["card"], corner_radius=12); about.grid(row=2,column=0, sticky="ew", padx=4, pady=8)
        ctk.CTkLabel(about, text="Sobre", font=ctk.CTkFont(size=14, weight="bold"), text_color=cols["text"]).pack(anchor="w", padx=16, pady=(14,4))
        ctk.CTkLabel(about, text="Pro Pilot v2.0 — Spotify Edition\nCurso de Piloto Privado de Avião (PPA) • Aeroclube de Pirassununga\n© Guayanaz Systems — Todos os direitos reservados • 2026", justify="left", text_color=cols["sub"], font=ctk.CTkFont(size=11)).pack(anchor="w", padx=16, pady=(0,6))
        ctk.CTkLabel(about, text="Tema inspirado no Spotify — escolha sua cor e voe no seu estilo.", font=ctk.CTkFont(size=11, slant="italic"), text_color=acc).pack(anchor="w", padx=16, pady=(0,14))

        self._load()

    def _set_theme(self, theme):
        if self.theme_manager:
            self.theme_manager.set_theme(theme)
            # atualiza paleta visual rapidamente - recarrega view
            # recria cores sem rebuild completo: apenas atualiza segmented selecionada
            acc = self.theme_manager.get_accent()
            self._seg.configure(selected_color=acc, selected_hover_color=ACCENTS[self.theme_manager.current_accent]["hover"])
            self._preview_btn.configure(fg_color=acc, hover_color=ACCENTS[self.theme_manager.current_accent]["hover"])
            self._preview_bar.configure(progress_color=acc)
            self._save_btn.configure(fg_color=acc, hover_color=ACCENTS[self.theme_manager.current_accent]["hover"])
            # avisa app para trocar topbar/sidebar
            try:
                # encontra App
                app = self.winfo_toplevel()
                if hasattr(app, "_toggle_theme"):
                    # não chama toggle (inverteria), só força refresh via navigate
                    pass
            except: pass

    def _set_accent(self, aid):
        if self.theme_manager:
            self.theme_manager.set_accent(aid)
            acc = self.theme_manager.get_accent()
            hover = ACCENTS[aid]["hover"]
            # atualiza seleção visual
            for k, card in self._accent_btns.items():
                if k==aid:
                    card.configure(fg_color=acc, border_color=acc)
                    for ch in card.winfo_children():
                        if isinstance(ch, ctk.CTkLabel):
                            ch.configure(text_color="white")
                else:
                    cols = _cols(self.theme_manager.current_theme)
                    card.configure(fg_color=cols["hover"], border_color="transparent")
                    for ch in card.winfo_children():
                        if isinstance(ch, ctk.CTkLabel):
                            # nome mantém text, color hex mantém sub
                            if "Spotify" in ch.cget("text") or "Ocean" in ch.cget("text") or "Violet" in ch.cget("text") or "Pink" in ch.cget("text") or "Sunset" in ch.cget("text") or "Crimson" in ch.cget("text") or "Teal" in ch.cget("text") or "Lime" in ch.cget("text"):
                                ch.configure(text_color=cols["text"])
                            else:
                                ch.configure(text_color=cols["sub"])
            self._preview_btn.configure(fg_color=acc, hover_color=hover)
            self._preview_bar.configure(progress_color=acc)
            self._save_btn.configure(fg_color=acc, hover_color=hover)
            self._seg.configure(selected_color=acc, selected_hover_color=hover)
            # atualiza combos
            try:
                self.combo_phase.configure(button_color=acc, button_hover_color=hover)
                self.combo_status.configure(button_color=acc, button_hover_color=hover)
            except: pass

    def _load(self):
        try:
            from database import get_database
            db = get_database()
            s = db.load_settings()
            self.theme_var = ctk.StringVar(value=s.get("theme","dark"))
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
