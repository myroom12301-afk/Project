import csv
import json
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import zoneinfo
from datetime import datetime, timedelta

import customtkinter as ctk

from ..currencies import CURRENCIES as CURRENCY_DATA, get_all as get_all_currencies, _DEFAULT_CODE
from ..locale import t
from .base_dialog import BaseDialog
from .base_page import BasePage

LANGUAGES = ["Русский", "English", "Кыргызча"]
_ALL_ZONES = sorted(zoneinfo.available_timezones())
_DEFAULT_ZONE = "Asia/Bishkek"

_ENTRY_STYLE = dict(
    height=42, corner_radius=8,
    fg_color="#1C2A3D", border_color="#22D7AF", border_width=2,
    text_color="#F7F8FC", placeholder_text_color="#5A6A7E",
)
_MENU_STYLE = dict(
    height=40, corner_radius=8,
    fg_color="#1C2A3D", button_color="#253040", button_hover_color="#2A3A50",
    text_color="#F7F8FC",
    dropdown_fg_color="#1C2A3D", dropdown_text_color="#F7F8FC",
    dropdown_hover_color="#22344E",
)


# ──────────────────────────────────────────────────────────────────── dialogs ──

class EditProfileDialog(BaseDialog):
    def __init__(self, master, user, on_saved=None) -> None:
        self._user = user
        self._on_saved = on_saved
        super().__init__(master, 360, 290)
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text=t("edit_profile.title"),
                     font=ctk.CTkFont("Segoe UI", 18, weight="bold"), text_color="#C8CDD8",
                     ).grid(row=0, column=0, padx=24, pady=(24, 16), sticky="w")

        ctk.CTkLabel(self, text=t("edit_profile.name"),
                     font=ctk.CTkFont("Segoe UI", 13), text_color="#8B95A5",
                     ).grid(row=1, column=0, padx=24, pady=(0, 4), sticky="w")
        self._name = ctk.CTkEntry(self, placeholder_text=t("edit_profile.name_hint"), **_ENTRY_STYLE)
        self._name.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="ew")
        self._name.insert(0, self._user["username"] or "")

        ctk.CTkLabel(self, text=t("edit_profile.email"),
                     font=ctk.CTkFont("Segoe UI", 13), text_color="#8B95A5",
                     ).grid(row=3, column=0, padx=24, pady=(0, 4), sticky="w")
        self._email = ctk.CTkEntry(self, placeholder_text=t("edit_profile.email_hint"), **_ENTRY_STYLE)
        self._email.grid(row=4, column=0, padx=24, pady=(0, 20), sticky="ew")
        try:
            self._email.insert(0, self._user["email"] or "")
        except Exception:
            pass

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=5, column=0, padx=24, pady=(0, 24), sticky="ew")
        btns.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btns, text=t("edit_profile.cancel"), height=40, corner_radius=8,
                      fg_color="#1E2A3A", hover_color="#263345", text_color="#8B95A5",
                      font=ctk.CTkFont("Segoe UI", 14), command=self.destroy,
                      ).grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(btns, text=t("edit_profile.save"), height=40, corner_radius=8,
                      fg_color="#1C584F", hover_color="#1A4F47", text_color="#32E1B5",
                      font=ctk.CTkFont("Segoe UI", 14, weight="bold"), command=self._save,
                      ).grid(row=0, column=1, sticky="ew")

    def _save(self) -> None:
        name = self._name.get().strip()
        if not name:
            self._name.configure(border_color="#E05555")
            return
        if self._on_saved:
            self._on_saved(name, self._email.get().strip())
        self.destroy()


