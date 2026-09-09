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

LEVEL_LABELS = {"E":"Excelência","A":"Aplicação","C":"Compreensão","M":"Memorização","X":"Excelência Total","a":"Aplicação (aux)","c":"Compreensão (aux)"}
LEVEL_COLORS = {"E":"#1DB954","A":"#3B82F6","C":"#F59E0B","M":"#95a5a6","X":"#8B5CF6","a":"#3B82F6","c":"#F59E0B"}

LEVEL_OFICIAL = {
    "M": ("M — Memorização", "Conhecer e memorizar a sequência. O IN demonstra e o aluno acompanha. Não se exige execução autônoma. Foco em nomenclatura e checklist."),
    "C": ("C — Compreensão", "Executar COM auxílio direto do IN. O aluno age, mas o IN intervém e corrige. Demonstra compreensão da técnica."),
    "A": ("A — Aplicação", "Executar com supervisão mínima. O AL realiza sozinho, IN apenas acompanha e intervém se necessário. Erros pequenos tolerados."),
    "E": ("E — Execução", "Executar de forma autônoma e correta. Sem auxílio. Padrão de segurança e precisão já próximo ao solo."),
    "X": ("X — Excelência", "Domínio total. Execução perfeita, dentro dos parâmetros, apto a voo solo e cheque (PS-X1/X2). Sem intervenção."),
}
# Fallback para minúsculas
LEVEL_OFICIAL["a"] = LEVEL_OFICIAL["A"]
LEVEL_OFICIAL["c"] = LEVEL_OFICIAL["C"]
LEVEL_OFICIAL["m"] = LEVEL_OFICIAL["M"]

def _official_charge(ex_name: str, level: str, mission_id: str) -> str:
    lvl_key = level.strip() if level.strip() in LEVEL_OFICIAL else level.strip().upper()
    title, desc = LEVEL_OFICIAL.get(lvl_key, (f"{level} — Nível exigido", "Executar conforme quadro de missões."))
    # Detecta quem executa pelo texto do exercício
    ex_low = ex_name.lower()
    quem = ""
    if "realizada pelo in" in ex_low and "al acompanha" in ex_low:
        quem = "Nesta missão o IN demonstra e o AL acompanha (familiarização)."
    elif "realizada pelo in" in ex_low:
        quem = "Nesta missão o exercício é demonstrado/executado pelo IN."
    elif "realizada pelo al" in ex_low:
        quem = "Nesta missão o AL executa e o IN apenas acompanha/supervisiona."
    elif "realizado pelo al" in ex_low:
        quem = "Nesta missão o AL executa com supervisão mínima."
    # Fase
    fase = mission_id.split("-")[0] if "-" in mission_id else ""
    fase_txt = {"PS":"Pré-Solo","AP":"Aperfeiçoamento","NV":"Navegação","NOT":"Noturno"}.get(fase, fase)
    return f"{title}: {desc} {quem} Cobrança oficial do Programa de Instrução {fase_txt} — ficha de voo exige grau ≥3 em cada exercício; grau 1 (Perigoso) ou 2 (Deficiente) reprova a missão. Nível '{level}' deve constar na ficha como atingido."


