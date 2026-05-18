from __future__ import annotations

from datetime import datetime

import customtkinter as ctk

from ..locale import t
from .base_page import BasePage

EXPENSE = 0
INCOME = 1


class MonthPickerDialog(ctk.CTkToplevel):
    def __init__(self, master, year: int, selected_month: int, on_select) -> None:
        super().__init__(master)
        self._year = year
        self._selected_month = selected_month
        self._on_select = on_select

        self.title("")
        self.geometry("300x248")
        self.resizable(False, False)
        self.configure(fg_color="#0E1726")
        self.lift()
        self.focus_force()
        self.after(50, self._center)
        self.after(50, self.grab_set)
        self.grid_columnconfigure((0, 1), weight=1)
        self._build()

    def _center(self) -> None:
        self.update_idletasks()
        p = self.master.winfo_toplevel()
        w, h = 300, 248
        self.geometry(f"{w}x{h}+{p.winfo_rootx() + (p.winfo_width() - w) // 2}+{p.winfo_rooty() + (p.winfo_height() - h) // 2}")

    def _build(self) -> None:
        ctk.CTkLabel(self, text=str(self._year),
                     font=ctk.CTkFont("Segoe UI", 18, weight="bold"), text_color="#F7F8FC",
                     ).grid(row=0, column=0, columnspan=2, padx=20, pady=(18, 14))

        for month in range(1, 13):
            row = ((month - 1) % 6) + 1
            col = 0 if month <= 6 else 1
            label = f"{t(f'month.{month}').capitalize()} {self._year}"
            ctk.CTkButton(
                self, text=label, height=30, corner_radius=8,
                fg_color="#20D6B1" if month == self._selected_month else "#1E2938",
                hover_color="#1AB89A" if month == self._selected_month else "#263345",
                text_color="#07131C" if month == self._selected_month else "#D7DFEA",
                font=ctk.CTkFont("Segoe UI", 13),
                command=lambda m=month: self._select(m),
            ).grid(row=row, column=col, padx=10, pady=4, sticky="ew")

    def _select(self, month: int) -> None:
        self._on_select(self._year, month)
        self.destroy()


