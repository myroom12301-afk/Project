from __future__ import annotations

import math
import tkinter as tk
from datetime import datetime
from tkinter import ttk

import customtkinter as ctk

from .base_page import BasePage


class DashboardPage(BasePage):
    INCOME_COLORS = ["#47D45A", "#18C6B9", "#1AB6AF", "#8E99A8"]
    EXPENSE_COLORS = ["#FF544D", "#FF8A00", "#FFC533", "#8E99A8"]

    def __init__(self, master, controller) -> None:
        super().__init__(master, controller)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.small_font = ctk.CTkFont(family="Segoe UI", size=13)
        self.body_font = ctk.CTkFont(family="Segoe UI", size=16)

        self._build_header()
        self._build_top_cards()
        self._build_bottom_section()

    @property
    def repo(self):
        return self.controller.repo

    @property
    def user(self):
        return self.controller.user

    def on_show(self) -> None:
        self.refresh()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(12, 10))
        header.grid_columnconfigure(0, weight=1)

        self.greeting_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=28),
            text_color="#F6F7FB",
        )
        self.greeting_label.grid(row=0, column=0, sticky="w")

        self.date_label = ctk.CTkLabel(
            header,
            text="",
            font=self.small_font,
            text_color="#7D8798",
        )
        self.date_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        separator = ctk.CTkFrame(header, height=1, fg_color="#5B6472")
        separator.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    def _build_top_cards(self) -> None:
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", padx=22, pady=(8, 18))
        cards.grid_columnconfigure(1, weight=1)

        self.balance_card = ctk.CTkFrame(cards, width=330, height=220, corner_radius=18, fg_color="#202B3C")
        self.balance_card.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        self.balance_card.grid_propagate(False)

        ctk.CTkLabel(
            self.balance_card,
            text="Общий баланс",
            font=self.body_font,
            text_color="#8E99A8",
        ).pack(anchor="w", padx=22, pady=(18, 10))

        self.balance_value_label = ctk.CTkLabel(
            self.balance_card,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=46, weight="bold"),
            text_color="#F8F9FB",
        )
        self.balance_value_label.pack(anchor="w", padx=22, pady=(0, 24))

        ctk.CTkButton(
            self.balance_card,
            text="+Транзакцию",
            width=190,
            height=42,
            corner_radius=10,
            fg_color="#229D84",
            hover_color="#1E816D",
            text_color="#ECFFFC",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            command=self._on_add_transaction,
        ).pack(anchor="center")

        self.analytics_card = ctk.CTkFrame(cards, height=220, corner_radius=18, fg_color="#202B3C")
        self.analytics_card.grid(row=0, column=1, sticky="nsew")
        self.analytics_card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.income_canvas = tk.Canvas(self.analytics_card, width=170, height=170, bg="#202B3C", highlightthickness=0)
        self.income_canvas.grid(row=0, column=0, padx=(26, 8), pady=22)
        self.income_legend = ctk.CTkFrame(self.analytics_card, fg_color="transparent")
        self.income_legend.grid(row=0, column=1, sticky="w")

        self.expense_canvas = tk.Canvas(self.analytics_card, width=170, height=170, bg="#202B3C", highlightthickness=0)
        self.expense_canvas.grid(row=0, column=2, padx=(10, 8), pady=22)
        self.expense_legend = ctk.CTkFrame(self.analytics_card, fg_color="transparent")
        self.expense_legend.grid(row=0, column=3, sticky="w", padx=(0, 16))

    def _build_bottom_section(self) -> None:
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=22, pady=(0, 20))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_rowconfigure(0, weight=1)

        self.transactions_panel = ctk.CTkFrame(bottom, corner_radius=18, fg_color="#202B3C")
        self.transactions_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.transactions_panel.grid_columnconfigure(0, weight=1)
        self.transactions_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.transactions_panel,
            text="Недавние транзакции",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#F7F8FC",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        self._build_transaction_table()

        self.chart_panel = ctk.CTkFrame(bottom, corner_radius=18, fg_color="#202B3C")
        self.chart_panel.grid(row=0, column=1, sticky="nsew")
        self.chart_panel.grid_columnconfigure(0, weight=1)
        self.chart_panel.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.chart_panel,
            text="График доходов и расходов",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#F7F8FC",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 2))

        self.weekly_total_label = ctk.CTkLabel(
            self.chart_panel,
            text="",
            font=self.small_font,
            text_color="#D8DEE8",
        )
        self.weekly_total_label.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        self.bar_canvas = tk.Canvas(self.chart_panel, bg="#202B3C", highlightthickness=0)
        self.bar_canvas.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 8))
        self.bar_canvas.bind("<Configure>", lambda _: self._draw_weekly_chart())

        legend = ctk.CTkFrame(self.chart_panel, fg_color="transparent")
        legend.grid(row=3, column=0, pady=(0, 16))
        self._legend_item(legend, "#29E073", "Доходы").pack(side="left", padx=12)
        self._legend_item(legend, "#FF613E", "Расходы").pack(side="left", padx=12)

    def _build_transaction_table(self) -> None:
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Dashboard.Treeview",
            background="#202B3C",
            fieldbackground="#202B3C",
            foreground="#EDF2FA",
            rowheight=40,
            borderwidth=0,
            font=("Segoe UI", 12),
        )
        style.configure(
            "Dashboard.Treeview.Heading",
            background="#1A2435",
            foreground="#A6B1C1",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
        )
        style.map("Dashboard.Treeview", background=[("selected", "#294454")], foreground=[("selected", "#FFFFFF")])
        style.configure(
            "Dashboard.Vertical.TScrollbar",
            troughcolor="#202B3C",
            background="#2A3A50",
            arrowcolor="#5A6A7E",
            bordercolor="#202B3C",
            lightcolor="#202B3C",
            darkcolor="#202B3C",
            relief="flat",
        )
        style.map(
            "Dashboard.Vertical.TScrollbar",
            background=[("active", "#3A4A60"), ("pressed", "#3A4A60")],
        )

        table_wrap = ctk.CTkFrame(self.transactions_panel, fg_color="transparent")
        table_wrap.grid(row=1, column=0, sticky="nsew", padx=18)
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_wrap,
            columns=("id", "description", "category", "date", "amount"),
            show="headings",
            style="Dashboard.Treeview",
            selectmode="browse",
            height=7,
        )
        for column, text, width in (
            ("id", "ID", 45),
            ("description", "Описание", 230),
            ("category", "Категория", 120),
            ("date", "Дата", 120),
            ("amount", "Сумма", 100),
        ):
            self.tree.heading(column, text=text)
            self.tree.column(column, width=width, anchor="w")

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_transaction_selected)

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview, style="Dashboard.Vertical.TScrollbar")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _legend_item(self, parent: ctk.CTkFrame, color: str, text: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(frame, text="■", text_color=color, font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(frame, text=text, text_color="#D6DBE5", font=self.small_font).pack(side="left")
        return frame

    def refresh(self) -> None:
        self.controller.refresh_user()
        summary = self.repo.get_dashboard_summary(self.user["id"])
        self.controller.sidebar.set_username(summary["username"])
        self.greeting_label.configure(text=f"Hello {summary['username']}")
        self.date_label.configure(text=datetime.now().strftime("%B %d, %Y"))
        balance_text = self._format_currency(summary["balance"])
        self.balance_value_label.configure(
            text=balance_text,
            font=ctk.CTkFont(family="Segoe UI", size=self._balance_font_size(balance_text), weight="bold"),
        )

        self._fill_transactions()
        self._draw_donut(self.income_canvas, "Доходы", summary["income_breakdown"], self.INCOME_COLORS)
        self._draw_legend(self.income_legend, summary["income_breakdown"], self.INCOME_COLORS)
        self._draw_donut(self.expense_canvas, "Расходы", summary["expense_breakdown"], self.EXPENSE_COLORS)
        self._draw_legend(self.expense_legend, summary["expense_breakdown"], self.EXPENSE_COLORS)
        self._draw_weekly_chart()

    def _fill_transactions(self) -> None:
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)

        for row in self.repo.get_transactions(self.user["id"], limit=12):
            amount_prefix = "+" if row["type"] == 1 else "-"
            self.tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["id"],
                    row["description"],
                    row["category_name"],
                    self._format_short_date(row["created_at"]),
                    f"{amount_prefix}{row['amount']:,.0f}$",
                ),
            )

    def _draw_legend(self, parent: ctk.CTkFrame, items: list[tuple[str, float]], colors: list[str]) -> None:
        for child in parent.winfo_children():
            child.destroy()

        display_items = items[:4] if items else [("Прочее", 1.0)]
        for index, (name, _) in enumerate(display_items):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(anchor="w", pady=3)
            ctk.CTkLabel(
                row,
                text="●",
                text_color=colors[index % len(colors)],
                font=ctk.CTkFont(size=16),
            ).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(row, text=name, text_color="#EFF3FA", font=self.small_font).pack(side="left")

    def _draw_donut(
        self,
        canvas: tk.Canvas,
        label: str,
        items: list[tuple[str, float]],
        colors: list[str],
    ) -> None:
        canvas.delete("all")
        display_items = items[:4] if items else [("Прочее", 1.0)]
        total = sum(value for _, value in display_items) or 1.0
        canvas.create_oval(18, 18, 152, 152, outline="#314056", width=18)
        start = 90

        for index, (_, value) in enumerate(display_items):
            extent = (value / total) * 360
            color = colors[index % len(colors)]
            if math.isclose(extent, 360.0, rel_tol=0.0, abs_tol=0.01):
                canvas.create_oval(18, 18, 152, 152, outline=color, width=18)
            else:
                canvas.create_arc(
                    18,
                    18,
                    152,
                    152,
                    start=start,
                    extent=-extent,
                    style="arc",
                    outline=color,
                    width=18,
                )
            start -= extent

        canvas.create_text(85, 78, text=label, fill="#F6F7FB", font=("Segoe UI", 16, "bold"))

    def _draw_weekly_chart(self) -> None:
        canvas = self.bar_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 520)
        height = max(canvas.winfo_height(), 300)
        canvas.configure(width=width, height=height)

        series = self.repo.get_weekly_series(self.user["id"])
        max_value = max([item["income"] for item in series] + [item["expense"] for item in series] + [1.0])
        max_value = math.ceil(max_value / 10000) * 10000
        top_padding = 32
        bottom_padding = 48
        left_padding = 52
        chart_height = height - top_padding - bottom_padding
        chart_width = width - left_padding - 24
        grid_steps = 5

        total_income = sum(item["income"] for item in series)
        total_expense = sum(item["expense"] for item in series)
        self.weekly_total_label.configure(
            text=f"Всего за неделю: Доходы +{total_income:,.0f} | Расходы -{total_expense:,.0f}"
        )

        for step in range(grid_steps + 1):
            y = top_padding + chart_height * step / grid_steps
            value = max_value - (max_value / grid_steps) * step
            canvas.create_line(left_padding, y, width - 20, y, fill="#58606D", dash=(6, 4))
            canvas.create_text(left_padding - 8, y, text=f"{value:,.0f}", fill="#A8B0BF", font=("Segoe UI", 10), anchor="e")

        base_y = top_padding + chart_height
        group_width = chart_width / max(len(series), 1)
        bar_width = min(18, group_width / 3)

        for index, item in enumerate(series):
            x_center = left_padding + group_width * index + group_width / 2
            income_height = 0 if max_value == 0 else (item["income"] / max_value) * chart_height
            expense_height = 0 if max_value == 0 else (item["expense"] / max_value) * chart_height

            canvas.create_rectangle(
                x_center - bar_width - 3,
                base_y - income_height,
                x_center - 3,
                base_y,
                fill="#29E073",
                width=0,
            )
            canvas.create_rectangle(
                x_center + 3,
                base_y - expense_height,
                x_center + bar_width + 3,
                base_y,
                fill="#FF613E",
                width=0,
            )
            canvas.create_text(x_center, height - 20, text=item["day"], fill="#A9B1C0", font=("Segoe UI", 10))

    def _on_add_transaction(self) -> None:
        from .transaction_dialog import TransactionDialog
        TransactionDialog(self, self.controller, on_saved=self.refresh)

    def _on_transaction_selected(self, _: object) -> None:
        selected = self.tree.selection()
        if not selected:
            return

        return

    @staticmethod
    def _format_currency(value: float) -> str:
        sign = "-" if value < 0 else ""
        abs_val = abs(value)
        if abs_val >= 1_000_000_000_000:
            return f"{sign}${abs_val / 1_000_000_000_000:.1f}Трлн"
        if abs_val >= 1_000_000_000:
            return f"{sign}${abs_val / 1_000_000_000:.1f}Млрд"
        return f"{sign}${abs_val:,.0f}"

    @staticmethod
    def _balance_font_size(text: str) -> int:
        n = len(text)
        if n <= 8:   return 46
        if n <= 11:  return 36
        if n <= 14:  return 28
        return 22

    @staticmethod
    def _format_short_date(value: str) -> str:
        try:
            date_value = datetime.fromisoformat(value)
            return date_value.strftime("%d.%m, %H:%M")
        except ValueError:
            return value
