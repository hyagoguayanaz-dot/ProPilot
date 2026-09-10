"""
ProPilot Mobile - Database manager adaptado para Android (Kivy)
- Cache em memoria com mtime para evitar leituras repetidas
- Escrita atomica + invalidacao de cache
- Singleton thread-safe leve
- Adaptacao de caminho: Android usa app_storage_path / primary storage,
  desktop usa mesmo caminho do database.py original.
"""
import json
import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def _get_android_data_dir() -> Path | None:
    """
    Tenta resolver diretorio de dados no Android via Kivy.
    Ordem de tentativa:
      1. android.storage.app_storage_path()
      2. android.storage.primary_external_storage_path() + /ProPilot
      3. jnius: context.getFilesDir().getPath()
      4. Fallback para KIVY_HOME / HOME
    Retorna None se nao estiver no Android ou se falhar.
    """
    try:
        from kivy.utils import platform as kivy_platform
        if kivy_platform != "android":
            return None
    except ImportError:
        return None
    except Exception:
        return None

    # 1) android.storage.app_storage_path (python-for-android)
    try:
        from android.storage import app_storage_path  # type: ignore
        p = Path(app_storage_path())
        if p.name == "files":
            return p
        return p / "ProPilot"
    except Exception:
        pass

    # 2) primary_external_storage_path (armazenamento compartilhado)
    try:
        from android.storage import primary_external_storage_path  # type: ignore
        p = Path(primary_external_storage_path()) / "ProPilot"
        return p
    except Exception:
        pass

    # 3) jnius via Context.getFilesDir()
    try:
        from jnius import autoclass  # type: ignore
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        context = PythonActivity.mActivity
        files_dir = context.getFilesDir().getPath()
        return Path(files_dir)
    except Exception:
        pass

    for env_key in ("ANDROID_APP_PATH", "ANDROID_PRIVATE", "HOME"):
        v = os.environ.get(env_key)
        if v:
            try:
                return Path(v) / "ProPilot"
            except Exception:
                continue

    return Path("/data/data/org.propilot.app/files")


def _get_user_data_dir() -> Path:
    android_dir = _get_android_data_dir()
    if android_dir is not None:
        return android_dir

    if getattr(sys, "frozen", False):
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "ProPilot"
    try:
        candidate = Path(__file__).resolve().parent.parent / "data"
        if candidate.exists():
            return candidate
    except Exception:
        pass
    return Path(__file__).resolve().parent / "data"


def get_user_data_dir() -> Path:
    """Public accessor - espelha API do database.py original."""
    return _get_user_data_dir()