# Dicionário de erros comuns e dicas por exercício (chave = trecho do nome)
EXERCISE_HELP = {
    "livro de bordo": (
        "Esquecer de conferir documentação; preencher horas errado; não levar headset/caneta.",
        "Chegue 15 min antes. Confira diário de bordo, horas de célula/motor e validade da IAM."
    ),
    "inspeção": (
        "Pular itens do checklist; não checar nível de óleo/combustível; ignorar calços.",
        "Siga o checklist externo→interno sem pressa. Toque e confirme cada item em voz alta."
    ),
    "partida do motor": (
        "Afogamento; hélice sem área livre; mistura/passo incorretos.",
        "Área livre, freio estacionado, mistura rica, chamada 'hélice livre' antes de acionar."
    ),
    "fraseologia": (
        "Falar rápido demais; esquecer prefixo; não colacionar autorizações.",
        "Use padrão ICAO: quem chama → quem é chamado → mensagem → colação. Fale pausado."
    ),
    "rolagem": ("Taxi rápido; freio brusco; não testar freios/bússola.",
        "Taxi lento (passo humano), teste freios nos primeiros metros, siga linha amarela."),
    "taxiamento": ("Taxi rápido; freio brusco; não testar freios/bússola.",
        "Taxi lento, teste freios, mantenha manche contra vento se houver."),
    "decolagem normal": (
        "Corrigir com freio em vez de leme; rotacionar cedo/tarde; esquecer compensador.",
        "Alinhe no eixo, potência suave, corrija só com pedais, rotacione em Vr (55-65 kt C152/C172)."
    ),
    "decolagem curta": (
        "Não usar flape recomendado; não travar freio para potência máxima.",
        "Flape conforme POH, freio aplicado, potência máxima, solte e mantenha Vx até obstáculo."
    ),
    "decolagem com obstáculo": (
        "Subida com velocidade errada (Vy vs Vx); recolher flape cedo.",
        "Mantenha Vx até livrar obstáculo, depois Vy. Só recolha flape com altura/velocidade seguras."
    ),
    "saída do tráfego": (
        "Curvar antes de 500 ft AGL; não informar saída na fonia.",
        "Mantenha rumo da pista até 500 ft, informe 'saindo do tráfego' e só então curve."
    ),
    "subida": (
        "Subida com nariz alto demais (baixa velocidade); não compensar.",
        "Mantenha Vy (melhor razão) e compense para voo mãos leves. Verifique temperatura do motor."
    ),
    "nivelamento": (
        "Nivelar brusco (vario negativo); esquecer de reduzir potência.",
        "Antecipe 10% da razão de subida antes da altitude, nivele, ajuste potência e compense."
    ),
    "identificação da área": (
        "Desorientar-se; não memorizar referências.",
        "Identifique estrada/rio/cidade de referência e memorize rumos de regresso."
    ),
    "uso dos comandos": (
        "Comandos bruscos; grip tenso; não coordenar pedais.",
        "Mãos leves, pressões suaves, coordene aileron+leme. Olhe horizonte, não só instrumentos."
    ),
    "uso do motor": (
        "Ajustes bruscos de potência; não checar mistura em altitude.",
        "Ajustes suaves, ajuste mistura para EGT/RPM conforme POH, monitore pressões."
    ),
    "compensador": (
        "Voar com força no manche; compensar em curva.",
        "Compense só em voo estabilizado, busque pressão zero no manche."
    ),
    "retas e curvas": (
        "Perder altitude em curva; curva descoordenada (esfera fora).",
        "Incline, mantenha altitude com leve pressão, esfera no centro com pedal."
    ),
    "voo nivelado": (
        "Altitude oscilando; não trimar.",
        "Ajuste atitude → potência → compensador. Voe por atitude, confirme no altímetro."
    ),
    "orientação": (
        "Confiar só em GPS; perderá referências visuais.",
        "Mantenha navegação por contato: compare carta com terreno a cada 2-3 min."
    ),
    "curvas de pequena": (
        "Inclinação errada (~15°); olhar só painel.",
        "Pequena = ~15° de inclinação, horizonte como referência, saída no rumo exato."
    ),
    "curvas de média": (
        "Perder altitude; inclinação >30° sem necessidade.",
        "Média = ~30°, adicione leve potência, mantenha esfera centrada."
    ),
    "voo em retângulo": (
        "Retângulo torto; não compensar vento.",
        "Cruze vento de través com correção de deriva, pernas paralelas a referência no solo."
    ),
    "estol": (
        "Recuperar com aileron; puxar manche na recuperação.",
        "Ao estol: nariz baixa, potência máxima, asas niveladas com pedal, saia do estol antes de curvar."
    ),
    "descida": (
        "Descida muito rápida; choque térmico no motor.",
        "Planeje descida 3° (~300 ft/NM), reduza potência gradualmente, mantenha velocidade."
    ),
    "circuito de tráfego": (
        "Perna base curta; altitude errada; não fazer checklist antes do pouso.",
        "Circuito retangular padrão 1000 ft AGL, GUMPS/checklist na perna contra o vento."
    ),
    "enquadramento": (
        "Final desalinhado; não corrigir deriva.",
        "Alinhe com eixo, corrija deriva com proa, mantenha rampa com potência."
    ),
    "aproximação final": (
        "Alta/baixa na rampa; velocidade instável.",
        "Mantenha velocidade de aproximação (65-70 kt), rampa com potência, eixo com leme/aileron."
    ),
    "pouso normal": (
        "Arredondamento alto (flare alto); olhar pista perto.",
        "Olhe para o fim da pista, flare suave a ~1m, corte de potência e toque no trem principal."
    ),
    "pouso curto": (
        "Aproximação longa; não usar ponto de toque preciso.",
        "Mire ponto preciso, aproximação estabilizada, toque com freio aerodinâmico e frenagem progressiva."
    ),
    "pouso de pista": (
        "Não manter eixo após toque; frear brusco.",
        "Mantenha eixo com leme, frenagem progressiva, flape recolhe só após dominar direção."
    ),
    "arremetida": (
        "Subir sem potência máxima; esquecer flape.",
        "Potência máxima, atitude de subida, flape recolhe em etapas, informe na fonia."
    ),
    "pane simulada": (
        "Demorar a baixar nariz; não escolher área.",
        "Nariz baixa imediato para velocidade de planeio, escolha área à frente, checklist de pane."
    ),
    "corrida após pouso": (
        "Sair da pista sem autorização; não livrar rápido.",
        "Mantenha velocidade até taxiway, só saia quando dominado e autorizado."
    ),
    "estacionamento": (
        "Não calçar/frear; hélice em posição errada.",
        "Freio estacionado, calços, corte conforme checklist, hélice horizontal se possível."
    ),
    "parada do motor": (
        "Cortar com motor quente/acelerado; esquecer magnetos.",
        "Resfrie 1-2 min em marcha lenta, teste magnetos, mistura corta, chaves off."
    ),
    "cheque de abandono": (
        "Deixar chave/bateria ligada; não fechar plano.",
        "Master off, chaves com responsável, feche plano de voo e registre no livro."
    ),
    "procedimentos após o pouso": (
        "Limpar pista devagar; esquecer transponder/flape.",
        "Livre pista rápido, transponder standby, flape recolhido, luzes conforme."
    ),
    "documentação": (
        "Peso e balanceamento errado; não conferir NOTAM.",
        "Confira peso/CG, autonomia, documentos da aeronave e NOTAM do aeródromo."
    ),
    "planejamento": (
        "Rota direta sobre área restrita; combustível justo.",
        "Trace rota evitando restritas, calcule combustível + 30 min reserva, alternativa."
    ),
    "meteorologia": (
        "Ignorar CB/vento de través limite; não checar TAF/METAR.",
        "Analise METAR/TAF, SIGMET, vento de través e teto. Tenha critério de cancelamento."
    ),
    "regras de tráfego": (
        "Entrar em controlada sem autorização; não ouvir ATIS.",
        "Ouça ATIS, peça autorização, mantenha escuta e níveis conforme classe do espaço."
    ),
    "navegação estimada": (
        "Não corrigir proa magnética/deriva; esquecer tempo estimado.",
        "Aplique declinação + deriva, marque ETO a cada perna, confirme com ponto visual."
    ),
    "navegação por contato": (
        "Perder-se por falta de pontos; não levar carta dobrada certa.",
        "Leve carta dobrada na perna atual, confirme pontos a cada 5 min."
    ),
    "reabastecimento": (
        "Abastecer com passageiro a bordo; não fazer aterramento.",
        "Desembarque todos, aterramento conectado, verifique tipo/quantidade de combustível."
    ),
    "pernoite": (
        "Não peiar/amarra; esquecer capa/pinos.",
        "Amarre nos três pontos, calços, capas de motor/hélice, feche portas."
    ),
    "cheques": ("Pular checklist; fazer de memória sem confirmar.",
        "Leia em voz alta e toque/confirme cada item. Nunca decore checklist crítico."),
}