class ExportDialog(BaseDialog):
    def __init__(self, master, controller, weekly: bool = False) -> None:
        self._ctl = controller
        self._weekly = weekly
        super().__init__(master, 300, 230)
        self._build()

    def _build(self) -> None:
        title_key = "weekly_report.title" if self._weekly else "export.title"
        ctk.CTkLabel(self, text=t(title_key),
                     font=ctk.CTkFont("Segoe UI", 18, weight="bold"), text_color="#C8CDD8",
                     ).grid(row=0, column=0, padx=24, pady=(24, 6), sticky="w")
        ctk.CTkLabel(self, text=t("export.choose"),
                     font=ctk.CTkFont("Segoe UI", 13), text_color="#8B95A5",
                     ).grid(row=1, column=0, padx=24, pady=(0, 14), sticky="w")
        for i, (label, fmt) in enumerate([("CSV", "csv"), ("JSON", "json"), ("Excel (.xlsx)", "xlsx")]):
            ctk.CTkButton(self, text=label, height=38, corner_radius=8,
                          fg_color="#1C2A3D", hover_color="#22344E",
                          text_color="#F7F8FC", font=ctk.CTkFont("Segoe UI", 14),
                          command=lambda f=fmt: self._run(f),
                          ).grid(row=2 + i, column=0, padx=24, pady=4, sticky="ew")

    def _run(self, fmt: str) -> None:
        if self._weekly:
            today = datetime.now()
            week_start = (today - timedelta(days=today.weekday())).strftime("%d.%m")
            default_name = f"week_{week_start}-{today.strftime('%d.%m.%Y')}"
            rows = self._ctl.repo.get_weekly_transactions(self._ctl.user["id"])
        else:
            default_name = f"finebank_{datetime.now().strftime('%Y%m%d')}"
            rows = self._ctl.repo.get_all_transactions(self._ctl.user["id"])

        type_map = {"csv": [("CSV", "*.csv")], "json": [("JSON", "*.json")], "xlsx": [("Excel", "*.xlsx")]}
        path = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}", filetypes=type_map[fmt],
            initialfile=default_name,
        )
        if not path:
            return
        if fmt == "csv":
            self._to_csv(path, rows)
        elif fmt == "json":
            self._to_json(path, rows)
        else:
            self._to_xlsx(path, rows)
        self.destroy()

    @staticmethod
    def _to_csv(path: str, rows) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ID", t("common.description"), t("table.category"), t("table.amount"), "Date"])
            for r in rows:
                w.writerow([r["id"], "income" if r["type"] == 1 else "expense",
                             r["category_name"], r["amount"], r["description"] or "", r["created_at"]])

    @staticmethod
    def _to_json(path: str, rows) -> None:
        data = [{"id": r["id"], "type": "income" if r["type"] == 1 else "expense",
                 "category": r["category_name"], "amount": r["amount"],
                 "description": r["description"] or "", "created_at": r["created_at"]} for r in rows]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _to_xlsx(path: str, rows) -> None:
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Error", "Install openpyxl:\npip install openpyxl")
            return
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transactions"
        ws.append(["ID", "Type", "Category", "Amount", "Description", "Date"])
        for r in rows:
            ws.append([r["id"], "income" if r["type"] == 1 else "expense",
                       r["category_name"], r["amount"], r["description"] or "", r["created_at"]])
        wb.save(path)


class ConfirmClearDialog(BaseDialog):
    def __init__(self, master, on_confirmed=None) -> None:
        self._cb = on_confirmed
        super().__init__(master, 340, 200)
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text=t("clear.title"),
                     font=ctk.CTkFont("Segoe UI", 18, weight="bold"), text_color="#F7F8FC",
                     ).grid(row=0, column=0, padx=28, pady=(28, 8))
        ctk.CTkLabel(self, text=t("clear.text"),
                     font=ctk.CTkFont("Segoe UI", 13), text_color="#8B95A5", justify="center",
                     ).grid(row=1, column=0, padx=28, pady=(0, 20))
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=2, column=0, padx=28, pady=(0, 24), sticky="ew")
        btns.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btns, text=t("clear.cancel"), height=40, corner_radius=8,
                      fg_color="#1E2A3A", hover_color="#263345", text_color="#8B95A5",
                      font=ctk.CTkFont("Segoe UI", 14), command=self.destroy,
                      ).grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(btns, text=t("clear.confirm"), height=40, corner_radius=8,
                      fg_color="#5C1A1A", hover_color="#8B2020", text_color="#FF6B6B",
                      font=ctk.CTkFont("Segoe UI", 14, weight="bold"), command=self._confirm,
                      ).grid(row=0, column=1, sticky="ew")

    def _confirm(self) -> None:
        if self._cb:
            self._cb()
        self.destroy()


