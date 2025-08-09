"""DataManager: абстракция для GUI над файловыми и модульными операциями.

Цели:
 - Сконцентрировать доступ к данным (токены, сертификаты, отчёты, регионы, email-конфиг)
 - Инкапсулировать преобразования структур для вкладок GUI
 - Обеспечить точку для последующего кеширования и фоновых обновлений
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import threading
import sys

# Добавляем корень репозитория и импортируем через пакет scripts.*
root_path = Path(__file__).parent.parent
scripts_path = root_path / "scripts"
for p in (root_path,):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from scripts.token_manager import (
        load_tokens_file,
        save_tokens_file,
        load_certificates_file,
        save_certificates_file,
        load_thumbprints_file,
        save_thumbprints_file,
        mask_token
    )
    from scripts.region_manager import load_regions_data, save_regions_data
    from scripts.file_utils import get_reports_list
    from scripts.email_utils import load_email_config
except ImportError as e:
    # Отложенный импорт — допустимо в ранних стадиях; логировать в stdout
    print(f"[DataManager] Import error: {e}")


class DataManager:
    _instance: Optional["DataManager"] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Кеши
        self._tokens: Dict[str, str] = {}
        self._tokens_generated_at: str = "-"
        self._certs: List[Dict[str, Any]] = []
        self._thumbprints: List[str] = []
        self._regions: Dict[str, Any] = {}
        self._reports_raw: Dict[str, List[Dict[str, Any]]] = {}
        self._email_config: Dict[str, Any] | None = None
        self.refresh_all(initial=True)

    # -------------------- PUBLIC API --------------------
    def refresh_all(self, initial: bool = False):
        """Полное обновление данных."""
        self._load_tokens()
        self._load_certs()
        self._load_regions()
        self._load_reports()
        self._load_email()

    # Tokens
    def list_tokens(self) -> List[Dict[str, str]]:
        return [
            {"name": name, "token": token, "masked": mask_token(token), "generated_at": self._tokens_generated_at}
            for name, token in self._tokens.items()
        ]

    def add_token(self, name: str, token: str) -> bool:
        data = load_tokens_file()
        tokens = data.get("tokens", {})
        if name in tokens:
            return False
        tokens[name] = token
        data["tokens"] = tokens
        data["generated_at"] = datetime.now().isoformat()
        ok = save_tokens_file(data)
        if ok:
            self._load_tokens()
        return ok

    def update_token(self, old_name: str, new_name: str, new_value: Optional[str]) -> bool:
        data = load_tokens_file()
        tokens = data.get("tokens", {})
        if old_name not in tokens:
            return False
        value = tokens[old_name]
        if new_value:
            value = new_value
        if new_name != old_name and new_name in tokens:
            return False
        if new_name != old_name:
            del tokens[old_name]
        tokens[new_name] = value
        data["tokens"] = tokens
        data["generated_at"] = datetime.now().isoformat()
        ok = save_tokens_file(data)
        if ok:
            self._load_tokens()
        return ok

    def delete_token(self, name: str) -> bool:
        data = load_tokens_file()
        tokens = data.get("tokens", {})
        if name in tokens:
            del tokens[name]
            data["tokens"] = tokens
            data["generated_at"] = datetime.now().isoformat()
            ok = save_tokens_file(data)
            if ok:
                self._load_tokens()
            return ok
        return False

    # Certificates
    def list_certificates(self) -> List[Dict[str, Any]]:
        return list(self._certs)

    def add_certificate(self, name: str, thumbprint: str) -> bool:
        data = load_certificates_file()
        certs = data.get("certificates", [])
        if any(c.get("thumbprint") == thumbprint for c in certs):
            return False
        certs.append({"name": name, "thumbprint": thumbprint})
        data["certificates"] = certs
        ok = save_certificates_file(data)
        if ok:
            self._load_certs()
        # thumbprints
        tps = load_thumbprints_file()
        if thumbprint not in tps:
            tps.append(thumbprint)
            save_thumbprints_file(tps)
            self._thumbprints = tps
        return ok

    def update_certificate(self, old_name: str, new_name: str, new_thumb: Optional[str]) -> bool:
        data = load_certificates_file()
        certs = data.get("certificates", [])
        found = None
        for c in certs:
            if c.get("name") == old_name:
                found = c
                break
        if not found:
            return False
        if new_thumb:
            found["thumbprint"] = new_thumb
        found["name"] = new_name
        ok = save_certificates_file({"certificates": certs})
        if ok:
            self._load_certs()
        return ok

    def delete_certificate(self, name: str) -> bool:
        data = load_certificates_file()
        certs = data.get("certificates", [])
        new_list = [c for c in certs if c.get("name") != name]
        if len(new_list) == len(certs):
            return False
        ok = save_certificates_file({"certificates": new_list})
        if ok:
            self._load_certs()
        return ok

    # Regions
    def list_regions(self) -> List[Dict[str, Any]]:
        return [
            {"code": code, **(info if isinstance(info, dict) else {"name": str(info)})}
            for code, info in self._regions.items()
        ]

    def save_region(self, code: str, name: str, emails: Optional[List[str]] = None, tc_list: Optional[List[str]] = None) -> bool:
        data = load_regions_data()
        data[code] = {
            "name": name,
            "emails": emails or [],
            "tc_list": tc_list or data.get(code, {}).get("tc_list", [])
        }
        ok = save_regions_data(data)
        if ok:
            self._load_regions()
        return ok

    # Reports
    def list_reports_flat(self) -> List[Dict[str, Any]]:
        flat: List[Dict[str, Any]] = []
        for cert, items in self._reports_raw.items():
            for r in items:
                flat.append({
                    "cert": cert,
                    "date": r.get("date", ""),
                    "filename": r.get("filename", ""),
                    "path": r.get("path", "")
                })
        return flat

    def load_email_config(self) -> Optional[Dict[str, Any]]:
        if self._email_config is None:
            self._load_email()
        return self._email_config

    # Placeholder for daily process (можно связать с main.run_daily_process)
    def run_daily_process(self):
        try:
            from scripts.main import run_daily_process as core_run
        except ImportError:
            # fallback: попытка относительного импорта если структура отличается
            from main import run_daily_process as core_run  # type: ignore
        return core_run()

    # -------------------- INTERNAL LOADERS --------------------
    def _load_tokens(self):
        data = load_tokens_file()
        self._tokens = data.get("tokens", {})
        self._tokens_generated_at = data.get("generated_at", "-")

    def _load_certs(self):
        data = load_certificates_file()
        self._certs = data.get("certificates", [])
        self._thumbprints = load_thumbprints_file()

    def _load_regions(self):
        self._regions = load_regions_data() or {}

    def _load_reports(self):
        try:
            self._reports_raw = get_reports_list() or {}
        except Exception:
            self._reports_raw = {}

    def _load_email(self):
        try:
            self._email_config = load_email_config()
        except Exception:
            self._email_config = None


def get_data_manager() -> DataManager:
    return DataManager()