def _help_for(ex_name: str):
    n = ex_name.lower()
    for key, (err, dica) in EXERCISE_HELP.items():
        if key in n:
            return err, dica
    return ("Falta de técnica ou esquecimento de checklist na fase Pré-Solo.", "Siga o POH/checklist da aeronave e repita a manobra com instrutor até automatizar.")


class MissionsView(ctk.CTkFrame):
    def __init__(self, parent, on_back: Callable=None, theme_manager=None):
        super().__init__(parent)
        self.on_back = on_back
        self.theme_manager = theme_manager
        from database import get_database
        self.db = get_database()
        self.missions_data = {}
        self.sop_data = {}
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
        # SOP exercicios
        try:
            sp = resource_path(os.path.join("data","sop_exercises.json"))
            if not os.path.exists(sp):
                sp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data","sop_exercises.json")
            with open(sp, encoding="utf-8") as f:
                self.sop_data = json.load(f)
        except Exception as e:
            # fallback tenta sop.json
            try:
                sp2 = resource_path(os.path.join("data","sop.json"))
                if not os.path.exists(sp2):
                    sp2 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data","sop.json")
                with open(sp2, encoding="utf-8") as f:
                    raw = json.load(f)
                    # converte para lower keys curtos
                    self.sop_data = {k.lower(): v for k,v in raw.items()}
            except:
                self.sop_data = {}
        self._build()

    def _sop_for(self, ex_name: str) -> str:
        if not getattr(self, "sop_data", None):
            return ""
        n = ex_name.lower()
    # tenta match exato ou parcial
        for key, txt in self.sop_data.items():
            if key in n or n in key:
                # limita tamanho
                t = txt.strip()
                if len(t) > 600:
                    t = t[:580] + "…"
                return t
    # fallback por palavra-chave
        for key, txt in self.sop_data.items():
            # primeira palavra
            first = key.split()[0] if key.split() else ""
            if first and first in n:
                t = txt.strip()
                if len(t) > 600:
                    t = t[:580] + "…"
                return t
        return ""

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
        self._ex_expanded = getattr(self, "_ex_expanded", {})
        for i, ex in enumerate(m.get("exercises",[]), 1):
            lvl = req.get(ex, m.get("required_level","M"))
            outer = ctk.CTkFrame(ex_box, fg_color=("gray92","gray18"), corner_radius=8)
            outer.pack(fill="x", padx=8, pady=3)
            outer.grid_columnconfigure(0, weight=1)
            row = ctk.CTkFrame(outer, fg_color="transparent")
            row.grid(row=0, column=0, sticky="ew", padx=4, pady=2)
            row.grid_columnconfigure(0, weight=1)
            idx = i; name = ex; level = lvl
            exp_key = f"{m['id']}_{idx}"
            is_open = self._ex_expanded.get(exp_key, False)
            arrow = "▼" if is_open else "▶"
            lbl = ctk.CTkLabel(row, text=f"{arrow}  {idx:02d}. {name}", font=ctk.CTkFont(size=12), anchor="w", justify="left", wraplength=300)
            lbl.grid(row=0, column=0, sticky="w", padx=6, pady=6)
            badge = ctk.CTkLabel(row, text=level, width=36, height=22, corner_radius=8, fg_color=LEVEL_COLORS.get(level, "#444"), text_color="white", font=ctk.CTkFont(weight="bold", size=11))
            badge.grid(row=0, column=1, padx=6)
            full = LEVEL_LABELS.get(level, level)
            ctk.CTkLabel(row, text=full, font=ctk.CTkFont(size=10), text_color=("gray45","gray60")).grid(row=0, column=2, padx=(0,6))
            ctk.CTkLabel(row, text="clique para dicas", font=ctk.CTkFont(size=9), text_color=("#1f538d","#4cc2ff")).grid(row=0, column=3, padx=4)
            detail = ctk.CTkFrame(outer, fg_color=("#fef9e7","#1e1a0a"), corner_radius=6, border_width=1, border_color=("#f0c040","#8a6d00"))
            if is_open:
                detail.grid(row=1, column=0, sticky="ew", padx=6, pady=(0,6))
                ctk.CTkLabel(detail, text="📋 O que é cobrado (documento oficial):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#1f538d", anchor="w").pack(anchor="w", padx=10, pady=(8,2))
                ctk.CTkLabel(detail, text=f"• {_official_charge(name, level, m['id'])}", wraplength=400, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=10, pady=(0,6))
                sop_txt = self._sop_for(name)
                if sop_txt:
                    ctk.CTkLabel(detail, text="📖 Procedimento SOP (ACP 2023 – P-56C Paulistinha):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#8e44ad", anchor="w").pack(anchor="w", padx=10, pady=(6,2))
                    ctk.CTkLabel(detail, text=f"• {sop_txt}", wraplength=400, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=10, pady=(0,6))
                err_txt, dica_txt = _help_for(name)
                ctk.CTkLabel(detail, text="⚠️ Erros comuns:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#c0392b", anchor="w").pack(anchor="w", padx=10, pady=(8,2))
                ctk.CTkLabel(detail, text=f"• {err_txt}", wraplength=400, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=10, pady=(0,4))
                ctk.CTkLabel(detail, text="💡 Dica:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#1f7a3a", anchor="w").pack(anchor="w", padx=10, pady=(4,2))
                ctk.CTkLabel(detail, text=f"• {dica_txt}", wraplength=400, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=10, pady=(0,8))
            def make_toggle(k=exp_key, o=outer, d=detail, ex_name=name, ii=idx, ll=lbl):
                def toggle(_e=None):
                    cur = self._ex_expanded.get(k, False)
                    self._ex_expanded[k] = not cur
                    if self._ex_expanded[k]:
                        d.grid(row=1, column=0, sticky="ew", padx=6, pady=(0,6))
                        if not d.winfo_children():
                            ctk.CTkLabel(d, text="📋 O que é cobrado (documento oficial):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#1f538d", anchor="w").pack(anchor="w", padx=10, pady=(8,2))
                            ctk.CTkLabel(d, text=f"• {_official_charge(ex_name, level, m['id'])}", wraplength=400, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=10, pady=(0,6))
                            sop2 = self._sop_for(ex_name)
                            if sop2:
                                ctk.CTkLabel(d, text="📖 Procedimento SOP (ACP 2023 – P-56C Paulistinha):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#8e44ad", anchor="w").pack(anchor="w", padx=10, pady=(6,2))
                                ctk.CTkLabel(d, text=f"• {sop2}", wraplength=400, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=10, pady=(0,6))
                            e, di = _help_for(ex_name)
                            ctk.CTkLabel(d, text="⚠️ Erros comuns:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#c0392b", anchor="w").pack(anchor="w", padx=10, pady=(8,2))
                            ctk.CTkLabel(d, text=f"• {e}", wraplength=400, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=10, pady=(0,4))
                            ctk.CTkLabel(d, text="💡 Dica:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#1f7a3a", anchor="w").pack(anchor="w", padx=10, pady=(4,2))
                            ctk.CTkLabel(d, text=f"• {di}", wraplength=400, justify="left", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=10, pady=(0,8))
                        ll.configure(text=f"▼  {ii:02d}. {ex_name}")
                    else:
                        d.grid_forget()
                        ll.configure(text=f"▶  {ii:02d}. {ex_name}")
                return toggle
            tog = make_toggle()
            for w in (row, lbl, badge, outer):
                w.bind("<Button-1>", tog)
                try: w.configure(cursor="hand2")
                except: pass
        # criterios
        crit = ctk.CTkFrame(self.right_scroll, fg_color=("#fff7cc","#2a2410"), border_width=1, border_color="#f1c40f"); crit.pack(fill="x", padx=6, pady=8)
        ctk.CTkLabel(crit, text="Criterios de aprovacao", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8,2))
        ctk.CTkLabel(crit, text="• Aprovado se obtiver Grau 3 (Satisfatorio) ou superior em TODOS os exercicios\n• Grau 1 (Perigoso) ou 2 (Deficiente) em qualquer exercicio = reprovado\n• Grau 4 = Bom  •  Grau 5 = Excelente\n• Revisao obrigatoria em caso de falha antes de progredir de fase.", justify="left", wraplength=420, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(0,10))
