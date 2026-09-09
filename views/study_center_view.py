"""
Central de Estudos - funcional com CTkScrollableFrame + resource_path
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

class StudyCenterView(ctk.CTkFrame):
    def __init__(self, parent, on_maneuver_select: Callable=None, on_back: Callable=None, theme_manager=None):
        super().__init__(parent)
        self.on_maneuver_select = on_maneuver_select
        self.on_back = on_back
        self.theme_manager = theme_manager
        self.data = {}
        self._load()
        self._selected = None
        self._cat = "all"
        self._build()
        self._refresh()

    def _load(self):
        try:
            p = resource_path(os.path.join("data","missions.json"))
            if not os.path.exists(p):
                p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data","missions.json")
            with open(p, encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception as e:
            print("study load err", e)
            self.data = {"maneuvers":{"basic":[],"navigation":[]},"phases":{},"info":{}}

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        # header
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.grid(row=0,column=0, sticky="ew", padx=8, pady=(8,4)); h.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(h, text="Central de Estudos", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0,column=0, sticky="w", padx=6)
        if self.on_back:
            ctk.CTkButton(h, text="← Voltar", width=90, height=28, command=self.on_back).grid(row=0,column=1, sticky="e")
        # search + filter
        filt = ctk.CTkFrame(self); filt.grid(row=1,column=0, sticky="ew", padx=8, pady=4); filt.grid_columnconfigure(0, weight=1)
        self._search_job = None
        self.search = ctk.CTkEntry(filt, placeholder_text="Buscar manobra, categoria ou termo... ex: estol, pouso, navegacao")
        self.search.grid(row=0,column=0, sticky="ew", padx=8, pady=8)
        self.search.bind("<KeyRelease>", self._on_search_debounced)
        cats = ctk.CTkFrame(filt, fg_color="transparent"); cats.grid(row=0,column=1, padx=6)
        for c in ["Todos","Basico","Navegacao"]:
            ctk.CTkButton(cats, text=c, width=76, height=28, command=lambda cc=c: self._set_cat(cc)).pack(side="left", padx=2)
        # body split
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2,column=0, sticky="nsew", padx=8, pady=(4,8))
        body.grid_columnconfigure(0, weight=1, uniform="col")
        body.grid_columnconfigure(1, weight=1, uniform="col")
        body.grid_rowconfigure(0, weight=1)
        self.left = ctk.CTkScrollableFrame(body, label_text="Manobras")
        self.left.grid(row=0,column=0, sticky="nsew", padx=(0,4))
        self.right = ctk.CTkScrollableFrame(body, label_text="Detalhes — selecione uma manobra")
        self.right.grid(row=0,column=1, sticky="nsew", padx=(4,0))

    def _set_cat(self, c):
        self._cat = "all" if c=="Todos" else c.lower()
        # normalize navegacao without accent
        if self._cat=="navegacao": self._cat="navigation"
        if self._cat=="basico": self._cat="basic"
        self._refresh()

    def _on_search_debounced(self, event=None):
        if hasattr(self, '_search_job') and self._search_job:
            try: self.after_cancel(self._search_job)
            except: pass
        target = getattr(self, '_refresh', None) or getattr(self, '_refresh_list', None)
        if target:
            self._search_job = self.after(180, target)

    def _refresh(self):
        term = (self.search.get() or "").strip().lower()
        for w in self.left.winfo_children(): w.destroy()
        mans = []
        if self._cat in ("all","basic"): mans.extend(self.data.get("maneuvers",{}).get("basic",[]))
        if self._cat in ("all","navigation"): mans.extend(self.data.get("maneuvers",{}).get("navigation",[]))
        if term:
            mans = [m for m in mans if term in m.get("name","").lower() or term in m.get("description","").lower() or term in " ".join(m.get("steps",[])).lower()]
        if not mans:
            ctk.CTkLabel(self.left, text="Nenhuma manobra encontrada.").pack(pady=20)
            return
        for m in mans:
            self._card(m)
        if self._selected is None and mans:
            # auto-select first to show content immediately (fixes "nada aparece")
            self._show_detail(mans[0])

    def _card(self, m: Dict):
        is_sel = self._selected and self._selected.get("id")==m.get("id")
        card = ctk.CTkFrame(self.left, corner_radius=10, border_width=2 if is_sel else 1, border_color="#4cc2ff" if is_sel else ("gray75","gray30"))
        card.pack(fill="x", padx=6, pady=5)
        def sel(_e=None, mm=m): 
            self._selected = mm
            self._show_detail(mm)
            self._refresh()
            self._show_detail(mm)
        card.bind("<Button-1>", sel)
        ctk.CTkLabel(card, text=m.get("name",""), font=ctk.CTkFont(weight="bold", size=13), anchor="w", wraplength=300, justify="left").pack(anchor="w", padx=10, pady=(8,2))
        # bind label too
        for child in card.winfo_children(): 
            try: child.bind("<Button-1>", sel)
            except: pass
        row = ctk.CTkFrame(card, fg_color="transparent"); row.pack(fill="x", padx=10, pady=(0,8))
        ctk.CTkLabel(row, text=m.get("category",""), font=ctk.CTkFont(size=11), text_color=("gray50","gray60")).pack(side="left")
        ctk.CTkLabel(row, text=m.get("phase",""), font=ctk.CTkFont(size=11), text_color=("#1f538d","#4cc2ff")).pack(side="right")
        # also bind row
        row.bind("<Button-1>", sel)
        desc = ctk.CTkLabel(card, text=(m.get("description","")[:110]+"...") if len(m.get("description",""))>110 else m.get("description",""), wraplength=300, justify="left", font=ctk.CTkFont(size=11), text_color=("gray45","gray65"), anchor="w")
        desc.pack(anchor="w", padx=10, pady=(0,8))
        desc.bind("<Button-1>", sel)

    def _show_detail(self, m: Dict):
        self._selected = m
        for w in self.right.winfo_children(): w.destroy()
        try: self.right.configure(label_text=m.get("name","Detalhes"))
        except: pass
        # header badges
        hdr = ctk.CTkFrame(self.right); hdr.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(hdr, text=m.get("category",""), fg_color=("#e8f4ff","#1f2a3a"), corner_radius=6, padx=8, pady=4, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=6, pady=6)
        ctk.CTkLabel(hdr, text=m.get("phase",""), font=ctk.CTkFont(size=11, weight="bold"), text_color=("#1f538d","#4cc2ff")).pack(side="left", padx=6)
        ctk.CTkLabel(hdr, text=m.get("id",""), font=ctk.CTkFont(size=11), text_color=("gray50","gray60")).pack(side="right", padx=6)
        # descricao
        box = ctk.CTkFrame(self.right); box.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(box, text="Descricao", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,2))
        ctk.CTkLabel(box, text=m.get("description",""), wraplength=420, justify="left", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(0,10))
        # passos
        steps = m.get("steps",[])
        if steps:
            sbox = ctk.CTkFrame(self.right); sbox.pack(fill="x", padx=6, pady=6)
            ctk.CTkLabel(sbox, text=f"Passo a passo — execucao ({len(steps)} etapas)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,4))
            for i, st in enumerate(steps, 1):
                r = ctk.CTkFrame(sbox, fg_color=("gray92","gray18")); r.pack(fill="x", padx=8, pady=2)
                ctk.CTkLabel(r, text=f"{i}", width=28, height=28, corner_radius=14, fg_color="#3498db", text_color="white", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=8, pady=6)
                ctk.CTkLabel(r, text=st, wraplength=360, justify="left", anchor="w", font=ctk.CTkFont(size=12)).pack(side="left", fill="x", expand=True, padx=(0,8), pady=6)
        # prereq + erros em 2 colunas
        bot = ctk.CTkFrame(self.right, fg_color="transparent"); bot.pack(fill="x", padx=6, pady=6)
        bot.grid_columnconfigure((0,1), weight=1)
        pre = ctk.CTkFrame(bot); pre.grid(row=0,column=0, sticky="nsew", padx=(0,4))
        ctk.CTkLabel(pre, text="Pre-requisitos", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", padx=10, pady=(8,2))
        ctk.CTkLabel(pre, text=m.get("prerequisites","Conhecimento basico da fase."), wraplength=200, justify="left", font=ctk.CTkFont(size=11), text_color=("gray45","gray65")).pack(anchor="w", padx=10, pady=(0,10))
        err = ctk.CTkFrame(bot, fg_color=("#ffeaea","#2a1515"), border_width=1, border_color="#e74c3c"); err.grid(row=0,column=1, sticky="nsew", padx=(4,0))
        ctk.CTkLabel(err, text="Erros comuns", font=ctk.CTkFont(weight="bold", size=12), text_color="#e74c3c").pack(anchor="w", padx=10, pady=(8,2))
        ce = m.get("common_errors","")
        if isinstance(ce, list): ce = " • ".join(ce)
        ctk.CTkLabel(err, text=ce or "Nenhum erro catalogado.", wraplength=200, justify="left", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(0,10))
        # seguranca
        sec = ctk.CTkFrame(self.right, fg_color=("#fff7cc","#2a2410"), border_width=1, border_color="#f1c40f"); sec.pack(fill="x", padx=6, pady=8)
        ctk.CTkLabel(sec, text="Nota de seguranca: sempre sob supervisao de instrutor em voo dual.", wraplength=420, justify="left", font=ctk.CTkFont(size=11)).pack(padx=10, pady=8)
        if self.on_maneuver_select:
            try: self.on_maneuver_select(m)
            except: pass