class TransactionListPage(BasePage):
    def __init__(self, master, controller, tx_type: int, title_key: str) -> None:
        super().__init__(master, controller)
        self.tx_type = tx_type
        self.title_key = title_key
        self.selected_category_id: int | None = None
        self.selected_year: int | None = None
        self.selected_month: int | None = None
        self.month_dialog: MonthPickerDialog | None = None
        self.filter_buttons: dict[int | None, ctk.CTkButton] = {}

        self.amount_color = "#57FF2D" if tx_type == INCOME else "#FF2F2F"
        self.badge_text = "#C4FFF1"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build()

    @property
    def repo(self):
        return self.controller.repo

    @property
    def user(self):
        return self.controller.user

    def on_show(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        self.controller.refresh_user()
        summary = self.repo.get_dashboard_summary(self.user["id"])
        self.controller.sidebar.set_username(summary["username"])
        self.greeting_label.configure(text=t("dashboard.hello", name=summary["username"].split()[0]))

        now = datetime.now()
        self.date_label.configure(text=f"{now.day} {t(f'month_short.{now.month}')}, {now.year}")

        self._ensure_selected_month()
        self.month_button.configure(text=self._get_month_label())
        self._render_filters()
        self._render_rows()

    def _build(self) -> None:
        self._build_header()
        self._build_filters()
        self._build_table()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 0))
        header.grid_columnconfigure(0, weight=1)

        self.greeting_label = ctk.CTkLabel(header, text="",
                                           font=ctk.CTkFont(family="Segoe UI", size=18),
                                           text_color="#F6F7FB")
        self.greeting_label.grid(row=0, column=0, sticky="w", padx=(18, 0))

        self.date_label = ctk.CTkLabel(header, text="",
                                       font=ctk.CTkFont(family="Segoe UI", size=12),
                                       text_color="#8B95A5")
        self.date_label.grid(row=1, column=0, sticky="w", padx=(18, 0), pady=(2, 0))

        ctk.CTkFrame(header, height=1, fg_color="#59616E").grid(row=2, column=0, sticky="ew", pady=(8, 0))

    def _build_filters(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=1, column=0, sticky="ew", padx=22, pady=(26, 16))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top, text=t(self.title_key),
                     font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                     text_color="#F5F7FB",
                     ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        chips_row = ctk.CTkFrame(top, fg_color="transparent")
        chips_row.grid(row=1, column=0, sticky="w")

        self.month_button = self._create_chip(chips_row, "", active=False,
                                              command=self._open_month_dialog, width=110)
        self.month_button.pack(side="left", padx=(0, 28))

        self.filters_wrap = ctk.CTkFrame(chips_row, fg_color="transparent")
        self.filters_wrap.pack(side="left")

    def _build_table(self) -> None:
        table_wrap = ctk.CTkFrame(self, fg_color="transparent")
        table_wrap.grid(row=2, column=0, sticky="nsew", padx=22, pady=(0, 22))
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(1, weight=1)

        self.table_header = ctk.CTkFrame(table_wrap, fg_color="#162034", corner_radius=8)
        self.table_header.grid(row=0, column=0, sticky="ew")
        self.table_header.grid_columnconfigure(0, weight=0, minsize=138)
        self.table_header.grid_columnconfigure(1, weight=1, minsize=280)
        self.table_header.grid_columnconfigure(2, weight=0, minsize=190)
        self.table_header.grid_columnconfigure(3, weight=0, minsize=134)

        self._header_label(self.table_header, 0, t("table.date"), "w")
        self._header_label(self.table_header, 1, t("table.description"), "w")
        self._header_label(self.table_header, 2, t("table.categories"), "w")
        amount_key = "table.amount" if self.tx_type == INCOME else "table.quantity"
        self._header_label(self.table_header, 3, t(amount_key), "e")

        self.body_scroll = ctk.CTkScrollableFrame(
            table_wrap, fg_color="transparent", corner_radius=0,
            scrollbar_button_color="#2A3A50", scrollbar_button_hover_color="#3A4A60",
        )
        self.body_scroll.grid(row=1, column=0, sticky="nsew", pady=(2, 0))
        self.body_scroll.grid_columnconfigure(0, weight=1)

        self.rows_container = ctk.CTkFrame(self.body_scroll, fg_color="transparent")
        self.rows_container.grid(row=0, column=0, sticky="ew")
        self.rows_container.grid_columnconfigure(0, weight=1)

    def _header_label(self, parent, column: int, text: str, anchor: str) -> None:
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color="#8A93A3", anchor=anchor,
                     ).grid(row=0, column=column, sticky="ew", padx=14, pady=9)

    def _render_filters(self) -> None:
        for widget in self.filters_wrap.winfo_children():
            widget.destroy()
        self.filter_buttons.clear()

        all_btn = self._create_chip(self.filters_wrap, t("txlist.all_categories"),
                                    active=self.selected_category_id is None,
                                    command=lambda: self._select_category(None))
        all_btn.pack(side="left", padx=(0, 10))
        self.filter_buttons[None] = all_btn

        for cat in self.repo.get_categories(self.user["id"], self.tx_type):
            btn = self._create_chip(self.filters_wrap, cat["name"],
                                    active=self.selected_category_id == cat["id"],
                                    command=lambda cid=cat["id"]: self._select_category(cid))
            btn.pack(side="left", padx=(0, 10))
            self.filter_buttons[cat["id"]] = btn

    def _create_chip(self, parent, text: str, active: bool, command=None, width: int = 96) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent, text=text, width=width, height=28, corner_radius=8,
            fg_color="#3FC2A3" if active else "#131D2C",
            hover_color="#36AF93" if active else "#1A2638",
            border_width=1, border_color="#3FC2A3" if active else "#233044",
            text_color="#07131C" if active else "#A4AFBE",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=command,
        )

    def _select_category(self, category_id: int | None) -> None:
        self.selected_category_id = category_id
        self._render_filters()
        self._render_rows()

    def _render_rows(self) -> None:
        for widget in self.rows_container.winfo_children():
            widget.destroy()

        rows = self.repo.get_transactions_for_page(
            user_id=self.user["id"],
            tx_type=self.tx_type,
            category_id=self.selected_category_id,
            year=self.selected_year,
            month=self.selected_month,
        )

        if not rows:
            empty = ctk.CTkFrame(self.rows_container, fg_color="#263241", corner_radius=0, height=54)
            empty.grid(row=0, column=0, sticky="ew")
            empty.grid_propagate(False)
            ctk.CTkLabel(empty, text=t("txlist.no_transactions"),
                         font=ctk.CTkFont(family="Segoe UI", size=14),
                         text_color="#7F899A",
                         ).place(relx=0.5, rely=0.5, anchor="center")
            return

        for index, row in enumerate(rows):
            rf = ctk.CTkFrame(self.rows_container, fg_color="#263241", corner_radius=0, height=36)
            rf.grid(row=index, column=0, sticky="ew", pady=(0, 2))
            rf.grid_propagate(False)
            rf.grid_columnconfigure(0, weight=0, minsize=138)
            rf.grid_columnconfigure(1, weight=1, minsize=280)
            rf.grid_columnconfigure(2, weight=0, minsize=190)
            rf.grid_columnconfigure(3, weight=0, minsize=134)

            self._row_text(rf, 0, self._format_date(row["created_at"]), "#F4F6FA", "w", 12)
            self._row_text(rf, 1, row["description"] or "-", "#9AA5B5", "w", 16)
            self._row_badge(rf, 2, row["category_name"])
            self._row_text(rf, 3, self._format_amount(row["amount"]), self.amount_color, "e", 13, "bold")

    def _row_text(self, parent, column: int, text: str, color: str,
                  anchor: str, size: int, weight: str = "normal") -> None:
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(family="Segoe UI", size=size, weight=weight),
                     text_color=color, anchor=anchor,
                     ).grid(row=0, column=column, sticky="ew", padx=14, pady=7)

    def _row_badge(self, parent, column: int, text: str) -> None:
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.grid(row=0, column=column, sticky="w", padx=14)
        ctk.CTkLabel(cell, text=text, fg_color="transparent",
                     text_color=self.badge_text,
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     ).pack(anchor="w")

    def _get_month_label(self) -> str:
        if self.selected_year is None or self.selected_month is None:
            return ""
        return f"{t(f'month.{self.selected_month}')} {self.selected_year}"

    def _ensure_selected_month(self) -> None:
        if self.selected_year is not None and self.selected_month is not None:
            return
        latest = self.repo.get_latest_transaction_for_type(self.user["id"], self.tx_type)
        dt = datetime.now() if latest is None else datetime.strptime(latest["created_at"], "%Y-%m-%d %H:%M:%S")
        self.selected_year = dt.year
        self.selected_month = dt.month

    def _open_month_dialog(self) -> None:
        self._ensure_selected_month()
        if self.month_dialog is not None and self.month_dialog.winfo_exists():
            self.month_dialog.focus_force()
            return
        self.month_dialog = MonthPickerDialog(
            self, self.selected_year, self.selected_month, self._on_month_selected)

    def _on_month_selected(self, year: int, month: int) -> None:
        self.selected_year = year
        self.selected_month = month
        self.month_button.configure(text=self._get_month_label())
        self._render_rows()
        self.month_dialog = None

    def _format_date(self, value: str) -> str:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return f"{dt.day:02d} {t(f'month_short.{dt.month}')},{dt.year}"

    def _format_amount(self, amount: float) -> str:
        sym = self.controller.currency_symbol
        return f"{amount:,.0f} {sym}".replace(",", " ")