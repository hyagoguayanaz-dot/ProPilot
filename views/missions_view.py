"""
Missions View - funcional com CTkScrollableFrame (sem Canvas bugado)
"""
import customtkinter as ctk
import sys, os, json
from typing import Callable, Dict

def resource_path(rel):
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

LEVEL_LABELS = {"E":"Elementar","A":"Aprendizagem","C":"Completar","M":"Medio","X":"Extra","a":"a - aux","c":"c - aux"}
LEVEL_COLORS = {"E":"#95a5a6","A":"#3498db","C":"#2ecc71","M":"#f39c12","X":"#e74c3c","a":"#3498db","c":"#2ecc71"}

class MissionsView(ctk.CTkFrame):
    def __init__(self, parent, on_back: Callable=None, theme_manager=None):
        super().__init__(parent)
        self.on_back = on_back
        self.theme_manager = theme_manager
        from database import get_database
        self.db = get_database()
        self.missions_data = {}
        self._selected_id = None
        # load data once
        try:
            p = resource_path(os.path.join("data","missions.json"))
            if not os.path.exists(p):
                p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data","missions.json")
            with open(p, encoding="utf-8") as f:
                self.missions_data = json.load(f)
        except Exception as e:
            print("missions load err", e)
            self.missions_data = {"missions":{},"requirements":{},"info":{}}
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        # header
        h = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        h.grid(row=0, column=0, sticky="ew", padx=8, pady=(8,4))
        h.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(h, text="Quadro de Missoes & Progresso", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0,column=0, sticky="w", padx=6)
        if self.on_back:
            ctk.CTkButton(h, text="← Voltar", width=90, height=28, command=self.on_back).grid(row=0,column=1, sticky="e")
        # search
        s = ctk.CTkFrame(self); s.grid(row=1,column=0, sticky="ew", padx=8, pady=4); s.grid_columnconfigure(0, weight=1)
        self.search = ctk.CTkEntry(s, placeholder_text="Buscar missao... ex: PS-3, navegacao, pouso")
        self.search.pack(fill="x", padx=8, pady=8)
        self.search.bind("<KeyRelease>", lambda e: self._refresh())

        # split: left list | right detail
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2,column=0, sticky="nsew", padx=8, pady=(4,8))
        body.grid_columnconfigure(0, weight=1, uniform="col")
        body.grid_columnconfigure(1, weight=1, uniform="col")
        body.grid_rowconfigure(0, weight=1)

        # LEFT - scrollable mission list
        self.left_scroll = ctk.CTkScrollableFrame(body, label_text="Missoes", label_text_color=("#1f538d","#4cc2ff"))
        self.left_scroll.grid(row=0,column=0, sticky="nsew", padx=(0,4))

        # RIGHT - scrollable detail
        self.right_scroll = ctk.CTkScrollableFrame(body, label_text="Detalhes — selecione uma missao")
        self.right_scroll.grid(row=0,column=1, sticky="nsew", padx=(4,0))
        self._refresh()

    def _refresh(self):
        term = (self.search.get() or "").strip().lower()
        for w in self.left_scroll.winfo_children():
            w.destroy()
        # reset right only if first load
        if self._selected_id is None:
            for w in self.right_scroll.winfo_children():
                w.destroy()
            ctk.CTkLabel(self.right_scroll, text="Clique em uma missao a esquerda\npara ver exercicios e niveis exigidos.", justify="center", text_color=("gray50","gray60")).pack(pady=30)

        order = ["PS","AP","NV","NOT"]
        colors = {"PS":"#3498db","AP":"#2ecc71","NV":"#9b59b6","NOT":"#e74c3c"}
        found = 0
        for ph in order:
            pdata = self.missions_data.get("missions",{}).get(ph)
            if not pdata: continue
            missions = pdata.get("missions",[])
            # filter
            if term:
                missions = [m for m in missions if term in m.get("name","").lower() or term in m.get("description","").lower() or term in " ".join(m.get("exercises",[])).lower()]
                if not missions: continue
            ctk.CTkLabel(self.left_scroll, text=f"{ph} — {pdata.get('name','')}", font=ctk.CTkFont(weight="bold", size=13), text_color=colors.get(ph,"#fff")).pack(anchor="w", padx=8, pady=(12,4))
            for m in missions:
                found += 1
                self._card(m, ph)
        if found==0:
            ctk.CTkLabel(self.left_scroll, text="Nenhuma missao encontrada.", text_color=("gray50","gray60")).pack(pady=20)

    def _card(self, m: Dict, phase: str):
        done = m["id"] in self.db.load_progress().get("completed_missions",[])
        is_sel = self._selected_id == m["id"]
        card = ctk.CTkFrame(self.left_scroll, corner_radius=10, border_width=2 if is_sel else 1, border_color="#4cc2ff" if is_sel else ("gray75","gray30"))
        card.pack(fill="x", padx=6, pady=5)
        # bind whole card
        def select(_e=None, mid=m["id"]):
            self._selected_id = mid
            self._show_detail(m)
            self._refresh()  # redraw to highlight
            # keep detail after refresh - already shown
            self._show_detail(m)
        card.bind("<Button-1>", select)
        top = ctk.CTkFrame(card, fg_color="transparent"); top.pack(fill="x", padx=10, pady=(8,2))
        top.grid_columnconfigure(1, weight=1)
        var = ctk.BooleanVar(value=done)
        def toggle():
            self.db.toggle_mission_completion(m["id"], var.get())
            self.db.update_study_progress(phase)
        cb = ctk.CTkCheckBox(top, text="", variable=var, command=toggle, width=22); cb.grid(row=0,column=0, sticky="w")
        # also bind checkbox label
        lbl = ctk.CTkLabel(top, text=m["name"], font=ctk.CTkFont(weight="bold", size=13), anchor="w")
        lbl.grid(row=0,column=1, sticky="w", padx=6)
        lbl.bind("<Button-1>", select)
        ctk.CTkLabel(top, text=m.get("duration",""), font=ctk.CTkFont(size=11), text_color=("gray50","gray60")).grid(row=0,column=2, sticky="e")
        desc = ctk.CTkLabel(card, text=m.get("description",""), wraplength=300, justify="left", font=ctk.CTkFont(size=11), text_color=("gray40","gray65"), anchor="w")
        desc.pack(anchor="w", padx=12, pady=(0,2))
        desc.bind("<Button-1>", select)
        meta = ctk.CTkFrame(card, fg_color="transparent"); meta.pack(fill="x", padx=10, pady=(0,8))
        ctk.CTkLabel(meta, text=f"{len(m.get('exercises',[]))} exercicios", font=ctk.CTkFont(size=11), text_color=("gray50","gray60")).pack(side="left")
        lvl = m.get("required_level") or m.get("level","")
        ctk.CTkLabel(meta, text=f"Nivel: {lvl}", font=ctk.CTkFont(size=11, weight="bold"), text_color=LEVEL_COLORS.get(lvl.strip().split()[0], "#f39c12")).pack(side="right")
        # make all children clickable
        for child in [card, top, lbl, desc, meta]:
            try: child.bind("<Button-1>", select)
            except: pass

    def _show_detail(self, m: Dict):
        for w in self.right_scroll.winfo_children():
            w.destroy()
        # dynamic label
        try: self.right_scroll.configure(label_text=f"{m['id']} — {m['name']}")
        except: pass
        # info badges
        info = ctk.CTkFrame(self.right_scroll); info.pack(fill="x", padx=6, pady=6)
        info.grid_columnconfigure((0,1), weight=1)
        ctk.CTkLabel(info, text=f"Duracao: {m.get('duration','--')}", font=ctk.CTkFont(weight="bold")).grid(row=0,column=0, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(info, text=f"Tipo: {m.get('type','DC')}  •  Nivel base: {m.get('required_level', m.get('level',''))}", font=ctk.CTkFont(size=12)).grid(row=0,column=1, padx=6, pady=6, sticky="w")
        # objetivo
        box = ctk.CTkFrame(self.right_scroll); box.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(box, text="Objetivo da missao", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,2))
        ctk.CTkLabel(box, text=m.get("description",""), wraplength=420, justify="left", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(0,10))
        # exercicios com nivel
        ex_box = ctk.CTkFrame(self.right_scroll); ex_box.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(ex_box, text=f"Exercicios necessarios — o que precisa cumprir ({len(m.get('exercises',[]))})", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,2))
        ctk.CTkLabel(ex_box, text="Toque no checkbox da lista para marcar a missao como concluida. Cada exercicio abaixo mostra o nivel exigido pela banca.", font=ctk.CTkFont(size=11), text_color=("gray50","gray60"), wraplength=420, justify="left").pack(anchor="w", padx=10, pady=(0,6))
        # requirements lookup
        req = self.missions_data.get("requirements",{}).get(m["id"].lower(), {})
        for i, ex in enumerate(m.get("exercises",[]), 1):
            lvl = req.get(ex, m.get("required_level","M"))
            row = ctk.CTkFrame(ex_box, fg_color=("gray92","gray18")); row.pack(fill="x", padx=8, pady=2)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row, text=f"{i:02d}. {ex}", font=ctk.CTkFont(size=12), anchor="w", justify="left", wraplength=300).grid(row=0,column=0, sticky="w", padx=8, pady=6)
            badge = ctk.CTkLabel(row, text=lvl, width=36, height=22, corner_radius=8, fg_color=LEVEL_COLORS.get(lvl, "#444"), text_color="white", font=ctk.CTkFont(weight="bold", size=11))
            badge.grid(row=0,column=1, padx=8)
            # tooltip via label
            full = LEVEL_LABELS.get(lvl, lvl)
            ctk.CTkLabel(row, text=full, font=ctk.CTkFont(size=10), text_color=("gray45","gray60")).grid(row=0,column=2, padx=(0,8))
        # criterios
        crit = ctk.CTkFrame(self.right_scroll, fg_color=("#fff7cc","#2a2410"), border_width=1, border_color="#f1c40f"); crit.pack(fill="x", padx=6, pady=8)
        ctk.CTkLabel(crit, text="Criterios de aprovacao", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,2))
        ctk.CTkLabel(crit, text="• Aprovado se obtiver Grau 3 (Satisfatorio) ou superior em TODOS os exercicios\n• Grau 1 (Perigoso) ou 2 (Deficiente) em qualquer exercicio = reprovado\n• Grau 4 = Bom  •  Grau 5 = Excelente\n• Revisao obrigatoria em caso de falha antes de progredir de fase.", justify="left", wraplength=420, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(0,10))
