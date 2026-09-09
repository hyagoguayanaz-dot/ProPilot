"""
QRH / Manuais View - Aba dedicada por aeronave
"""
import customtkinter as ctk
import sys, os, json
from typing import Callable, Dict, List

def resource_path(rel):
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

class ManualsView(ctk.CTkFrame):
    def __init__(self, parent, on_back: Callable=None, theme_manager=None):
        super().__init__(parent)
        self.on_back = on_back
        self.theme_manager = theme_manager
        self.data = {}
        self._selected_id = None
        self._section = "manual"  # manual | qrh | perf | limites
        try:
            p = resource_path(os.path.join("data","manuals.json"))
            if not os.path.exists(p):
                p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data","manuals.json")
            with open(p, encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception as e:
            print("manuals load err", e)
            self.data = {"aircraft":[]}
        self._build()
        # auto-select first
        if self.data.get("aircraft"):
            self._selected_id = self.data["aircraft"][0]["id"]
            self._show_detail(self.data["aircraft"][0])
        self._refresh_list()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        # header
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.grid(row=0,column=0, sticky="ew", padx=8, pady=(8,4)); h.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(h, text="QRH / Manuais", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0,column=0, sticky="w", padx=6)
        ctk.CTkLabel(h, text="Manuais de operação e Quick Reference por aeronave", font=ctk.CTkFont(size=12), text_color=("gray50","gray60")).grid(row=1,column=0, sticky="w", padx=6)
        if self.on_back:
            ctk.CTkButton(h, text="← Voltar", width=90, height=28, command=self.on_back).grid(row=0,column=1,rowspan=2, sticky="e", padx=6)
        # search
        s = ctk.CTkFrame(self); s.grid(row=1,column=0, sticky="ew", padx=8, pady=4); s.grid_columnconfigure(0, weight=1)
        self.search = ctk.CTkEntry(s, placeholder_text="Buscar aeronave ou procedimento... ex: C172, fogo, Vne")
        self.search.pack(fill="x", padx=8, pady=8)
        self.search.bind("<KeyRelease>", lambda e: self._refresh_list())
        # body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2,column=0, sticky="nsew", padx=8, pady=(4,8))
        body.grid_columnconfigure(0, weight=0, minsize=260)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)
        # left
        self.left = ctk.CTkScrollableFrame(body, label_text="Aeronaves da frota", label_text_color=("#1f538d","#4cc2ff"), width=260)
        self.left.grid(row=0,column=0, sticky="nsew", padx=(0,4))
        # right
        self.right = ctk.CTkScrollableFrame(body, label_text="Selecione uma aeronave")
        self.right.grid(row=0,column=1, sticky="nsew", padx=(4,0))

    def _refresh_list(self):
        term = (self.search.get() or "").strip().lower()
        for w in self.left.winfo_children(): w.destroy()
        for ac in self.data.get("aircraft",[]):
            hay = " ".join([ac.get("name",""), ac.get("icao",""), ac.get("role",""), ac.get("overview","")]).lower()
            # também busca em qrh
            if term and term not in hay:
                # busca em qrh titles
                qrh_hay = " ".join([q.get("title","") for q in ac.get("qrh",[])])
                if term not in qrh_hay.lower():
                    continue
            is_sel = self._selected_id == ac["id"]
            card = ctk.CTkFrame(self.left, corner_radius=10, border_width=2 if is_sel else 1, border_color="#4cc2ff" if is_sel else ("gray75","gray30"))
            card.pack(fill="x", padx=6, pady=5)
            card.bind("<Button-1>", lambda e,a=ac: self._select(a))
            ctk.CTkLabel(card, text=ac["name"], font=ctk.CTkFont(weight="bold", size=13), anchor="w").pack(anchor="w", padx=10, pady=(8,2))
            for child in card.winfo_children(): child.bind("<Button-1>", lambda e,a=ac: self._select(a))
            ctk.CTkLabel(card, text=ac["icao"], font=ctk.CTkFont(size=11), text_color=("#1f538d","#4cc2ff")).pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=ac["role"], font=ctk.CTkFont(size=11), text_color=("gray50","gray60"), wraplength=220, justify="left").pack(anchor="w", padx=10, pady=(2,8))
            # specs mini
            specs = ac.get("specs",{})
            if specs:
                mini = list(specs.items())[:2]
                txt = " • ".join([f"{k}: {v}" for k,v in mini])
                ctk.CTkLabel(card, text=txt, font=ctk.CTkFont(size=10), text_color=("gray45","gray65"), wraplength=220, justify="left").pack(anchor="w", padx=10, pady=(0,8))
                for ch in card.winfo_children(): ch.bind("<Button-1>", lambda e,a=ac: self._select(a))

    def _select(self, ac: Dict):
        self._selected_id = ac["id"]
        self._show_detail(ac)
        self._refresh_list()
        self._show_detail(ac)

    def _show_detail(self, ac: Dict):
        for w in self.right.winfo_children(): w.destroy()
        try: self.right.configure(label_text=f"{ac['name']} — {ac['icao']}")
        except: pass
        # header info
        hdr = ctk.CTkFrame(self.right); hdr.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(hdr, text=ac["name"], font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=(8,2))
        ctk.CTkLabel(hdr, text=ac["role"], font=ctk.CTkFont(size=12), text_color=("#1f538d","#4cc2ff")).pack(anchor="w", padx=10)
        ctk.CTkLabel(hdr, text=ac["overview"], wraplength=520, justify="left", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(6,4))
        ctk.CTkLabel(hdr, text=ac.get("image_hint",""), font=ctk.CTkFont(size=11, slant="italic"), text_color=("gray50","gray60")).pack(anchor="w", padx=10, pady=(0,8))
        # aviso POH
        warn = ctk.CTkFrame(self.right, fg_color=("#fff3cd","#332a00"), border_width=1, border_color="#ffc107"); warn.pack(fill="x", padx=6, pady=4)
        ctk.CTkLabel(warn, text="⚠️ QRH de estudo — sempre consulte o POH/AFM oficial e checklist plastificado da aeronave antes do voo.", wraplength=520, justify="left", font=ctk.CTkFont(size=11, weight="bold")).pack(padx=10, pady=8)
        # segmented control
        seg = ctk.CTkFrame(self.right, fg_color="transparent"); seg.pack(fill="x", padx=6, pady=6)
        for key,label in [("manual","Manual"),("qrh","QRH Emergência"),("limites","Limitações"),("perf","Performance")]:
            btn = ctk.CTkButton(seg, text=label, width=110, height=28,
                                fg_color="#4cc2ff" if self._section==key else ("gray75","gray30"),
                                text_color="white" if self._section==key else ("black","white"),
                                command=lambda k=key, a=ac: self._switch(k,a))
            btn.pack(side="left", padx=4)
        # also quick ref sempre visível no topo quando manual
        if self._section == "manual":
            self._render_manual(ac)
        elif self._section == "qrh":
            self._render_qrh(ac)
        elif self._section == "limites":
            self._render_limites(ac)
        elif self._section == "perf":
            self._render_perf(ac)
        # quick ref bottom
        qr = ac.get("quick_ref",{})
        if qr:
            box = ctk.CTkFrame(self.right, fg_color=("#e8f8f5","#0f2a23"), border_width=1, border_color="#2ecc71"); box.pack(fill="x", padx=6, pady=8)
            ctk.CTkLabel(box, text="⚡ Quick Reference — velocidades de bolso", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,2))
            for k,v in qr.items():
                ctk.CTkLabel(box, text=f"• {k}: {v}", wraplength=500, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=10, pady=1)
            ctk.CTkLabel(box, text="", height=4).pack()

    def _switch(self, key, ac):
        self._section = key
        self._show_detail(ac)

    def _render_manual(self, ac):
        procs = ac.get("normal_procedures",[])
        for sec in procs:
            box = ctk.CTkFrame(self.right); box.pack(fill="x", padx=6, pady=5)
            ctk.CTkLabel(box, text=sec["title"], font=ctk.CTkFont(weight="bold", size=13)).pack(anchor="w", padx=10, pady=(8,4))
            for item in sec.get("checklist",[]):
                row = ctk.CTkFrame(box, fg_color=("gray92","gray18")); row.pack(fill="x", padx=8, pady=2)
                ctk.CTkLabel(row, text="☐", font=ctk.CTkFont(size=13)).pack(side="left", padx=8, pady=4)
                ctk.CTkLabel(row, text=item, wraplength=460, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(side="left", padx=(0,8), pady=4, fill="x", expand=True)

    def _render_qrh(self, ac):
        for q in ac.get("qrh",[]):
            is_mem = q.get("memory", False)
            bg = ("#fdedec","#2a1515") if is_mem else ("gray92","gray18")
            border = "#e74c3c" if is_mem else ("gray75","gray30")
            box = ctk.CTkFrame(self.right, fg_color=bg, border_width=1, border_color=border); box.pack(fill="x", padx=6, pady=5)
            title_row = ctk.CTkFrame(box, fg_color="transparent"); title_row.pack(fill="x", padx=8, pady=(8,2))
            badge = "MEMÓRIA" if is_mem else "QRH"
            ctk.CTkLabel(title_row, text=badge, fg_color="#e74c3c" if is_mem else "#2c3e50", text_color="white", corner_radius=4, padx=6, pady=2, font=ctk.CTkFont(size=10, weight="bold")).pack(side="left")
            ctk.CTkLabel(title_row, text=q["title"], font=ctk.CTkFont(weight="bold", size=12)).pack(side="left", padx=8)
            for idx, step in enumerate(q.get("steps",[]),1):
                r = ctk.CTkFrame(box, fg_color=("white","gray22") if is_mem else ("white","gray20")); r.pack(fill="x", padx=8, pady=2)
                ctk.CTkLabel(r, text=f"{idx}", width=22, height=22, corner_radius=11, fg_color="#e74c3c" if is_mem else "#3498db", text_color="white", font=ctk.CTkFont(weight="bold", size=11)).pack(side="left", padx=8, pady=4)
                ctk.CTkLabel(r, text=step, wraplength=430, justify="left", font=ctk.CTkFont(size=11, weight="bold" if is_mem else "normal"), anchor="w").pack(side="left", padx=(0,8), pady=4, fill="x", expand=True)
            if is_mem:
                ctk.CTkLabel(box, text="Item de memória — decore e execute sem consultar.", font=ctk.CTkFont(size=10, slant="italic"), text_color="#c0392b").pack(anchor="w", padx=10, pady=(2,6))

    def _render_limites(self, ac):
        box = ctk.CTkFrame(self.right); box.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(box, text="Limitações e velocidades (KIAS salvo indicado)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,6))
        for k,v in ac.get("limitations",{}).items():
            row = ctk.CTkFrame(box, fg_color=("gray92","gray18")); row.pack(fill="x", padx=8, pady=2)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row, text=k, font=ctk.CTkFont(size=11, weight="bold"), anchor="w").grid(row=0,column=0, sticky="w", padx=8, pady=4)
            ctk.CTkLabel(row, text=v, font=ctk.CTkFont(size=11), anchor="e", text_color=("#c0392b" if "nunca" in k.lower() or "Vne" in k else ("gray20","gray80"))).grid(row=0,column=1, sticky="e", padx=8)
        specs = ac.get("specs",{})
        if specs:
            sbox = ctk.CTkFrame(self.right); sbox.pack(fill="x", padx=6, pady=6)
            ctk.CTkLabel(sbox, text="Especificações", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,6))
            for k,v in specs.items():
                r = ctk.CTkFrame(sbox, fg_color=("gray92","gray18")); r.pack(fill="x", padx=8, pady=1)
                ctk.CTkLabel(r, text=k, font=ctk.CTkFont(size=11), anchor="w").pack(side="left", padx=8, pady=4)
                ctk.CTkLabel(r, text=v, font=ctk.CTkFont(size=11), text_color=("gray50","gray60"), wraplength=260, justify="right", anchor="e").pack(side="right", padx=8)

    def _render_perf(self, ac):
        box = ctk.CTkFrame(self.right); box.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(box, text="Performance (condições padrão, pista pavimentada)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,6))
        for k,v in ac.get("performance",{}).items():
            r = ctk.CTkFrame(box, fg_color=("gray92","gray18")); r.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(r, text=k, font=ctk.CTkFont(size=11), anchor="w", wraplength=220).pack(side="left", padx=8, pady=4)
            ctk.CTkLabel(r, text=v, font=ctk.CTkFont(size=11, weight="bold"), anchor="e").pack(side="right", padx=8)
