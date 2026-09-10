#!/usr/bin/env python3
"""
ProPilot Mobile - KivyMD 2.0 App
6 telas: Dashboard, Missões, Central Estudos, QRH/Manuais, SOP, Configurações
Design Spotify dark #121212 / light #FFFFFF + 8 accents
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer, MDDialogContentContainer
from kivymd.uix.divider import MDDivider
from kivymd.uix.scrollview import MDScrollView

# ---------------------------------------------------------------------------
# Paths & Data
# ---------------------------------------------------------------------------
def resource_path(rel: str) -> str:
    """Resolve data file: mobile/data -> ../data fallback, also frozen."""
    try:
        base = Path(sys._MEIPASS)  # type: ignore
        p = base / rel
        if p.exists():
            return str(p)
    except Exception:
        pass
    here = Path(__file__).parent
    cand = here / rel
    if cand.exists():
        return str(cand)
    # mobile/data fallback to ../data
    alt = here.parent / rel.replace("mobile/data", "data").replace("data\\", "data/")
    # try both
    for a in [here / "data" / Path(rel).name, here.parent / "data" / Path(rel).name]:
        if a.exists():
            return str(a)
    return str(cand)

def load_json(rel: str, default):
    try:
        p = resource_path(rel)
        if not os.path.exists(p):
            # try mobile/data vs data
            for alt in [Path(__file__).parent / "data" / Path(rel).name, Path(__file__).parent.parent / "data" / Path(rel).name]:
                if alt.exists():
                    p = str(alt)
                    break
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"load_json {rel} err: {e}")
        return default

# ---------------------------------------------------------------------------
# Theme / Constants
# ---------------------------------------------------------------------------
ACCENTS = {
    "spotify": {"name": "Spotify Green", "color": "#1DB954", "hover": "#1ED760"},
    "ocean":   {"name": "Ocean Blue",    "color": "#3B82F6", "hover": "#60A5FA"},
    "violet":  {"name": "Violet Haze",   "color": "#8B5CF6", "hover": "#A78BFA"},
    "pink":    {"name": "Hot Pink",      "color": "#EC4899", "hover": "#F472B6"},
    "sunset":  {"name": "Sunset Orange", "color": "#F59E0B", "hover": "#FBBF24"},
    "crimson": {"name": "Crimson Red",   "color": "#EF4444", "hover": "#F87171"},
    "teal":    {"name": "Teal Wave",     "color": "#06B6D4", "hover": "#22D3EE"},
    "lime":    {"name": "Lime Pulse",    "color": "#84CC16", "hover": "#A3E635"},
}

DARK =  {"bg":"#121212","card":"#1E1E1E","elevated":"#242424","hover":"#2A2A2A","text":"#FFFFFF","sub":"#B3B3B3","line":"#2A2A2A"}
LIGHT = {"bg":"#FFFFFF","card":"#F5F5F5","elevated":"#EEEEEE","hover":"#E8E8E8","text":"#121212","sub":"#6A6A6A","line":"#E0E0E0"}

LEVEL_COLORS = {"M":"#9E9E9E","C":"#F59E0B","A":"#3B82F6","E":"#1DB954","X":"#8B5CF6","m":"#9E9E9E","c":"#F59E0B","a":"#3B82F6"}
LEVEL_OFICIAL = {
    "M": ("M — Memorização", "Conhecer e memorizar a sequência. O instrutor demonstra e o aluno acompanha. Não se exige execução autônoma."),
    "C": ("C — Compreensão", "Executar COM auxílio direto do instrutor. O aluno age, mas o IN intervém e corrige."),
    "A": ("A — Aplicação", "Executar com supervisão mínima. O aluno realiza sozinho, o IN apenas acompanha."),
    "E": ("E — Execução", "Execução autônoma e correta, padrão de segurança já próximo ao solo."),
    "X": ("X — Excelência", "Domínio total. Execução perfeita, sem intervenção, apto a solo/cheque."),
}
LEVEL_OFICIAL["m"]=LEVEL_OFICIAL["M"]; LEVEL_OFICIAL["c"]=LEVEL_OFICIAL["C"]; LEVEL_OFICIAL["a"]=LEVEL_OFICIAL["A"]

EXERCISE_HELP = {
    "livro de bordo":("Esquecer documentação / preencher horas errado.","Chegue 15 min antes, confira diário e validade da IAM."),
    "inspeção":("Pular itens / não checar combustível/óleo.","Siga checklist externo→interno, toque e confirme em voz alta."),
    "partida do motor":("Afogamento / hélice sem área livre.","Área livre, freio, mistura rica, chamada 'hélice livre'."),
    "fraseologia":("Falar rápido / esquecer prefixo.","Padrão ICAO, fale pausado, colacione autorizações."),
    "rolagem":("Taxi rápido / freio brusco.","Taxi lento (passo humano), teste freios nos primeiros metros."),
    "taxiamento":("Taxi rápido / freio brusco.","Taxi lento, manche contra vento se houver."),
    "decolagem normal":("Corrigir com freio / rotacionar cedo.","Alinhe no eixo, corrija só com pedais, Vr 55-65 kt."),
    "saída do tráfego":("Curvar antes de 500 ft.","Mantenha rumo até 500 ft AGL, informe saída."),
    "subida":("Nariz alto demais / não compensar.","Mantenha Vy e compense para mãos leves."),
    "nivelamento":("Nivelar brusco / esquecer potência.","Antecipe 10% da razão, nivele, ajuste 2200 RPM."),
    "curva":("Inclinação errada / perder altitude.","Inclinação constante, esfera no centro, olhe horizonte."),
    "estol":("Puxar manche no estol / usar aileron.","Manche à frente, potência máxima, nivelar com pedal."),
    "pouso":("Flare alto / freio brusco.","Rampa com potência, flare 1 m, toque trem principal."),
    "arremetida":("Esquecer flape / não aplicar potência.","Potência máxima, flape 20→10→0 em etapas, Vy."),
    "pane":("Tentar voltar para pista.","Nariz para 60 KIAS, escolha área à frente ±30°."),
    "navegação":("Desorientar / esquecer proa.","Compare carta-terreno a cada 2-3 min, rumos de regresso."),
    "noturno":("Ofuscamento / ilusão visual.","Use luzes, mantenha instrumentos em scan, reduza carga."),
}

def greeting_for_hour(h: int) -> str:
    if 5 <= h < 12: return "Bom dia"
    if 12 <= h < 18: return "Boa tarde"
    return "Boa noite"

def find_exercise_help(name: str):
    low = name.lower()
    for k, v in EXERCISE_HELP.items():
        if k in low:
            return v
    return ("Falta de briefing / executar sem compensar.","Estude o SOP da manobra, brife com o IN e compense corretamente.")

def hex_to_rgba(h: str):
    return get_color_from_hex(h)

# ---------------------------------------------------------------------------
# Dialog helper
# ---------------------------------------------------------------------------
_dialog = None
def show_dialog(app, title: str, text: str):
    global _dialog
    try:
        if _dialog: _dialog.dismiss()
    except: pass
    from kivymd.uix.button import MDButton, MDButtonText
    _dialog = MDDialog(
        MDDialogHeadlineText(text=title),
        MDDialogSupportingText(text=text),
        MDDialogButtonContainer(
            MDButton(MDButtonText(text="Fechar"), style="text", on_release=lambda x: _dialog.dismiss()),
            spacing="8dp",
        ),
        size_hint=(0.9, None),
    )
    _dialog.open()

# ---------------------------------------------------------------------------
# Base screen helpers
# ---------------------------------------------------------------------------
class BaseScreen(MDScreen):
    accent = StringProperty("#1DB954")
    def cols(self):
        app = MDApp.get_running_app()
        return app.get_colors()
    def accent_hex(self):
        return MDApp.get_running_app().get_accent()

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "dashboard"
        self.md_bg_color = hex_to_rgba(DARK["bg"])
        self._build()

    def _build(self):
        root = MDBoxLayout(orientation="vertical", padding=[dp(16),dp(12),dp(16),dp(0)], spacing=dp(12))
        # header greeting
        self.greet_lbl = MDLabel(text="Boa tarde, piloto", font_style="Headline", role="small", size_hint_y=None, height=dp(28))
        self.sub_lbl = MDLabel(text="", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(18))
        self.time_lbl = MDLabel(text="", font_style="Label", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(16))
        root.add_widget(self.greet_lbl)
        root.add_widget(self.sub_lbl)
        root.add_widget(self.time_lbl)

        # stats row - 2 cards
        row = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(92))
        self.phase_card = MDCard(style="elevated", padding=dp(12), size_hint_x=0.55)
        self.phase_card.md_bg_color = hex_to_rgba(DARK["card"])
        pc_box = MDBoxLayout(orientation="vertical", spacing=dp(4))
        pc_box.add_widget(MDLabel(text="FASE ATUAL", font_style="Label", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(14)))
        self.phase_val = MDLabel(text="Pré-Solo (PS)", font_style="Title", role="medium", size_hint_y=None, height=dp(22))
        pc_box.add_widget(self.phase_val)
        self.phase_sub = MDLabel(text="0/19 missões", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(16))
        pc_box.add_widget(self.phase_sub)
        self.phase_card.add_widget(pc_box)
        row.add_widget(self.phase_card)

        self.hours_card = MDCard(style="elevated", padding=dp(12), size_hint_x=0.45)
        self.hours_card.md_bg_color = hex_to_rgba(DARK["card"])
        hc = MDBoxLayout(orientation="vertical", spacing=dp(4))
        hc.add_widget(MDLabel(text="HORAS DE VOO", font_style="Label", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(14)))
        self.hours_val = MDLabel(text="0.0 h", font_style="Title", role="medium", size_hint_y=None, height=dp(22))
        hc.add_widget(self.hours_val)
        self.hours_sub = MDLabel(text="Solo: 0.0 h", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(16))
        hc.add_widget(self.hours_sub)
        self.hours_card.add_widget(hc)
        row.add_widget(self.hours_card)
        root.add_widget(row)

        # progress card
        self.progress_card = MDCard(style="elevated", padding=dp(14), size_hint_y=None, height=dp(84))
        self.progress_card.md_bg_color = hex_to_rgba(DARK["card"])
        pbox = MDBoxLayout(orientation="vertical", spacing=dp(6))
        pbox.add_widget(MDLabel(text="Progresso geral", font_style="Title", role="small", size_hint_y=None, height=dp(18)))
        self.progress_lbl = MDLabel(text="0 de 36 missões concluídas", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(16))
        pbox.add_widget(self.progress_lbl)
        self.progress_bar_wrap = MDBoxLayout(size_hint_y=None, height=dp(6))
        from kivymd.uix.progressindicator import MDLinearProgressIndicator
        self.progress_bar = MDLinearProgressIndicator(value=0, size_hint_y=None, height=dp(6))
        self.progress_bar_wrap.add_widget(self.progress_bar)
        pbox.add_widget(self.progress_bar_wrap)
        self.progress_card.add_widget(pbox)
        root.add_widget(self.progress_card)

        # quick access
        root.add_widget(MDLabel(text="Acesso rápido", font_style="Title", role="small", size_hint_y=None, height=dp(22)))
        qa = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(74))
        for icon, label, target in [("airplane","Missões","missions"),("book-open-variant","Estudos","study"),("file-document","SOP","sop")]:
            c = MDCard(style="outlined", padding=dp(8), on_release=lambda x, t=target: MDApp.get_running_app().switch_to(t))
            c.md_bg_color = hex_to_rgba(DARK["card"])
            b = MDBoxLayout(orientation="vertical", spacing=dp(2))
            b.add_widget(MDLabel(text=label, halign="center", font_style="Label", role="medium", size_hint_y=None, height=dp(18)))
            b.add_widget(MDLabel(text="Toque para abrir →", halign="center", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(14)))
            c.add_widget(b)
            qa.add_widget(c)
        root.add_widget(qa)

        # tip
        self.tip_card = MDCard(style="filled", padding=dp(12), size_hint_y=None, height=dp(64))
        self.tip_card.md_bg_color = hex_to_rgba(DARK["elevated"])
        self.tip_lbl = MDLabel(text="Dica: toque em um exercício com nível M/C/A/E/X para ver a cobrança oficial.", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]))
        self.tip_card.add_widget(self.tip_lbl)
        root.add_widget(self.tip_card)
        root.add_widget(MDBoxLayout(size_hint_y=None, height=dp(80)))  # spacer for bottom nav

        sc = MDScrollView()
        sc.add_widget(root)
        self.add_widget(sc)
        Clock.schedule_interval(lambda dt: self.refresh_header(), 60)
        Clock.schedule_once(lambda dt: self.refresh(), 0.3)

    def refresh_header(self):
        try:
            app = MDApp.get_running_app()
            db = app.db
            prof = db.load_progress().get("profile", {})
            name = prof.get("display_name") or db.load_settings().get("display_name") or "Piloto-Aluno"
            now = datetime.now()
            greet = greeting_for_hour(now.hour)
            self.greet_lbl.text = f"{greet}, {name}"
            self.sub_lbl.text = f"{prof.get('school','Aeroclube de Pirassununga')} • {now.strftime('%d/%m/%Y')}"
            self.time_lbl.text = now.strftime("%H:%M • %A")
        except Exception:
            pass

    def refresh(self):
        self.refresh_header()
        try:
            app = MDApp.get_running_app()
            db = app.db
            prog = db.load_progress()
            cols = app.get_colors()
            accent = app.get_accent()
            # theme bg
            self.md_bg_color = hex_to_rgba(cols["bg"])
            for c in [self.phase_card, self.hours_card, self.progress_card]:
                c.md_bg_color = hex_to_rgba(cols["card"])
            self.tip_card.md_bg_color = hex_to_rgba(cols["elevated"])
            # phase
            phase = prog.get("profile",{}).get("current_phase","PS")
            phase_names = {"PS":"Pré-Solo (PS)","AP":"Aperfeiçoamento (AP)","NV":"Navegação (NV)","NOT":"Noturno (NOT)"}
            self.phase_val.text = phase_names.get(phase, phase)
            sp = prog.get("study_progress",{}).get(phase, {})
            tot = sp.get("total", 19)
            comp = len([m for m in prog.get("completed_missions",[]) if m.startswith(phase+"-")])
            self.phase_sub.text = f"{comp}/{tot} missões"
            # hours
            self.hours_val.text = f"{prog.get('profile',{}).get('total_flight_hours',0):.1f} h"
            self.hours_sub.text = f"Solo: {prog.get('profile',{}).get('solo_hours',0):.1f} h"
            # geral
            total_done = len(prog.get("completed_missions",[]))
            self.progress_lbl.text = f"{total_done} de 36 missões concluídas"
            self.progress_bar.value = (total_done/36*100) if total_done else 0
            # text colors
            for lbl in [self.greet_lbl, self.phase_val, self.hours_val]:
                lbl.text_color = hex_to_rgba(cols["text"])
        except Exception as e:
            print("dashboard refresh err", e)

    def on_enter(self, *args):
        self.refresh()

# ---------------------------------------------------------------------------
# Missões
# ---------------------------------------------------------------------------
class MissionsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "missions"
        self.md_bg_color = hex_to_rgba(DARK["bg"])
        self._filter_phase = "ALL"
        self._search = ""
        self._data = load_json("data/missions.json", {"missions":{},"info":{}})
        self._sop_ex = load_json("data/sop_exercises.json", {})
        self._all_missions = []
        for pk, pv in self._data.get("missions", {}).items():
            for m in pv.get("missions", []):
                mm = dict(m); mm["_phase"] = pk
                self._all_missions.append(mm)
        self._build()

    def _build(self):
        root = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(12),dp(8),dp(12),dp(0)])
        root.add_widget(MDLabel(text="Missões", font_style="Headline", role="small", size_hint_y=None, height=dp(28)))
        root.add_widget(MDLabel(text="36 missões • toque no card para detalhes", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(16)))

        # search
        self.search_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(48))
        self.search_field.hint_text = "Buscar missão, exercício ou fase..."
        self.search_field.bind(text=self._on_search)
        root.add_widget(self.search_field)

        # phase chips row
        chip_row = MDBoxLayout(spacing=dp(6), size_hint_y=None, height=dp(36), padding=[0,dp(4),0,0])
        for ph in ["ALL","PS","AP","NV","NOT"]:
            btn = MDButton(style="outlined", size_hint_x=None, width=dp(62), height=dp(32), on_release=lambda x, p=ph: self._set_phase(p))
            btn.add_widget(MDButtonText(text=ph if ph!="ALL" else "Todas", pos_hint={"center_x":0.5,"center_y":0.5}))
            chip_row.add_widget(btn)
        self._chip_row = chip_row
        root.add_widget(chip_row)

        # list scroll
        self.list_box = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=[0,0,0,dp(88)], adaptive_height=True)
        sc = MDScrollView()
        sc.add_widget(self.list_box)
        root.add_widget(sc)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.2)

    def _on_search(self, inst, val):
        self._search = (val or "").strip().lower()
        Clock.unschedule(self._debounced)
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.25)

    def _debounced(self, *a): pass

    def _set_phase(self, ph):
        self._filter_phase = ph
        self.refresh_list()

    def refresh_list(self):
        self.list_box.clear_widgets()
        app = MDApp.get_running_app()
        cols = app.get_colors()
        self.md_bg_color = hex_to_rgba(cols["bg"])
        term = self._search
        done = set(app.db.load_progress().get("completed_missions",[]))
        shown = 0
        for m in self._all_missions:
            if self._filter_phase != "ALL" and m["_phase"] != self._filter_phase:
                continue
            hay = f"{m['id']} {m['name']} {m.get('description','')} {' '.join(m.get('exercises',[]))}".lower()
            if term and term not in hay:
                continue
            # card
            card = MDCard(orientation="vertical", padding=dp(12), spacing=dp(6), size_hint_y=None, height=dp(112), style="elevated")
            card.md_bg_color = hex_to_rgba(cols["card"])
            card.bind(on_release=lambda x, mm=m: self._open_detail(mm))
            # ripple via on_release works on MDCard
            top = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(22))
            # level badge
            lvl = m.get("level") or m.get("required_level") or "M"
            badge = MDCard(style="filled", size_hint=(None,None), size=(dp(28),dp(20)), radius=[dp(6)])
            badge.md_bg_color = hex_to_rgba(LEVEL_COLORS.get(lvl, "#9E9E9E"))
            badge.add_widget(MDLabel(text=lvl, halign="center", valign="center", font_style="Label", role="small", theme_text_color="Custom", text_color=(1,1,1,1)))
            top.add_widget(badge)
            top.add_widget(MDLabel(text=m["id"], font_style="Label", role="medium", size_hint_x=None, width=dp(52)))
            top.add_widget(MDLabel(text=m["name"], font_style="Title", role="small", size_hint_x=1))
            top.add_widget(MDLabel(text="✓" if m["id"] in done else "", font_style="Title", role="small", theme_text_color="Custom", text_color=hex_to_rgba(app.get_accent()), size_hint_x=None, width=dp(18)))
            card.add_widget(top)
            card.add_widget(MDLabel(text=m.get("description","")[:110], font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_y=None, height=dp(32)))
            card.add_widget(MDLabel(text=f"{len(m.get('exercises',[]))} exercícios • {m.get('duration','--')} • {m.get('type','DC')}", font_style="Label", role="small", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_y=None, height=dp(14)))
            self.list_box.add_widget(card)
            shown += 1
        if shown == 0:
            self.list_box.add_widget(MDLabel(text="Nenhuma missão encontrada.", halign="center", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_y=None, height=dp(40)))

    def _open_detail(self, mission):
        app = MDApp.get_running_app()
        cols = app.get_colors()
        accent = app.get_accent()
        lvl = mission.get("level") or mission.get("required_level") or "M"
        lvl_title, lvl_desc = LEVEL_OFICIAL.get(lvl, LEVEL_OFICIAL.get(lvl.upper(), ("Nível "+lvl, "")))
        done = mission["id"] in app.db.load_progress().get("completed_missions", [])

        # Build content
        content = MDBoxLayout(orientation="vertical", spacing=dp(8), adaptive_height=True, padding=[dp(4),dp(4),dp(4),dp(4)])

        # Header inside dialog
        content.add_widget(MDLabel(text=f"{mission['id']} — {mission['name']}", font_style="Title", role="medium", size_hint_y=None, height=dp(22)))
        content.add_widget(MDLabel(text=mission.get("description",""), font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_y=None, height=dp(36)))
        # level row
        lvl_row = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(28))
        badge2 = MDCard(style="filled", size_hint=(None,None), size=(dp(34),dp(22)), radius=[dp(6)], on_release=lambda x: show_dialog(app, lvl_title, lvl_desc))
        badge2.md_bg_color = hex_to_rgba(LEVEL_COLORS.get(lvl, "#9E9E9E"))
        badge2.add_widget(MDLabel(text=lvl, halign="center", theme_text_color="Custom", text_color=(1,1,1,1), font_style="Label", role="small"))
        lvl_row.add_widget(badge2)
        lvl_row.add_widget(MDLabel(text=lvl_title, font_style="Label", role="small", size_hint_x=1))
        lvl_row.add_widget(MDLabel(text=lvl_desc[:60]+"…", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_x=1))
        content.add_widget(lvl_row)

        # toggle done button
        btn_done = MDButton(style="filled", size_hint_y=None, height=dp(36))
        btn_done.md_bg_color = hex_to_rgba(accent if not done else "#4CAF50")
        btn_done.add_widget(MDButtonText(text="Marcar concluída" if not done else "✓ Concluída — tocar para desfazer"))
        def toggle(*a):
            is_done = app.db.toggle_mission_complete(mission["id"])
            btn_done.children[0].text = "✓ Concluída" if is_done else "Marcar concluída"
            self.refresh_list()
            try: MDApp.get_running_app().get_screen("dashboard").refresh()
            except: pass
        btn_done.bind(on_release=toggle)
        content.add_widget(btn_done)

        content.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
        content.add_widget(MDLabel(text="Exercícios — toque no nível para ver cobrança e dica", font_style="Title", role="small", size_hint_y=None, height=dp(18)))

        # exercises list
        for ex in mission.get("exercises", []):
            row = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(36), padding=[0,dp(2),0,dp(2)])
            row.add_widget(MDLabel(text="• "+ex, font_style="Body", role="small", size_hint_x=1))
            # level chip clickable
            chip = MDCard(style="filled", size_hint=(None,None), size=(dp(28),dp(22)), radius=[dp(6)])
            chip.md_bg_color = hex_to_rgba(LEVEL_COLORS.get(lvl, "#9E9E9E"))
            chip.add_widget(MDLabel(text=lvl, halign="center", theme_text_color="Custom", text_color=(1,1,1,1), font_style="Label", role="small"))
            # capture ex
            def make_popup(chip_inst, ex_name=ex, level=lvl):
                t, d = LEVEL_OFICIAL.get(level, LEVEL_OFICIAL.get(level.upper(), (level, "")))
                # detect quem executa
                low = ex_name.lower()
                quem = ""
                if "realizada pelo in" in low and "al acompanha" in low:
                    quem = "IN demonstra, AL acompanha."
                elif "realizada pelo in" in low:
                    quem = "Exercício demonstrado pelo IN."
                elif "realizada pelo al" in low or "realizado pelo al" in low:
                    quem = "AL executa, IN supervisiona."
                fase = mission["id"].split("-")[0]
                fase_txt = {"PS":"Pré-Solo","AP":"Aperfeiçoamento","NV":"Navegação","NOT":"Noturno"}.get(fase, fase)
                sop_txt = self._sop_ex.get(ex_name.lower()) or self._sop_ex.get(ex_name.lower().split("–")[0].strip()) or ""
                # fallback partial
                if not sop_txt:
                    for k, v in self._sop_ex.items():
                        if k in low or low[:18] in k:
                            sop_txt = v; break
                err, tip = find_exercise_help(ex_name)
                body = f"{t}: {d}\n{quem}\nFase {fase_txt} — ficha exige grau ≥3.\n\nSOP: {sop_txt[:260] + ('…' if len(sop_txt)>260 else '') if sop_txt else 'Consulte o SOP da seção correspondente.'}\n\nErros comuns: {err}\nDica: {tip}"
                show_dialog(app, f"{ex_name}  [{level}]", body)
            chip.bind(on_release=make_popup)
            row.add_widget(chip)
            content.add_widget(row)

        content.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
        # SOP snippet if any
        if self._sop_ex:
            # show first matching
            pass

        # Wrap in scroll
        sc = MDScrollView(size_hint_y=None, height=dp(420))
        sc.add_widget(content)

        global _dialog
        try:
            if _dialog: _dialog.dismiss()
        except: pass
        _dialog = MDDialog(
            MDDialogHeadlineText(text=f"{mission['id']} — Detalhe"),
            MDDialogSupportingText(text=f"{mission.get('duration','')} • {mission.get('type','')} • {len(mission.get('exercises',[]))} exercícios"),
            MDDialogContentContainer(sc, orientation="vertical"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Fechar"), style="text", on_release=lambda x: _dialog.dismiss()),
                spacing="8dp",
            ),
            size_hint=(0.95, None),
        )
        _dialog.open()

    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.1)

# ---------------------------------------------------------------------------
# Central de Estudos
# ---------------------------------------------------------------------------
class StudyCenterScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "study"
        self.md_bg_color = hex_to_rgba(DARK["bg"])
        self._data = load_json("data/missions.json", {"maneuvers":{"basic":[],"navigation":[]},"phases":{}})
        self._cat = "all"
        self._search = ""
        self._build()

    def _build(self):
        root = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(12),dp(8),dp(12),dp(0)])
        root.add_widget(MDLabel(text="Central de Estudos", font_style="Headline", role="small", size_hint_y=None, height=dp(28)))
        root.add_widget(MDLabel(text="Manobras por categoria • toque para passo-a-passo", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(16)))
        self.search_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(48))
        self.search_field.hint_text = "Buscar manobra... ex: estol, pouso, navegação"
        self.search_field.bind(text=self._on_search)
        root.add_widget(self.search_field)
        # cats
        cats = MDBoxLayout(spacing=dp(6), size_hint_y=None, height=dp(34))
        for label, key in [("Todas","all"),("Básico","basic"),("Navegação","navigation")]:
            b = MDButton(style="outlined", size_hint_x=None, width=dp(92), height=dp(32), on_release=lambda x, k=key: self._set_cat(k))
            b.add_widget(MDButtonText(text=label))
            cats.add_widget(b)
        root.add_widget(cats)
        self.list_box = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=[0,0,0,dp(88)], adaptive_height=True)
        sc = MDScrollView()
        sc.add_widget(self.list_box)
        root.add_widget(sc)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.2)

    def _on_search(self, inst, val):
        self._search = (val or "").lower()
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.25)

    def _set_cat(self, c):
        self._cat = c
        self.refresh_list()

    def refresh_list(self):
        self.list_box.clear_widgets()
        cols = MDApp.get_running_app().get_colors()
        self.md_bg_color = hex_to_rgba(cols["bg"])
        mans = []
        if self._cat in ("all","basic"): mans.extend(self._data.get("maneuvers",{}).get("basic",[]))
        if self._cat in ("all","navigation"): mans.extend(self._data.get("maneuvers",{}).get("navigation",[]))
        term = self._search.strip()
        if term:
            mans = [m for m in mans if term in m.get("name","").lower() or term in m.get("description","").lower() or term in " ".join(m.get("steps",[])).lower()]
        if not mans:
            self.list_box.add_widget(MDLabel(text="Nenhuma manobra encontrada.", halign="center", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_y=None, height=dp(40)))
            return
        for m in mans:
            card = MDCard(orientation="vertical", padding=dp(12), spacing=dp(4), size_hint_y=None, height=dp(88), style="elevated", on_release=lambda x, mm=m: self._show_detail(mm))
            card.md_bg_color = hex_to_rgba(cols["card"])
            card.add_widget(MDLabel(text=m.get("name","Manobra"), font_style="Title", role="small", size_hint_y=None, height=dp(18)))
            card.add_widget(MDLabel(text=m.get("description","")[:120], font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_y=None, height=dp(32)))
            card.add_widget(MDLabel(text=f"{len(m.get('steps',[]))} passos • toque para abrir →", font_style="Label", role="small", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_y=None, height=dp(14)))
            self.list_box.add_widget(card)

    def _show_detail(self, m):
        app = MDApp.get_running_app()
        steps = m.get("steps", [])
        body = m.get("description","") + "\n\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
        if not steps:
            body = m.get("description","Sem passos cadastrados.")
        show_dialog(app, m.get("name","Manobra"), body[:900] + ("…" if len(body)>900 else ""))

    def on_enter(self, *a):
        self.refresh_list()

# ---------------------------------------------------------------------------
# QRH / Manuais
# ---------------------------------------------------------------------------
class ManualsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "manuals"
        self.md_bg_color = hex_to_rgba(DARK["bg"])
        self._data = load_json("data/manuals.json", {"aircraft":[]})
        self._selected = 0
        self._build()

    def _build(self):
        root = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(12),dp(8),dp(12),dp(0)])
        root.add_widget(MDLabel(text="QRH / Manuais", font_style="Headline", role="small", size_hint_y=None, height=dp(28)))
        root.add_widget(MDLabel(text="Toque na aeronave para QRH completo", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(16)))
        # aircraft chips horizontal scroll
        self.chip_box = MDBoxLayout(spacing=dp(6), size_hint_y=None, height=dp(36), adaptive_width=True)
        chip_sc = MDScrollView(size_hint_y=None, height=dp(40), do_scroll_y=False)
        chip_sc.add_widget(self.chip_box)
        root.add_widget(chip_sc)
        # detail scroll
        self.detail_box = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=[0,0,0,dp(88)], adaptive_height=True)
        sc = MDScrollView()
        sc.add_widget(self.detail_box)
        root.add_widget(sc)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self.refresh_chips(), 0.2)

    def refresh_chips(self):
        self.chip_box.clear_widgets()
        acs = self._data.get("aircraft", [])
        cols = MDApp.get_running_app().get_colors()
        self.md_bg_color = hex_to_rgba(cols["bg"])
        accent = MDApp.get_running_app().get_accent()
        for idx, ac in enumerate(acs):
            btn = MDButton(style="filled" if idx==self._selected else "outlined", size_hint_x=None, width=dp(128), height=dp(32), on_release=lambda x, i=idx: self._select(i))
            if idx==self._selected:
                btn.md_bg_color = hex_to_rgba(accent)
            btn.add_widget(MDButtonText(text=ac.get("icao", ac.get("name",""))[:14]))
            self.chip_box.add_widget(btn)
        self._show_aircraft(self._selected)

    def _select(self, idx):
        self._selected = idx
        self.refresh_chips()

    def _show_aircraft(self, idx):
        self.detail_box.clear_widgets()
        acs = self._data.get("aircraft", [])
        if not acs or idx >= len(acs):
            return
        ac = acs[idx]
        cols = MDApp.get_running_app().get_colors()
        accent = MDApp.get_running_app().get_accent()
        # overview card
        c0 = MDCard(orientation="vertical", padding=dp(14), spacing=dp(6), style="elevated", size_hint_y=None, height=dp(96))
        c0.md_bg_color = hex_to_rgba(cols["card"])
        c0.add_widget(MDLabel(text=ac.get("name",""), font_style="Title", role="medium", size_hint_y=None, height=dp(20)))
        c0.add_widget(MDLabel(text=ac.get("role",""), font_style="Label", role="small", theme_text_color="Custom", text_color=hex_to_rgba(accent), size_hint_y=None, height=dp(16)))
        c0.add_widget(MDLabel(text=ac.get("overview","")[:180], font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_y=None, height=dp(36)))
        self.detail_box.add_widget(c0)
        # specs
        specs = ac.get("specs", {})
        if specs:
            self.detail_box.add_widget(MDLabel(text="Especificações", font_style="Title", role="small", size_hint_y=None, height=dp(20)))
            for k, v in specs.items():
                row = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(22))
                row.add_widget(MDLabel(text=k, font_style="Label", role="small", size_hint_x=0.45))
                row.add_widget(MDLabel(text=str(v), font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"]), size_hint_x=0.55))
                self.detail_box.add_widget(row)
        # limitations
        lims = ac.get("limitations", {})
        if lims:
            self.detail_box.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
            self.detail_box.add_widget(MDLabel(text="Limitações (KIAS)", font_style="Title", role="small", size_hint_y=None, height=dp(20)))
            for k, v in lims.items():
                row = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(22))
                row.add_widget(MDLabel(text=k, font_style="Label", role="small", size_hint_x=0.55))
                row.add_widget(MDLabel(text=str(v), font_style="Body", role="small", size_hint_x=0.45, halign="right"))
                self.detail_box.add_widget(row)
        # normal procedures
        procs = ac.get("normal_procedures", [])
        if procs:
            self.detail_box.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
            self.detail_box.add_widget(MDLabel(text="Procedimentos normais", font_style="Title", role="small", size_hint_y=None, height=dp(20)))
            for p in procs:
                self.detail_box.add_widget(MDLabel(text="▸ "+p.get("title",""), font_style="Label", role="medium", theme_text_color="Custom", text_color=hex_to_rgba(accent), size_hint_y=None, height=dp(18)))
                for step in p.get("checklist", []):
                    self.detail_box.add_widget(MDLabel(text="  • "+step, font_style="Body", role="small", size_hint_y=None, height=dp(18)))
        # QRH
        qrh = ac.get("qrh", [])
        if qrh:
            self.detail_box.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
            self.detail_box.add_widget(MDLabel(text="QRH — Emergências", font_style="Title", role="small", theme_text_color="Custom", text_color=hex_to_rgba("#EF4444"), size_hint_y=None, height=dp(20)))
            for q in qrh:
                card = MDCard(orientation="vertical", padding=dp(10), spacing=dp(4), style="outlined", size_hint_y=None, adaptive_height=True)
                card.md_bg_color = hex_to_rgba(cols["card"])
                card.add_widget(MDLabel(text=q.get("title",""), font_style="Label", role="medium", size_hint_y=None, height=dp(18)))
                if q.get("memory"):
                    card.add_widget(MDLabel(text="MEMORY ITEMS", font_style="Label", role="small", theme_text_color="Custom", text_color=hex_to_rgba("#EF4444"), size_hint_y=None, height=dp(14)))
                for s in q.get("steps", []):
                    card.add_widget(MDLabel(text="• "+s, font_style="Body", role="small", size_hint_y=None, height=dp(18)))
                self.detail_box.add_widget(card)
        # performance
        perf = ac.get("performance", {})
        if perf:
            self.detail_box.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
            self.detail_box.add_widget(MDLabel(text="Performance", font_style="Title", role="small", size_hint_y=None, height=dp(20)))
            for k, v in perf.items():
                row = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(22))
                row.add_widget(MDLabel(text=k, font_style="Label", role="small", size_hint_x=0.5))
                row.add_widget(MDLabel(text=str(v), font_style="Body", role="small", size_hint_x=0.5, halign="right"))
                self.detail_box.add_widget(row)

    def on_enter(self, *a):
        self.refresh_chips()

# ---------------------------------------------------------------------------
# SOP
# ---------------------------------------------------------------------------
class SOPScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "sop"
        self.md_bg_color = hex_to_rgba(DARK["bg"])
        self._data = load_json("data/sop.json", {})
        self._search = ""
        self._selected = list(self._data.keys())[0] if self._data else None
        self._build()

    def _build(self):
        root = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(12),dp(8),dp(12),dp(0)])
        root.add_widget(MDLabel(text="SOP — Standard Operating Procedures", font_style="Headline", role="small", size_hint_y=None, height=dp(28)))
        root.add_widget(MDLabel(text=f"{len(self._data)} seções • ACP 2023 • P-56C Paulistinha", font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(16)))
        self.search_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(48))
        self.search_field.hint_text = "Buscar no SOP... ex: decolagem, estol, pane"
        self.search_field.bind(text=self._on_search)
        root.add_widget(self.search_field)
        # split lists
        body = MDBoxLayout(spacing=dp(8))
        # left list
        self.left_box = MDBoxLayout(orientation="vertical", spacing=dp(6), adaptive_height=True, padding=[0,0,0,dp(88)])
        left_sc = MDScrollView(size_hint_x=0.42)
        left_sc.add_widget(self.left_box)
        # right detail
        self.right_box = MDBoxLayout(orientation="vertical", spacing=dp(8), adaptive_height=True, padding=[dp(8),dp(8),dp(8),dp(88)])
        right_sc = MDScrollView(size_hint_x=0.58)
        right_sc.add_widget(self.right_box)
        body.add_widget(left_sc)
        body.add_widget(right_sc)
        root.add_widget(body)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self.refresh_lists(), 0.2)

    def _on_search(self, inst, val):
        self._search = (val or "").lower()
        Clock.schedule_once(lambda dt: self.refresh_lists(), 0.25)

    def refresh_lists(self):
        self.left_box.clear_widgets()
        cols = MDApp.get_running_app().get_colors()
        accent = MDApp.get_running_app().get_accent()
        self.md_bg_color = hex_to_rgba(cols["bg"])
        term = self._search.strip()
        sections = list(self._data.keys())
        if term:
            sections = [s for s in sections if term in s.lower() or term in str(self._data[s]).lower()]
        if not sections:
            self.left_box.add_widget(MDLabel(text="Nenhuma seção.", halign="center", theme_text_color="Custom", text_color=hex_to_rgba(cols["sub"])))
            self.right_box.clear_widgets()
            return
        if self._selected not in sections:
            self._selected = sections[0]
        for sec in sections:
            card = MDCard(padding=dp(8), size_hint_y=None, height=dp(44), style="filled" if sec==self._selected else "outlined", on_release=lambda x, s=sec: self._select(s))
            card.md_bg_color = hex_to_rgba(accent if sec==self._selected else cols["card"])
            lbl = MDLabel(text=sec[:34], font_style="Label", role="small", theme_text_color="Custom", text_color=(1,1,1,1) if sec==self._selected else hex_to_rgba(cols["text"]), size_hint_y=None, height=dp(28))
            card.add_widget(lbl)
            self.left_box.add_widget(card)
        self._show_detail(self._selected)

    def _select(self, sec):
        self._selected = sec
        self.refresh_lists()

    def _show_detail(self, sec):
        self.right_box.clear_widgets()
        if not sec or sec not in self._data:
            return
        cols = MDApp.get_running_app().get_colors()
        txt = str(self._data[sec])
        self.right_box.add_widget(MDLabel(text=sec, font_style="Title", role="medium", size_hint_y=None, height=dp(22)))
        self.right_box.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
        # split by sentences for readability
        self.right_box.add_widget(MDLabel(text=txt, font_style="Body", role="small", theme_text_color="Custom", text_color=hex_to_rgba(cols["text"]), adaptive_height=True))

    def on_enter(self, *a):
        self.refresh_lists()

# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------
class SettingsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.md_bg_color = hex_to_rgba(DARK["bg"])
        self._build()

    def _build(self):
        root_box = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=[dp(16),dp(12),dp(16),dp(0)], adaptive_height=True)
        root_box.add_widget(MDLabel(text="Configurações", font_style="Headline", role="small", size_hint_y=None, height=dp(28)))

        # perfil
        root_box.add_widget(MDLabel(text="Perfil", font_style="Title", role="small", size_hint_y=None, height=dp(20)))
        self.name_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(52))
        self.name_field.hint_text = "Nome de exibição"
        root_box.add_widget(self.name_field)
        self.school_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(52))
        self.school_field.hint_text = "Escola / Aeroclube"
        root_box.add_widget(self.school_field)
        save_btn = MDButton(style="filled", size_hint_y=None, height=dp(40), on_release=lambda x: self._save_profile())
        save_btn.add_widget(MDButtonText(text="Salvar perfil"))
        root_box.add_widget(save_btn)

        root_box.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
        # tema
        root_box.add_widget(MDLabel(text="Tema", font_style="Title", role="small", size_hint_y=None, height=dp(20)))
        self.theme_row = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(40))
        self.btn_dark = MDButton(style="filled", size_hint_x=0.5, height=dp(36), on_release=lambda x: self._set_theme("dark"))
        self.btn_dark.add_widget(MDButtonText(text="🌙  Escuro"))
        self.btn_light = MDButton(style="outlined", size_hint_x=0.5, height=dp(36), on_release=lambda x: self._set_theme("light"))
        self.btn_light.add_widget(MDButtonText(text="☀️  Claro"))
        self.theme_row.add_widget(self.btn_dark); self.theme_row.add_widget(self.btn_light)
        root_box.add_widget(self.theme_row)

        # accents
        root_box.add_widget(MDLabel(text="Cor de destaque (8 opções)", font_style="Title", role="small", size_hint_y=None, height=dp(20)))
        self.accent_grid = MDBoxLayout(orientation="vertical", spacing=dp(8), adaptive_height=True)
        # build 2 rows of 4
        row1 = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(56))
        row2 = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(56))
        aids = list(ACCENTS.keys())
        for i, aid in enumerate(aids):
            info = ACCENTS[aid]
            card = MDCard(padding=dp(6), style="elevated", size_hint_x=1, on_release=lambda x, a=aid: self._set_accent(a))
            card.md_bg_color = hex_to_rgba(info["color"])
            card.add_widget(MDLabel(text=info["name"], halign="center", font_style="Label", role="small", theme_text_color="Custom", text_color=(1,1,1,1)))
            (row1 if i<4 else row2).add_widget(card)
        self.accent_grid.add_widget(row1); self.accent_grid.add_widget(row2)
        root_box.add_widget(self.accent_grid)

        root_box.add_widget(MDDivider(size_hint_y=None, height=dp(1)))
        root_box.add_widget(MDLabel(text="© Guayanaz Systems • ProPilot Mobile v2.0", font_style="Body", role="small", halign="center", theme_text_color="Custom", text_color=hex_to_rgba(DARK["sub"]), size_hint_y=None, height=dp(20)))
        root_box.add_widget(MDBoxLayout(size_hint_y=None, height=dp(88)))

        sc = MDScrollView()
        sc.add_widget(root_box)
        self.add_widget(sc)
        Clock.schedule_once(lambda dt: self.refresh(), 0.3)

    def refresh(self):
        app = MDApp.get_running_app()
        cols = app.get_colors()
        self.md_bg_color = hex_to_rgba(cols["bg"])
        sett = app.db.load_settings()
        self.name_field.text = sett.get("display_name","")
        self.school_field.text = sett.get("school","")
        # theme buttons
        cur = sett.get("theme","dark")
        accent = app.get_accent()
        if cur == "dark":
            self.btn_dark.style = "filled"; self.btn_dark.md_bg_color = hex_to_rgba(accent)
            self.btn_light.style = "outlined"
        else:
            self.btn_light.style = "filled"; self.btn_light.md_bg_color = hex_to_rgba(accent)
            self.btn_dark.style = "outlined"

    def _save_profile(self):
        app = MDApp.get_running_app()
        name = self.name_field.text.strip() or "Piloto-Aluno"
        school = self.school_field.text.strip() or "Aeroclube de Pirassununga"
        app.db.update_profile(display_name=name, school=school)
        try: app.get_screen("dashboard").refresh()
        except: pass
        show_dialog(app, "Perfil salvo", f"Nome: {name}\nEscola: {school}")

    def _set_theme(self, t):
        app = MDApp.get_running_app()
        app.set_theme(t)
        self.refresh()
        try: app.get_screen("dashboard").refresh()
        except: pass

    def _set_accent(self, aid):
        app = MDApp.get_running_app()
        app.set_accent(aid)
        self.refresh()

    def on_enter(self, *a):
        self.refresh()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
class ProPilotMobileApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "ProPilot"
        # importar database
        try:
            from database import get_database
            self.db = get_database()
        except ImportError:
            import database as _db
            self.db = _db.get_database()
        self._accent = self.db.load_settings().get("accent","spotify")
        self._theme_name = self.db.load_settings().get("theme","dark")

    def get_accent(self):
        return ACCENTS.get(self._accent, ACCENTS["spotify"])["color"]

    def get_colors(self):
        return DARK if self._theme_name == "dark" else LIGHT

    def set_theme(self, t):
        if t not in ("dark","light"): return
        self._theme_name = t
        s = self.db.load_settings(); s["theme"]=t; self.db.save_settings(s)
        self.theme_cls.theme_style = "Dark" if t=="dark" else "Light"
        # refresh all screens
        for scr in self.sm.screens:
            try: scr.refresh()
            except: pass
            try: scr.refresh_list()
            except: pass
            try: scr.refresh_chips()
            except: pass
            try: scr.refresh_lists()
            except: pass
        self._apply_window_bg()

    def set_accent(self, aid):
        if aid not in ACCENTS: return
        self._accent = aid
        s = self.db.load_settings(); s["accent"]=aid; self.db.save_settings(s)
        self.theme_cls.primary_palette = "Green"  # keep valid
        # update custom accent usage
        for scr in self.sm.screens:
            try: scr.refresh()
            except: pass

    def _apply_window_bg(self):
        Window.clearcolor = hex_to_rgba(self.get_colors()["bg"])

    def build(self):
        self.theme_cls.theme_style = "Dark" if self._theme_name=="dark" else "Light"
        self.theme_cls.primary_palette = "Green"
        self._apply_window_bg()

        self.sm = MDScreenManager()

        self.dashboard = DashboardScreen()
        self.missions = MissionsScreen()
        self.study = StudyCenterScreen()
        self.manuals = ManualsScreen()
        self.sop = SOPScreen()
        self.settings = SettingsScreen()

        for scr in [self.dashboard, self.missions, self.study, self.manuals, self.sop, self.settings]:
            self.sm.add_widget(scr)

        # Root with ScreenManager + Bottom Navigation Bar
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(self.sm)

        # Bottom nav bar (custom, reliable across KivyMD versions)
        nav = MDBoxLayout(size_hint_y=None, height=dp(64), padding=[0,dp(4),0,dp(4)], spacing=0)
        # use card bg
        nav.md_bg_color = hex_to_rgba(self.get_colors()["card"])
        self._nav_bar = nav
        self._nav_items = []
        items = [
            ("view-dashboard","Início","dashboard"),
            ("airplane","Missões","missions"),
            ("book-open-variant","Estudos","study"),
            ("file-document","QRH","manuals"),
            ("script-text","SOP","sop"),
            ("cog","Ajustes","settings"),
        ]
        for icon, label, key in items:
            btn_box = MDBoxLayout(orientation="vertical", spacing=0, padding=[dp(2),dp(2),dp(2),dp(2)])
            ib = MDIconButton(icon=icon, size_hint_y=None, height=dp(32), pos_hint={"center_x":0.5})
            ib.bind(on_release=lambda x, k=key: self.switch_to(k))
            lbl = MDLabel(text=label, halign="center", font_style="Label", role="small", size_hint_y=None, height=dp(16))
            btn_box.add_widget(ib); btn_box.add_widget(lbl)
            # keep refs for highlight
            self._nav_items.append((key, ib, lbl, btn_box))
            nav.add_widget(btn_box)
        root.add_widget(nav)
        self._highlight_nav("dashboard")
        Clock.schedule_once(lambda dt: self._highlight_nav("dashboard"), 0.4)
        return root

    def switch_to(self, key):
        self.sm.current = key
        self._highlight_nav(key)
        # trigger refresh
        try:
            scr = self.sm.get_screen(key)
            if hasattr(scr, "refresh"): scr.refresh()
            if hasattr(scr, "refresh_list"): scr.refresh_list()
            if hasattr(scr, "refresh_chips"): scr.refresh_chips()
            if hasattr(scr, "refresh_lists"): scr.refresh_lists()
        except: pass

    def _highlight_nav(self, active):
        accent = self.get_accent()
        cols = self.get_colors()
        self._nav_bar.md_bg_color = hex_to_rgba(cols["card"])
        for key, ib, lbl, box in self._nav_items:
            is_active = key == active
            ib.theme_text_color = "Custom"
            ib.text_color = hex_to_rgba(accent if is_active else cols["sub"])
            lbl.theme_text_color = "Custom"
            lbl.text_color = hex_to_rgba(accent if is_active else cols["sub"])

    def get_screen(self, name):
        return self.sm.get_screen(name)

if __name__ == "__main__":
    ProPilotMobileApp().run()