# ──────────────────────────────────────────────────────── currency picker ──

class CurrencyPickerDialog(BaseDialog):
    def __init__(self, master, current: str, on_selected=None) -> None:
        self._on_selected = on_selected
        self._all = get_all_currencies()
        super().__init__(master, 400, 460)
        self.grid_rowconfigure(1, weight=1)
        self._build(current)

    def _build(self, current: str) -> None:
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())

        ctk.CTkEntry(
            self, textvariable=self._search_var,
            placeholder_text="Search...",
            **_ENTRY_STYLE,
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")

        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color="#2A3A50", scrollbar_button_hover_color="#3A4A60",
        )
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self._scroll.grid_columnconfigure(0, weight=1)

        self._filtered = self._all[:]
        self._render(current)

    def _filter(self) -> None:
        q = self._search_var.get().lower()
        self._filtered = [
            (code, name, sym) for code, name, sym in self._all
            if q in code.lower() or q in name.lower() or q in sym.lower()
        ]
        self._render()

    def _render(self, highlight: str = "") -> None:
        for w in self._scroll.winfo_children():
            w.destroy()
        for code, name, sym in self._filtered:
            is_cur = code == highlight
            row = ctk.CTkFrame(
                self._scroll,
                fg_color="#1C584F" if is_cur else "transparent",
                corner_radius=6,
            )
            row.pack(fill="x", pady=1)
            row.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(
                row, text=sym, width=36, anchor="center",
                font=ctk.CTkFont("Segoe UI", 15, weight="bold"),
                text_color="#32E1B5" if is_cur else "#F7F8FC",
            ).grid(row=0, column=0, padx=(10, 6), pady=6)
            ctk.CTkLabel(
                row, text=f"{code}  —  {name}", anchor="w",
                font=ctk.CTkFont("Segoe UI", 13),
                text_color="#32E1B5" if is_cur else "#C8D4E3",
            ).grid(row=0, column=1, sticky="ew")
            row.bind("<Button-1>", lambda e, c=code: self._select(c))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, c=code: self._select(c))

    def _select(self, code: str) -> None:
        if self._on_selected:
            self._on_selected(code)
        self.destroy()


# ──────────────────────────────────────────────────────── timezone picker ──

class TimezonePickerDialog(BaseDialog):
    def __init__(self, master, current: str, on_selected=None) -> None:
        self._on_selected = on_selected
        self._all_zones = _ALL_ZONES
        super().__init__(master, 360, 440)
        self.grid_rowconfigure(1, weight=1)
        self._build(current)

    def _build(self, current: str) -> None:
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())

        ctk.CTkEntry(
            self, textvariable=self._search_var,
            placeholder_text="Search...",
            **_ENTRY_STYLE,
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")

        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color="#2A3A50", scrollbar_button_hover_color="#3A4A60",
        )
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self._scroll.grid_columnconfigure(0, weight=1)

        self._filtered = self._all_zones[:]
        self._render(current)

    def _filter(self) -> None:
        q = self._search_var.get().lower()
        self._filtered = [z for z in self._all_zones if q in z.lower()]
        self._render()

    def _render(self, highlight: str = "") -> None:
        for w in self._scroll.winfo_children():
            w.destroy()
        for zone in self._filtered[:200]:
            is_cur = zone == highlight
            ctk.CTkButton(
                self._scroll, text=zone, anchor="w", height=30, corner_radius=6,
                fg_color="#1C584F" if is_cur else "transparent",
                hover_color="#1C2A3D",
                text_color="#32E1B5" if is_cur else "#C8D4E3",
                font=ctk.CTkFont("Segoe UI", 13),
                command=lambda z=zone: self._select(z),
            ).pack(fill="x", pady=1)

    def _select(self, zone: str) -> None:
        if self._on_selected:
            self._on_selected(zone)
        self.destroy()