class DatabaseManager:
    def __init__(self, data_dir: str | Path = None):
        if data_dir is None:
            data_dir = _get_user_data_dir()
        self.data_dir = Path(data_dir)
        self.progress_file = self.data_dir / "user_progress.json"
        self.settings_file = self.data_dir / "user_settings.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._progress_cache = None
        self._settings_cache = None
        self._progress_mtime = 0
        self._settings_mtime = 0
        try:
            if getattr(sys, "frozen", False):
                legacy = Path(__file__).resolve().parent.parent / "data"
                exe_dir = Path(sys.executable).parent / "data"
                for src_dir in [legacy, exe_dir]:
                    for fname in ["user_progress.json", "user_settings.json"]:
                        src = src_dir / fname
                        dst = self.data_dir / fname
                        if src.exists() and not dst.exists():
                            try:
                                dst.write_bytes(src.read_bytes())
                            except Exception:
                                pass
                alt = Path(os.environ.get("APPDATA", "")) / "ProPilot" if os.environ.get("APPDATA") else None
                if alt and alt != self.data_dir and alt.exists():
                    for fname in ["user_progress.json", "user_settings.json"]:
                        src = alt / fname
                        dst = self.data_dir / fname
                        if src.exists() and not dst.exists():
                            try:
                                dst.write_bytes(src.read_bytes())
                            except Exception:
                                pass
            else:
                try:
                    root_data = Path(__file__).resolve().parent.parent / "data"
                    mobile_data = Path(__file__).resolve().parent / "data"
                    if self.data_dir == mobile_data and root_data.exists():
                        for fname in ["user_progress.json", "user_settings.json"]:
                            src = root_data / fname
                            dst = self.data_dir / fname
                            if src.exists() and not dst.exists():
                                try:
                                    dst.write_bytes(src.read_bytes())
                                except Exception:
                                    pass
                except Exception:
                    pass
        except Exception:
            pass
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
                "NOT": {"completed": 0, "total": 2, "exercises_mastered": []},
            },
            "last_updated": datetime.now().isoformat(),
            "profile": {
                "display_name": "Piloto-Aluno",
                "school": "Aeroclube de Pirassununga",
                "total_flight_hours": 0,
                "solo_hours": 0,
                "current_phase": "PS",
                "pilot_license_status": "student",
            },
        }
        if not self.progress_file.exists():
            self._save_progress(default_progress)
        else:
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                changed = False
                for k, v in default_progress.items():
                    if k not in existing:
                        existing[k] = v
                        changed = True
                for pk, pv in default_progress["profile"].items():
                    if pk not in existing.get("profile", {}):
                        existing["profile"][pk] = pv
                        changed = True
                expected_totals = {"PS": 19, "AP": 10, "NV": 5, "NOT": 2}
                sp = existing.get("study_progress", {})
                for ph, exp in expected_totals.items():
                    if ph not in sp or sp[ph].get("total") != exp:
                        if ph not in sp:
                            sp[ph] = {"completed": 0, "total": exp, "exercises_mastered": []}
                        else:
                            sp[ph]["total"] = exp
                        changed = True
                existing["study_progress"] = sp
                if changed:
                    self._save_progress(existing)
            except Exception:
                pass

    def _init_default_settings(self):
        default_settings = {
            "theme": "dark",
            "accent": "spotify",
            "language": "pt-BR",
            "notifications": True,
            "study_reminders": True,
            "display_name": "Piloto-Aluno",
            "school": "Aeroclube de Pirassununga",
        }
        if not self.settings_file.exists():
            self._save_settings(default_settings)
        else:
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    s = json.load(f)
                if "accent" not in s:
                    s["accent"] = "spotify"
                    self._save_settings(s)
            except Exception:
                pass

    def _save_progress(self, data: Dict) -> None:
        with self._lock:
            data["last_updated"] = datetime.now().isoformat()
            tmp = self.progress_file.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            tmp.replace(self.progress_file)
            self._progress_cache = data
            try:
                self._progress_mtime = self.progress_file.stat().st_mtime
            except Exception:
                self._progress_mtime = time.time()

    def _save_settings(self, settings: Dict) -> None:
        with self._lock:
            tmp = self.settings_file.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            tmp.replace(self.settings_file)
            self._settings_cache = settings
            try:
                self._settings_mtime = self.settings_file.stat().st_mtime
            except Exception:
                self._settings_mtime = time.time()

    def load_progress(self) -> Dict:
        with self._lock:
            try:
                mtime = self.progress_file.stat().st_mtime
                if self._progress_cache is not None and mtime == self._progress_mtime:
                    return self._progress_cache
            except Exception:
                pass
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                prof = data.get("profile", {})
                if "display_name" not in prof:
                    prof["display_name"] = self.load_settings().get("display_name", "Piloto-Aluno")
                if "school" not in prof:
                    prof["school"] = self.load_settings().get("school", "Aeroclube de Pirassununga")
                if "solo_hours" not in prof:
                    prof["solo_hours"] = 0
                data["profile"] = prof
                self._progress_cache = data
                try:
                    self._progress_mtime = self.progress_file.stat().st_mtime
                except Exception:
                    self._progress_mtime = time.time()
                return data
            except (FileNotFoundError, json.JSONDecodeError):
                self._init_default_progress()
                return self.load_progress()

    def save_progress(self, data: Dict) -> None:
        """Wrapper publico para _save_progress (requisito mobile)."""
        self._save_progress(data)

    def load_settings(self) -> Dict:
        with self._lock:
            try:
                mtime = self.settings_file.stat().st_mtime
                if self._settings_cache is not None and mtime == self._settings_mtime:
                    return self._settings_cache
            except Exception:
                pass
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._settings_cache = data
                try:
                    self._settings_mtime = self.settings_file.stat().st_mtime
                except Exception:
                    self._settings_mtime = time.time()
                return data
            except (FileNotFoundError, json.JSONDecodeError):
                self._init_default_settings()
                return self.load_settings()

    def save_settings(self, settings: Dict) -> None:
        self._save_settings(settings)

    def toggle_mission_completion(self, mission_id: str, completed: bool = None) -> bool:
        progress = self.load_progress()
        progress = json.loads(json.dumps(progress))
        if completed is None:
            completed = mission_id not in progress["completed_missions"]
        if completed and mission_id not in progress["completed_missions"]:
            progress["completed_missions"].append(mission_id)
        elif not completed and mission_id in progress["completed_missions"]:
            progress["completed_missions"].remove(mission_id)
        self._save_progress(progress)
        try:
            phase = mission_id.split("-")[0]
            self.update_study_progress(phase)
        except Exception:
            pass
        return True

    # Aliases para compatibilidade com versao simplificada anterior
    def toggle_mission_complete(self, mission_id: str):
        result = self.toggle_mission_completion(mission_id)
        return self.is_mission_completed(mission_id)

    def is_mission_completed(self, mission_id: str) -> bool:
        prog = self.load_progress()
        return mission_id in prog.get("completed_missions", [])

    def is_mission_complete(self, mission_id: str) -> bool:
        return self.is_mission_completed(mission_id)

    def add_mission_note(self, mission_id: str, note: str) -> None:
        progress = json.loads(json.dumps(self.load_progress()))
        if mission_id not in progress["mission_notes"]:
            progress["mission_notes"][mission_id] = []
        progress["mission_notes"][mission_id].append({"timestamp": datetime.now().isoformat(), "note": note})
        self._save_progress(progress)

    def get_mission_notes(self, mission_id: str) -> List[Dict]:
        return self.load_progress()["mission_notes"].get(mission_id, [])

    def update_study_progress(self, phase: str) -> None:
        progress = json.loads(json.dumps(self.load_progress()))
        phase_missions = [m for m in progress["completed_missions"] if m.startswith(phase)]
        count = len(phase_missions)
        totals = {"PS": 19, "AP": 10, "NV": 5, "NOT": 2}
        total_expected = totals.get(phase, 1)
        existing_total = progress.get("study_progress", {}).get(phase, {}).get("total", total_expected)
        progress["study_progress"][phase] = {"completed": count, "total": existing_total, "exercises_mastered": phase_missions}
        order = ["PS", "AP", "NV", "NOT"]
        last = "PS"
        for p in order:
            if progress["study_progress"].get(p, {}).get("completed", 0) > 0:
                last = p
        try:
            cur_idx = order.index(progress["profile"].get("current_phase", "PS"))
            new_idx = order.index(last)
            if new_idx > cur_idx:
                progress["profile"]["current_phase"] = last
        except Exception:
            progress["profile"]["current_phase"] = last
        self._save_progress(progress)

    def update_profile(self, display_name=None, school=None, **kwargs):
        prog = json.loads(json.dumps(self.load_progress()))
        sett = json.loads(json.dumps(self.load_settings()))
        if display_name is not None:
            prog["profile"]["display_name"] = display_name
            sett["display_name"] = display_name
        if school is not None:
            prog["profile"]["school"] = school
            sett["school"] = school
        for k, v in kwargs.items():
            prog["profile"][k] = v
        self._save_progress(prog)
        self._save_settings(sett)

    def get_progress_summary(self) -> Dict:
        progress = self.load_progress()
        total_missions = sum(v.get("total", 0) for v in progress["study_progress"].values()) or 7
        completed_missions = len(progress["completed_missions"])
        progress_pct = (completed_missions / max(total_missions, 1)) * 100
        return {
            "completed_missions": completed_missions,
            "total_missions_estimated": total_missions,
            "progress_percentage": round(progress_pct, 1),
            "completed_phases": len([p for p, d in progress["study_progress"].items() if d["completed"] > 0]),
            "total_phases": 4,
            "current_phase": progress["profile"]["current_phase"],
        }

    def get_phase_progress(self, phase: str) -> Dict:
        return self.load_progress()["study_progress"].get(phase, {"completed": 0, "total": 0, "exercises_mastered": []})

    def clear_completed_missions(self) -> None:
        progress = json.loads(json.dumps(self.load_progress()))
        progress["completed_missions"] = []
        progress["study_progress"] = {
            "PS": {"completed": 0, "total": 19, "exercises_mastered": []},
            "AP": {"completed": 0, "total": 10, "exercises_mastered": []},
            "NV": {"completed": 0, "total": 5, "exercises_mastered": []},
            "NOT": {"completed": 0, "total": 2, "exercises_mastered": []},
        }
        self._save_progress(progress)

    def get_data_dir(self) -> Path:
        return self.data_dir


_db_instance = None
_lock_inst = threading.Lock()


def get_database(data_dir=None) -> DatabaseManager:
    global _db_instance
    if _db_instance is None:
        with _lock_inst:
            if _db_instance is None:
                _db_instance = DatabaseManager(data_dir=data_dir)
    return _db_instance
