"""
SOP View - Exibe o Standard Operating Procedures (SOP) - ACP 2023 completo
Baseado em P-56C Paulistinha, com busca e navegação por seções
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

class SOPView(ctk.CTkFrame):
    def __init__(self, parent, on_back: Callable=None, theme_manager=None):
        super().__init__(parent, fg_color="transparent")
        self.on_back = on_back
        self.theme_manager = theme_manager
        self.sop_data = {}
        self.sop_ex_data = {}
        self._selected = None
        # Load SOP
        try:
            p = resource_path(os.path.join("data","sop.json"))
            if not os.path.exists(p):
                p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data","sop.json")
            with open(p, encoding="utf-8") as f:
                self.sop_data = json.load(f)
        except Exception as e:
            print("sop load err", e)
            self.sop_data = {}
        try:
            p2 = resource_path(os.path.join("data","sop_exercises.json"))
            if not os.path.exists(p2):
                p2 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data","sop_exercises.json")
            with open(p2, encoding="utf-8") as f:
                self.sop_ex_data = json.load(f)
        except:
            self.sop_ex_data = {}
        self._build()
        # auto-select first
        if self.sop_data:
            first = list(self.sop_data.keys())[0]
            self._selected = first
            self._show_detail(first)
        self._refresh_list()

    def _cols(self):
        if self.theme_manager and self.theme_manager.current_theme == "light":
            return {"card":"#FFFFFF","hover":"#F0F0F0","text":"#121212","sub":"#6A6A6A","line":"#E0E0E0","bg":"#F5F5F5"}
        else:
            return {"card":"#181818","hover":"#282828","text":"#FFFFFF","sub":"#B3B3B3","line":"#2A2A2A","bg":"#121212"}

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        cols = self._cols()
        # header
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.grid(row=0,column=0, sticky="ew", padx=8, pady=(8,4)); h.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(h, text="SOP — Standard Operating Procedures", font=ctk.CTkFont(size=18, weight="bold"), text_color=cols["text"]).grid(row=0,column=0, sticky="w", padx=6)
        ctk.CTkLabel(h, text="ACP 2023 • P-56C Paulistinha • Consulta rápida", font=ctk.CTkFont(size=11), text_color=cols["sub"]).grid(row=1,column=0, sticky="w", padx=6)
        if self.on_back:
            ctk.CTkButton(h, text="← Voltar", width=90, height=28, corner_radius=20, fg_color=cols["card"], hover_color=cols["hover"], text_color=cols["text"], command=self.on_back).grid(row=0,column=1,rowspan=2, sticky="e")
        # search
        s = ctk.CTkFrame(self, fg_color=cols["card"], corner_radius=8)
        s.grid(row=1,column=0, sticky="ew", padx=8, pady=4); s.grid_columnconfigure(0, weight=1)
        self._search_job = None
        self.search = ctk.CTkEntry(s, placeholder_text="Buscar no SOP... ex: decolagem, estol, pane, cheque", fg_color=cols["hover"], border_color=cols["line"], text_color=cols["text"])
        self.search.pack(fill="x", padx=10, pady=10)
        self.search.bind("<KeyRelease>", self._on_search_debounced)
        # body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2,column=0, sticky="nsew", padx=8, pady=(4,8))
        body.grid_columnconfigure(0, weight=0, minsize=280)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)
        self.left = ctk.CTkScrollableFrame(body, label_text="Seções do SOP", label_text_color=cols["sub"], fg_color=cols["card"], width=280)
        self.left.grid(row=0,column=0, sticky="nsew", padx=(0,4))
        self.right = ctk.CTkScrollableFrame(body, label_text="Selecione uma seção", fg_color=cols["card"])
        self.right.grid(row=0,column=1, sticky="nsew", padx=(4,0))

    def _on_search_debounced(self, event=None):
        if hasattr(self, '_search_job') and self._search_job:
            try: self.after_cancel(self._search_job)
            except: pass
        target = getattr(self, '_refresh', None) or getattr(self, '_refresh_list', None)
        if target:
            self._search_job = self.after(180, target)

    def _refresh_list(self):
        term = (self.search.get() or "").strip().lower()
        for w in self.left.winfo_children(): w.destroy()
        cols = self._cols()
        acc = self.theme_manager.get_accent() if self.theme_manager else "#1DB954"
        matched = []
        for title in self.sop_data.keys():
            if term and term not in title.lower() and term not in self.sop_data[title].lower():
                continue
            matched.append(title)
        if not matched:
            ctk.CTkLabel(self.left, text="Nenhuma seção encontrada.", text_color=cols["sub"]).pack(pady=20)
            return
        for title in matched:
            is_sel = self._selected == title
            card = ctk.CTkFrame(self.left, fg_color=acc if is_sel else cols["hover"], corner_radius=8, border_width=2 if is_sel else 0, border_color=acc)
            card.pack(fill="x", padx=6, pady=4)
            card.bind("<Button-1>", lambda e,t=title: self._select(t))
            lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="white" if is_sel else cols["text"], anchor="w", wraplength=240, justify="left")
            lbl.pack(anchor="w", padx=10, pady=(8,4))
            lbl.bind("<Button-1>", lambda e,t=title: self._select(t))
            preview = self.sop_data[title][:80].replace("\n"," ") + "…"
            ctk.CTkLabel(card, text=preview, font=ctk.CTkFont(size=10), text_color="white" if is_sel else cols["sub"], wraplength=240, justify="left", anchor="w").pack(anchor="w", padx=10, pady=(0,8))
            card.bind("<Button-1>", lambda e,t=title: self._select(t))
            for ch in card.winfo_children():
                try: ch.bind("<Button-1>", lambda e,t=title: self._select(t))
                except: pass

    def _select(self, title):
        self._selected = title
        self._show_detail(title)
        self._refresh_list()
        self._show_detail(title)

    def _show_detail(self, title):
        for w in self.right.winfo_children(): w.destroy()
        cols = self._cols()
        try: self.right.configure(label_text=title[:50])
        except: pass
        # header
        hdr = ctk.CTkFrame(self.right, fg_color=cols["hover"], corner_radius=8)
        hdr.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(hdr, text=title, font=ctk.CTkFont(size=15, weight="bold"), text_color=cols["text"], wraplength=500, justify="left").pack(anchor="w", padx=12, pady=(10,4))
        ctk.CTkLabel(hdr, text="SOP ACP 2023 • P-56C Paulistinha • Procedimento oficial", font=ctk.CTkFont(size=11), text_color=cols["sub"]).pack(anchor="w", padx=12, pady=(0,10))
        # content
        txt = self.sop_data.get(title, "")
        # quebrar em parágrafos
        body = ctk.CTkFrame(self.right, fg_color="transparent")
        body.pack(fill="x", padx=6, pady=6)
        # dividir por sentenças para melhor leitura
        import re
        sentences = re.split(r'(?<=[\.:\;])\s+', txt)
        # agrupa em blocos de 2-3 sentenças
        chunk = ""
        for sent in sentences:
            if not sent.strip(): continue
            if len(chunk) + len(sent) < 400:
                chunk += " " + sent if chunk else sent
            else:
                ctk.CTkLabel(body, text=chunk.strip(), wraplength=520, justify="left", font=ctk.CTkFont(size=12), text_color=cols["text"], anchor="w").pack(anchor="w", padx=10, pady=4)
                chunk = sent
        if chunk:
            ctk.CTkLabel(body, text=chunk.strip(), wraplength=520, justify="left", font=ctk.CTkFont(size=12), text_color=cols["text"], anchor="w").pack(anchor="w", padx=10, pady=4)
        # nota rodapé
        foot = ctk.CTkFrame(self.right, fg_color="#fff3cd" if self.theme_manager and self.theme_manager.current_theme=="light" else "#332a00", corner_radius=8, border_width=1, border_color="#ffc107")
        foot.pack(fill="x", padx=6, pady=8)
        ctk.CTkLabel(foot, text="Nota: Este SOP é baseado no P-56C Paulistinha. Para outra aeronave, consulte o adendo específico e o checklist da aeronave. Sempre confirme com o IN antes do voo.", wraplength=500, justify="left", font=ctk.CTkFont(size=11)).pack(padx=10, pady=8)
