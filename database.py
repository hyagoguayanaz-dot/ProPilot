"""
Database manager for Pro Pilot - persistência corrigida para .exe
- Em modo dev: usa ./data ao lado do código
- Em modo .exe (frozen): usa %LOCALAPPDATA%/ProPilot (persistente)
  e migra dados antigos de ./data se existirem
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

def _get_user_data_dir() -> Path:
    """Retorna diretório persistente gravável."""
    if getattr(sys, 'frozen', False):
        # Rodando como .exe PyInstaller
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "ProPilot"
    else:
        # Rodando como script python
        return Path(__file__).parent / "data"

class DatabaseManager:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = _get_user_data_dir()
        self.data_dir = Path(data_dir)
        self.progress_file = self.data_dir / "user_progress.json"
        self.settings_file = self.data_dir / "user_settings.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Migração: se estiver em modo frozen e existir ./data antigo com progresso, copia
        try:
            if getattr(sys, 'frozen', False):
                legacy = Path(__file__).parent / "data"
                # tenta também pasta ao lado do exe
                exe_dir = Path(sys.executable).parent / "data"
                for src_dir in [legacy, exe_dir]:
                    for fname in ["user_progress.json", "user_settings.json"]:
                        src = src_dir / fname
                        dst = self.data_dir / fname
                        if src.exists() and not dst.exists():
                            try:
                                dst.write_bytes(src.read_bytes())
                            except: pass
                # também tenta %APPDATA%/ProPilot antigo sem LOCAL
                alt = Path(os.environ.get("APPDATA","")) / "ProPilot" if os.environ.get("APPDATA") else None
                if alt and alt != self.data_dir and alt.exists():
                    for fname in ["user_progress.json", "user_settings.json"]:
                        src = alt / fname
                        dst = self.data_dir / fname
                        if src.exists() and not dst.exists():
                            try:
                                dst.write_bytes(src.read_bytes())
                            except: pass
        except: pass

        self._init_default_progress()
        self._init_default_settings()

    def _init_default_progress(self):
        default_progress = {
            "completed_missions": [],
            "mission_notes": {},
            "study_progress": {
                "PS": {"completed": 0, "total": 19, "exercises_mastered": []},
                "AP": {"completed": 0, "total": 10, "exercises_mastered": []},
                "NV": {"completed": 0, "total": 5, "exercises_mastered": []},
                "NOT": {"completed": 0, "total": 2, "exercises_mastered": []}
            },
            "last_updated": datetime.now().isoformat(),
            "profile": {
                "display_name": "Piloto-Aluno",
                "school": "Aeroclube de Pirassununga",
                "total_flight_hours": 0,
                "solo_hours": 0,
                "current_phase": "PS",
                "pilot_license_status": "student"
            }
        }
        if not self.progress_file.exists():
            self._save_progress(default_progress)
        else:
            # garante que arquivo existente tenha chaves novas (migração leve)
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                changed = False
                for k,v in default_progress.items():
                    if k not in existing:
                        existing[k] = v; changed=True
                # profile subkeys
                for pk, pv in default_progress["profile"].items():
                    if pk not in existing.get("profile",{}):
                        existing["profile"][pk] = pv; changed=True
                # migra totals para documento oficial (19/10/5/2)
                expected_totals = {"PS":19,"AP":10,"NV":5,"NOT":2}
                sp = existing.get("study_progress",{})
                for ph, exp in expected_totals.items():
                    if ph not in sp or sp[ph].get("total") != exp:
                        if ph not in sp:
                            sp[ph] = {"completed":0,"total":exp,"exercises_mastered":[]}
                        else:
                            sp[ph]["total"] = exp
                        changed=True
                existing["study_progress"] = sp
                if changed:
                    self._save_progress(existing)
            except: pass

    def _init_default_settings(self):
        default_settings = {
            "theme": "dark",
            "accent": "spotify",
            "language": "pt-BR",
            "notifications": True,
            "study_reminders": True,
            "display_name": "Piloto-Aluno",
            "school": "Aeroclube de Pirassununga"
        }
        if not self.settings_file.exists():
            self._save_settings(default_settings)
        else:
            # migracao: adiciona accent se faltar
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    s = json.load(f)
                if "accent" not in s:
                    s["accent"] = "spotify"
                    self._save_settings(s)
            except: pass

    def _save_progress(self, data: Dict) -> None:
        data["last_updated"] = datetime.now().isoformat()
        # escrita atômica: temp + rename para evitar corrupção se fechar abrupto
        tmp = self.progress_file.with_suffix(".tmp")
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(self.progress_file)

    def _save_settings(self, settings: Dict) -> None:
        tmp = self.settings_file.with_suffix(".tmp")
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        tmp.replace(self.settings_file)

    def load_progress(self) -> Dict:
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                prof = data.get("profile", {})
                if "display_name" not in prof:
                    prof["display_name"] = self.load_settings().get("display_name", "Piloto-Aluno")
                if "school" not in prof:
                    prof["school"] = self.load_settings().get("school", "Aeroclube de Pirassununga")
                if "solo_hours" not in prof:
                    prof["solo_hours"] = 0
                data["profile"] = prof
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_default_progress()
            return self.load_progress()

    def load_settings(self) -> Dict:
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_default_settings()
            return self.load_settings()

    def save_settings(self, settings: Dict) -> None:
        self._save_settings(settings)

    def toggle_mission_completion(self, mission_id: str, completed: bool = None) -> bool:
        progress = self.load_progress()
        if completed is None:
            completed = mission_id not in progress["completed_missions"]
        if completed and mission_id not in progress["completed_missions"]:
            progress["completed_missions"].append(mission_id)
        elif not completed and mission_id in progress["completed_missions"]:
            progress["completed_missions"].remove(mission_id)
        self._save_progress(progress)
        # atualiza barras automaticamente
        try:
            phase = mission_id.split("-")[0]
            self.update_study_progress(phase)
        except: pass
        return True

    def is_mission_completed(self, mission_id: str) -> bool:
        return mission_id in self.load_progress()["completed_missions"]

    def add_mission_note(self, mission_id: str, note: str) -> None:
        progress = self.load_progress()
        if mission_id not in progress["mission_notes"]:
            progress["mission_notes"][mission_id] = []
        progress["mission_notes"][mission_id].append({"timestamp": datetime.now().isoformat(), "note": note})
        self._save_progress(progress)

    def get_mission_notes(self, mission_id: str) -> List[Dict]:
        return self.load_progress()["mission_notes"].get(mission_id, [])

    def update_study_progress(self, phase: str) -> None:
        progress = self.load_progress()
        phase_missions = [m for m in progress["completed_missions"] if m.startswith(phase)]
        count = len(phase_missions)
        totals = {"PS": 19, "AP": 10, "NV": 5, "NOT": 2}
        total_expected = totals.get(phase, 1)
        # preserva total correto se já existia
        existing_total = progress.get("study_progress",{}).get(phase,{}).get("total", total_expected)
        progress["study_progress"][phase] = {"completed": count, "total": existing_total, "exercises_mastered": phase_missions}
        # atualiza fase atual
        order = ["PS","AP","NV","NOT"]
        last = "PS"
        for p in order:
            if progress["study_progress"].get(p,{}).get("completed",0) > 0:
                last = p
        # só avança, nunca volta
        try:
            cur_idx = order.index(progress["profile"].get("current_phase","PS"))
            new_idx = order.index(last)
            if new_idx > cur_idx:
                progress["profile"]["current_phase"] = last
        except:
            progress["profile"]["current_phase"] = last
        self._save_progress(progress)

    def get_progress_summary(self) -> Dict:
        progress = self.load_progress()
        total_missions = sum(v.get("total",0) for v in progress["study_progress"].values()) or 7
        completed_missions = len(progress["completed_missions"])
        progress_pct = (completed_missions / max(total_missions, 1)) * 100
        return {
            "completed_missions": completed_missions,
            "total_missions_estimated": total_missions,
            "progress_percentage": round(progress_pct, 1),
            "completed_phases": len([p for p,d in progress["study_progress"].items() if d["completed"]>0]),
            "total_phases": 4,
            "current_phase": progress["profile"]["current_phase"]
        }

    def get_phase_progress(self, phase: str) -> Dict:
        return self.load_progress()["study_progress"].get(phase, {"completed":0,"total":0,"exercises_mastered":[]})

    def clear_completed_missions(self) -> None:
        progress = self.load_progress()
        progress["completed_missions"] = []
        progress["study_progress"] = {
            "PS": {"completed": 0, "total": 19, "exercises_mastered": []},
            "AP": {"completed": 0, "total": 10, "exercises_mastered": []},
            "NV": {"completed": 0, "total": 5, "exercises_mastered": []},
            "NOT": {"completed": 0, "total": 2, "exercises_mastered": []}
        }
        self._save_progress(progress)

    def get_data_dir(self) -> Path:
        return self.data_dir

# Singleton
_db_instance = None
def get_database() -> "DatabaseManager":
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance

def get_user_data_dir() -> Path:
    return _get_user_data_dir()