# ───────────────────────────────────────────────────────────────── main page ──

class SettingsPage(BasePage):
    def __init__(self, master, controller) -> None:
        super().__init__(master, controller)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_scroll()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 0))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=t("settings.title"),
                     font=ctk.CTkFont("Segoe UI", 28, weight="bold"), text_color="#F6F7FB",
                     ).grid(row=0, column=0, sticky="w")
        ctk.CTkFrame(header, height=1, fg_color="#3A4456").grid(row=1, column=0, sticky="ew", pady=(10, 0))

    def _build_scroll(self) -> None:
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color="#2A3A50", scrollbar_button_hover_color="#3A4A60",
        )
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=28, pady=(16, 20))
        self._scroll.grid_columnconfigure(0, weight=1)
        self._build_profile_card()
        self._build_data_card()

    def _build_profile_card(self) -> None:
        card = ctk.CTkFrame(self._scroll, fg_color="#151F2E", corner_radius=16)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=t("settings.profile"),
                     font=ctk.CTkFont("Segoe UI", 16, weight="bold"), text_color="#C8D4E3",
                     ).grid(row=0, column=0, padx=20, pady=(18, 12), sticky="w")
        ctk.CTkFrame(card, height=1, fg_color="#263041").grid(row=1, column=0, sticky="ew", padx=20)

        user_row = ctk.CTkFrame(card, fg_color="transparent")
        user_row.grid(row=2, column=0, sticky="ew", padx=20, pady=(14, 0))
        user_row.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkFrame(user_row, width=48, height=48, corner_radius=24, fg_color="#1AB89A")
        avatar.grid(row=0, column=0, padx=(0, 14))
        avatar.grid_propagate(False)
        self._avatar_label = ctk.CTkLabel(avatar, text="T",
                                          font=ctk.CTkFont("Segoe UI", 20, weight="bold"),
                                          text_color="#FFFFFF", fg_color="transparent")
        self._avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(user_row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w")
        self._name_label  = ctk.CTkLabel(info, text="",
                                         font=ctk.CTkFont("Segoe UI", 15, weight="bold"), text_color="#F7F8FC")
        self._name_label.pack(anchor="w")
        self._email_label = ctk.CTkLabel(info, text="",
                                         font=ctk.CTkFont("Segoe UI", 12), text_color="#7F899A")
        self._email_label.pack(anchor="w")

        ctk.CTkButton(user_row, text=t("settings.edit_btn"),
                      width=100, height=34, corner_radius=8,
                      fg_color="#1C2A3D", hover_color="#22344E",
                      border_width=1, border_color="#3A4A5E",
                      text_color="#C8D4E3", font=ctk.CTkFont("Segoe UI", 13),
                      command=self._open_edit_profile,
                      ).grid(row=0, column=2)

        ctk.CTkFrame(card, height=1, fg_color="#263041").grid(row=3, column=0, sticky="ew", padx=20, pady=(14, 0))

        ctk.CTkLabel(card, text=t("settings.currency"),
                     font=ctk.CTkFont("Segoe UI", 13), text_color="#8B95A5",
                     ).grid(row=4, column=0, padx=20, pady=(14, 4), sticky="w")
        self._currency_code = _DEFAULT_CODE
        self._currency_display = ctk.StringVar(value=self._currency_label(_DEFAULT_CODE))
        self._currency_btn = ctk.CTkButton(
            card, textvariable=self._currency_display, anchor="w",
            height=40, corner_radius=8,
            fg_color="#1C2A3D", hover_color="#22344E",
            text_color="#F7F8FC", font=ctk.CTkFont("Segoe UI", 13),
            command=self._open_currency_picker,
        )
        self._currency_btn.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(card, text=t("settings.language"),
                     font=ctk.CTkFont("Segoe UI", 13), text_color="#8B95A5",
                     ).grid(row=6, column=0, padx=20, pady=(0, 4), sticky="w")
        self._language_var = ctk.StringVar(value=LANGUAGES[0])
        ctk.CTkOptionMenu(card, variable=self._language_var, values=LANGUAGES, **_MENU_STYLE,
                          ).grid(row=7, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(card, text=t("settings.timezone"),
                     font=ctk.CTkFont("Segoe UI", 13), text_color="#8B95A5",
                     ).grid(row=8, column=0, padx=20, pady=(0, 4), sticky="w")
        self._timezone_var = ctk.StringVar(value=_DEFAULT_ZONE)
        self._timezone_btn = ctk.CTkButton(
            card, textvariable=self._timezone_var, anchor="w",
            height=40, corner_radius=8,
            fg_color="#1C2A3D", hover_color="#22344E",
            text_color="#F7F8FC", font=ctk.CTkFont("Segoe UI", 13),
            command=self._open_timezone_picker,
        )
        self._timezone_btn.grid(row=9, column=0, padx=20, pady=(0, 10), sticky="ew")

        self._settings_status = ctk.CTkLabel(card, text="",
                                             font=ctk.CTkFont("Segoe UI", 12), text_color="#32E1B5")
        self._settings_status.grid(row=10, column=0, padx=20, sticky="w")

        ctk.CTkButton(card, text=t("settings.save_btn"),
                      height=42, corner_radius=10,
                      fg_color="#1C584F", hover_color="#1A4F47",
                      text_color="#32E1B5", font=ctk.CTkFont("Segoe UI", 14, weight="bold"),
                      command=self._save_settings,
                      ).grid(row=11, column=0, padx=20, pady=(4, 18), sticky="w")

    def _build_data_card(self) -> None:
        card = ctk.CTkFrame(self._scroll, fg_color="#151F2E", corner_radius=16)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=t("settings.data"),
                     font=ctk.CTkFont("Segoe UI", 16, weight="bold"), text_color="#C8D4E3",
                     ).grid(row=0, column=0, padx=20, pady=(18, 12), sticky="w")
        ctk.CTkFrame(card, height=1, fg_color="#263041").grid(row=1, column=0, sticky="ew", padx=20)

        self._action_row(card, row=2,
                         icon="📥",
                         title=t("settings.export_title"),
                         desc=t("settings.export_desc"),
                         btn_text=t("settings.export_btn"),
                         btn_fg="#1C2A3D", btn_hover="#22344E", btn_color="#A4AFBE",
                         command=self._open_export)

        ctk.CTkFrame(card, height=1, fg_color="#263041").grid(row=3, column=0, sticky="ew", padx=20)

        self._action_row(card, row=4,
                         icon="🗑",
                         title=t("settings.clear_title"),
                         desc=t("settings.clear_desc"),
                         btn_text=t("settings.clear_btn"),
                         btn_fg="#5C1A1A", btn_hover="#8B2020", btn_color="#FF6B6B",
                         command=self._confirm_clear)

        ctk.CTkFrame(card, height=1, fg_color="#263041").grid(row=5, column=0, sticky="ew", padx=20)

        self._action_row(card, row=6,
                         icon="📊",
                         title=t("settings.weekly_title"),
                         desc=t("settings.weekly_desc"),
                         btn_text=t("settings.weekly_btn"),
                         btn_fg="#1C2A3D", btn_hover="#22344E", btn_color="#A4AFBE",
                         command=self._open_weekly_report)

    @staticmethod
    def _action_row(parent, row: int, icon: str, title: str, desc: str,
                    btn_text: str, btn_fg: str, btn_hover: str, btn_color: str, command) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=20, pady=12)
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=icon, font=ctk.CTkFont("Segoe UI", 20), text_color="#3FC2A3",
                     ).grid(row=0, column=0, rowspan=2, padx=(0, 14))
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont("Segoe UI", 14, weight="bold"), text_color="#EDF2FA",
                     ).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(frame, text=desc, font=ctk.CTkFont("Segoe UI", 12), text_color="#7F899A",
                     ).grid(row=1, column=1, sticky="w")
        ctk.CTkButton(frame, text=btn_text, width=130, height=34, corner_radius=8,
                      fg_color=btn_fg, hover_color=btn_hover,
                      border_width=1, border_color="#3A4A5E",
                      text_color=btn_color, font=ctk.CTkFont("Segoe UI", 13),
                      command=command,
                      ).grid(row=0, column=2, rowspan=2, padx=(8, 0))

    # ── actions ───────────────────────────────────────────────────────────────

    def _open_edit_profile(self) -> None:
        EditProfileDialog(self, self.controller.user, on_saved=self._on_profile_saved)

    def _on_profile_saved(self, name: str, email: str) -> None:
        repo = self.controller.repo
        user_id = self.controller.user["id"]
        with repo.connection:
            repo.connection.execute(
                "UPDATE users SET username = ?, email = ? WHERE id = ?",
                (name, email, user_id),
            )
        self.controller.refresh_user()
        self.controller.sidebar.set_username(name)
        self._refresh_profile_ui()

    def _save_settings(self) -> None:
        repo     = self.controller.repo
        user_id  = self.controller.user["id"]
        with repo.connection:
            repo.connection.execute(
                "UPDATE users SET currency = ?, language = ?, timezone = ? WHERE id = ?",
                (self._currency_code, self._language_var.get(), self._timezone_var.get(), user_id),
            )
        self.controller.apply_language(self._language_var.get())

    def _open_currency_picker(self) -> None:
        CurrencyPickerDialog(self, self._currency_code, on_selected=self._on_currency_selected)

    def _on_currency_selected(self, code: str) -> None:
        self._currency_code = code
        self._currency_display.set(self._currency_label(code))

    @staticmethod
    def _currency_label(code: str) -> str:
        info = CURRENCY_DATA.get(code, {})
        return f"{info.get('symbol', code)}  {code}  —  {info.get('name', '')}"

    def _open_timezone_picker(self) -> None:
        TimezonePickerDialog(self, self._timezone_var.get(),
                             on_selected=lambda z: self._timezone_var.set(z))

    def _open_weekly_report(self) -> None:
        ExportDialog(self, self.controller, weekly=True)

    def _open_export(self) -> None:
        ExportDialog(self, self.controller)

    def _confirm_clear(self) -> None:
        ConfirmClearDialog(self, on_confirmed=self._clear_data)

    def _clear_data(self) -> None:
        self.controller.repo.reset_demo_data()
        self.controller.refresh_user()
        self.controller.show_page("Обзор")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _refresh_profile_ui(self) -> None:
        user = self.controller.user
        if not user:
            return
        name = user["username"] or ""
        self._name_label.configure(text=name)
        self._avatar_label.configure(text=name[0].upper() if name else "?")
        try:
            self._email_label.configure(text=user["email"] or "")
        except Exception:
            pass

    def on_show(self) -> None:
        self._refresh_profile_ui()
        user = self.controller.user
        if not user:
            return
        try:
            currency = user["currency"] or _DEFAULT_CODE
            language = user["language"] or "Русский"
            timezone = user["timezone"] or _DEFAULT_ZONE
        except Exception:
            currency, language, timezone = _DEFAULT_CODE, "Русский", _DEFAULT_ZONE

        self._currency_code = currency if currency in CURRENCY_DATA else _DEFAULT_CODE
        self._currency_display.set(self._currency_label(self._currency_code))
        self._language_var.set(language if language in LANGUAGES else LANGUAGES[0])
        self._timezone_var.set(timezone if timezone in _ALL_ZONES else _DEFAULT_ZONE)
