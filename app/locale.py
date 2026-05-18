from __future__ import annotations

import json
from pathlib import Path

_DIR = Path(__file__).resolve().parent / "locales"
_LANG_MAP = {"Русский": "ru", "English": "en", "Кыргызча": "kg"}


class _Locale:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._load("ru")

    def set(self, lang_name: str) -> None:
        self._load(_LANG_MAP.get(lang_name, "ru"))

    def _load(self, code: str) -> None:
        path = _DIR / f"{code}.json"
        try:
            self._data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass

    def __call__(self, key: str, **kw) -> str:
        text = self._data.get(key, key)
        try:
            return text.format(**kw) if kw else text
        except Exception:
            return text


locale = _Locale()
t = locale