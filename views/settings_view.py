"""
Settings View - Configurações com perfil do piloto editável
"""
import customtkinter as ctk
from typing import Callable

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, on_back: Callable = None, theme_manager=None):
        super().__init__(parent)
        self.on_back = on_back
        self.theme_manager = theme_manager
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        # header
        hdr = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=10, pady=10); hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Configurações", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0,column=0, sticky="w", padx=10)
        if self.on_back:
            ctk.CTkButton(hdr, text="← Voltar", width=90, height=28, command=self.on_back).grid(row=0,column=1, sticky="e", padx=6)

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Tema
        sec = ctk.CTkFrame(scroll); sec.grid(row=0,column=0, sticky="ew", padx=10, pady=8); sec.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sec, text="Tema de exibição", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=14, pady=(12,2))
        ctk.CTkLabel(sec, text="Escolha claro ou escuro", text_color=("gray50","gray60"), font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14, pady=(0,8))
        self.theme_var = ctk.StringVar(value="dark")
        ctk.CTkRadioButton(sec, text="Escuro (recomendado)", variable=self.theme_var, value="dark", command=self._toggle_theme).pack(anchor="w", padx=22, pady=4)
        ctk.CTkRadioButton(sec, text="Claro", variable=self.theme_var, value="light", command=self._toggle_theme).pack(anchor="w", padx=22, pady=(0,12))

        # Perfil editável
        prof = ctk.CTkFrame(scroll); prof.grid(row=1,column=0, sticky="ew", padx=10, pady=8); prof.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(prof, text="Perfil do piloto — personalizável", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0,column=0,columnspan=2, sticky="w", padx=14, pady=(12,6))
        ctk.CTkLabel(prof, text="Edite e clique em Salvar. Os dados aparecem no cabeçalho e dashboard.", text_color=("gray50","gray60"), font=ctk.CTkFont(size=11), wraplength=500, justify="left").grid(row=1,column=0,columnspan=2, sticky="w", padx=14, pady=(0,10))

        # Nome
        ctk.CTkLabel(prof, text="Nome do piloto:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2,column=0, sticky="w", padx=14, pady=6)
        self.entry_name = ctk.CTkEntry(prof, placeholder_text="Ex: Cmte. Guayanaz")
        self.entry_name.grid(row=2,column=1, sticky="ew", padx=14, pady=6)

        # Escola / Aeroclube
        ctk.CTkLabel(prof, text="Escola / Aeroclube:", font=ctk.CTkFont(size=12)).grid(row=3,column=0, sticky="w", padx=14, pady=6)
        self.entry_school = ctk.CTkEntry(prof, placeholder_text="Ex: Aeroclube de Pirassununga")
        self.entry_school.grid(row=3,column=1, sticky="ew", padx=14, pady=6)

        # Horas totais
        ctk.CTkLabel(prof, text="Horas totais (h):", font=ctk.CTkFont(size=12)).grid(row=4,column=0, sticky="w", padx=14, pady=6)
        self.entry_hours = ctk.CTkEntry(prof, placeholder_text="0", width=120)
        self.entry_hours.grid(row=4,column=1, sticky="w", padx=14, pady=6)

        # Horas solo
        ctk.CTkLabel(prof, text="Horas solo (h):", font=ctk.CTkFont(size=12)).grid(row=5,column=0, sticky="w", padx=14, pady=6)
        self.entry_solo = ctk.CTkEntry(prof, placeholder_text="0", width=120)
        self.entry_solo.grid(row=5,column=1, sticky="w", padx=14, pady=6)

        # Fase atual
        ctk.CTkLabel(prof, text="Fase atual:", font=ctk.CTkFont(size=12)).grid(row=6,column=0, sticky="w", padx=14, pady=6)
        self.combo_phase = ctk.CTkOptionMenu(prof, values=["PS - Pré-Solo","AP - Aperfeiçoamento","NV - Navegação","NOT - Noturno"], width=200)
        self.combo_phase.grid(row=6,column=1, sticky="w", padx=14, pady=6)

        # Status licença
        ctk.CTkLabel(prof, text="Status:", font=ctk.CTkFont(size=12)).grid(row=7,column=0, sticky="w", padx=14, pady=6)
        self.combo_status = ctk.CTkOptionMenu(prof, values=["student - Aluno","solo - Solo","check - Check PX","licensed - Licenciado"], width=200)
        self.combo_status.grid(row=7,column=1, sticky="w", padx=14, pady=6)

        # Botões salvar / reset
        btn_row = ctk.CTkFrame(prof, fg_color="transparent"); btn_row.grid(row=8,column=0,columnspan=2, sticky="ew", padx=14, pady=14); btn_row.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(btn_row, text="💾 Salvar perfil", command=self._save_profile, height=36).grid(row=0,column=0, padx=6, sticky="ew")
        ctk.CTkButton(btn_row, text="↺ Restaurar padrão", fg_color=("gray70","gray25"), hover_color=("gray60","gray30"), command=self._reset_profile, height=36).grid(row=0,column=1, padx=6, sticky="ew")
        self.save_msg = ctk.CTkLabel(prof, text="", font=ctk.CTkFont(size=11), text_color="#2ecc71")
        self.save_msg.grid(row=9,column=0,columnspan=2, pady=(0,10))

        # Progresso por fase (visível)
        prog = ctk.CTkFrame(scroll); prog.grid(row=2,column=0, sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(prog, text="Progresso por fase", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=14, pady=(12,6))
        self.bars = {}
        for code,label in [("PS","Pré-Solo (20h)"),("AP","Aperfeiçoamento (10h)"),("NV","Navegação (10h)"),("NOT","Noturno (3h)")]:
            row = ctk.CTkFrame(prog, fg_color="transparent"); row.pack(fill="x", padx=14, pady=4)
            ctk.CTkLabel(row, text=label, width=160, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left")
            bar = ctk.CTkProgressBar(row, height=8); bar.set(0); bar.pack(side="left", fill="x", expand=True, padx=8)
            ctk.CTkLabel(row, text="0/0", width=50, font=ctk.CTkFont(size=11), text_color=("gray50","gray60")).pack(side="left")
            self.bars[code] = bar
            # guarda label pra atualizar texto depois
            bar._label_text = row.winfo_children()[-1]

        # Sobre
        about = ctk.CTkFrame(scroll); about.grid(row=3,column=0, sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(about, text="Sobre", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=14, pady=(12,4))
        ctk.CTkLabel(about, text="Pro Pilot v1.0 — Curso de Piloto Privado de Avião (PPA)\nBaseado no Programa de Instrução Aeroclube de Pirassununga\n© Guayanaz Systems — Todos os direitos reservados.", justify="left", text_color=("gray50","gray60"), font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14, pady=(0,6))
        ctk.CTkLabel(about, text="© 2026 Guayanaz Systems", font=ctk.CTkFont(size=11, slant="italic"), text_color=("gray50","gray60")).pack(anchor="w", padx=14, pady=(0,12))

        self._load()

    def _toggle_theme(self):
        if self.theme_manager: self.theme_manager.set_theme(self.theme_var.get())

    def _load(self):
        try:
            from database import get_database
            db = get_database()
            s = db.load_settings()
            self.theme_var.set(s.get("theme","dark"))
            p = db.load_progress().get("profile",{})
            # settings display_name vs profile display_name - usa profile se existir senão settings
            name = p.get("display_name") or s.get("display_name","Piloto-Aluno")
            self.entry_name.delete(0,"end"); self.entry_name.insert(0, name)
            school = p.get("school") or s.get("school","Aeroclube de Pirassununga")
            self.entry_school.delete(0,"end"); self.entry_school.insert(0, school)
            self.entry_hours.delete(0,"end"); self.entry_hours.insert(0, str(p.get("total_flight_hours",0)))
            self.entry_solo.delete(0,"end"); self.entry_solo.insert(0, str(p.get("solo_hours",0)))
            # phase/status
            phase_map = {"PS":"PS - Pré-Solo","AP":"AP - Aperfeiçoamento","NV":"NV - Navegação","NOT":"NOT - Noturno"}
            self.combo_phase.set(phase_map.get(p.get("current_phase","PS"), "PS - Pré-Solo"))
            status_map = {"student":"student - Aluno","solo":"solo - Solo","check":"check - Check PX","licensed":"licensed - Licenciado"}
            self.combo_status.set(status_map.get(p.get("pilot_license_status","student"), "student - Aluno"))
            # barras
            for code, bar in self.bars.items():
                prog = db.load_progress().get("study_progress",{}).get(code,{"completed":0,"total":1})
                pct = prog.get("completed",0)/max(prog.get("total",1),1)
                bar.set(min(pct,1.0))
                # atualiza texto
                try:
                    bar._label_text.configure(text=f"{prog.get('completed',0)}/{prog.get('total',1)}")
                except: pass
        except Exception as e:
            print("load settings err", e)

    def _save_profile(self):
        try:
            from database import get_database
            db = get_database()
            prog = db.load_progress()
            settings = db.load_settings()
            name = self.entry_name.get().strip() or "Piloto-Aluno"
            school = self.entry_school.get().strip() or "Aeroclube de Pirassununga"
            try: hours = float(self.entry_hours.get().strip() or 0)
            except: hours = 0
            try: solo = float(self.entry_solo.get().strip() or 0)
            except: solo = 0
            phase = self.combo_phase.get().split(" - ")[0].strip()
            status = self.combo_status.get().split(" - ")[0].strip()
            # salva em profile (principal) e espelha em settings pra compatibilidade
            prog["profile"]["display_name"] = name
            prog["profile"]["school"] = school
            prog["profile"]["total_flight_hours"] = hours
            prog["profile"]["solo_hours"] = solo
            prog["profile"]["current_phase"] = phase
            prog["profile"]["pilot_license_status"] = status
            db._save_progress(prog)
            settings["display_name"] = name
            settings["school"] = school
            db.save_settings(settings)
            self.save_msg.configure(text="✓ Perfil salvo com sucesso!", text_color="#2ecc71")
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
            settings = db.load_settings()
            settings["display_name"] = "Piloto-Aluno"; settings["school"]="Aeroclube de Pirassununga"
            db.save_settings(settings)
            self._load()
            self.save_msg.configure(text="↺ Perfil restaurado", text_color="#f39c12")
            self.after(2000, lambda: self.save_msg.configure(text=""))
        except Exception as e:
            self.save_msg.configure(text=f"Erro: {e}", text_color="#e74c3c")
