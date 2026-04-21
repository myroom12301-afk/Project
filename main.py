from __future__ import annotations

import math
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FinanceRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self._init_db()
        self._ensure_seed_data()

    def _init_db(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT NOT NULL,
                balance    INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name      TEXT NOT NULL,
                type      INTEGER NOT NULL,
                is_active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                category_id INTEGER NOT NULL REFERENCES categories(id),
                type        INTEGER NOT NULL,
                amount      INTEGER NOT NULL,
                description TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_transactions_user_id
                ON transactions(user_id);

            CREATE INDEX IF NOT EXISTS idx_transactions_created_at
                ON transactions(created_at);
            """
        )
        self.connection.commit()

    def _ensure_seed_data(self) -> None:
        stats_row = self.connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM users) AS user_count,
                (SELECT COUNT(*) FROM categories) AS category_count,
                (SELECT COUNT(*) FROM transactions) AS transaction_count
            """
        ).fetchone()
        if stats_row["user_count"] and stats_row["category_count"] and stats_row["transaction_count"]:
            user_row = self.connection.execute(
                "SELECT id FROM users ORDER BY id LIMIT 1"
            ).fetchone()
            self._recalculate_balance(user_row["id"])
            return

        self.reset_demo_data()

    def reset_demo_data(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM transactions")
            self.connection.execute("DELETE FROM categories")
            self.connection.execute("DELETE FROM users")
            self.connection.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'categories', 'transactions')")

        with self.connection:
            user_id = self.connection.execute(
                "INSERT INTO users (username) VALUES (?)",
                ("Tanzir Rahman",),
            ).lastrowid

            categories = [
                (user_id, "Зарплата", 1),
                (user_id, "Фриланс", 1),
                (user_id, "Кэшбек", 1),
                (user_id, "Прочее", 1),
                (user_id, "Магазины", 0),
                (user_id, "АЗС", 0),
                (user_id, "Аптека", 0),
                (user_id, "Прочее", 0),
            ]
            self.connection.executemany(
                "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
                categories,
            )

        category_map = {
            (row["name"], row["type"]): row["id"]
            for row in self.connection.execute(
                "SELECT id, name, type FROM categories WHERE user_id = ?",
                (user_id,),
            ).fetchall()
        }

        now = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        seed_transactions = [
            ("Зарплата за месяц", "Зарплата", 1, 145000.0, now - timedelta(days=6, hours=1)),
            ("Проект для клиента", "Фриланс", 1, 42000.0, now - timedelta(days=5, hours=3)),
            ("Кэшбек банка", "Кэшбек", 1, 2300.0, now - timedelta(days=4, hours=5)),
            ("Бонус", "Прочее", 1, 18000.0, now - timedelta(days=2, hours=2)),
            ("Покупка в магазине Globus", "Магазины", 0, 12150.0, now - timedelta(days=6, hours=2)),
            ("Заправка автомобиля", "АЗС", 0, 6250.0, now - timedelta(days=5, hours=1)),
            ("Аптека", "Аптека", 0, 4300.0, now - timedelta(days=3, hours=4)),
            ("Коммунальные платежи", "Прочее", 0, 27000.0, now - timedelta(days=2, hours=1)),
            ("Покупка техники", "Магазины", 0, 18500.0, now - timedelta(days=1, hours=3)),
            ("Повторная заправка", "АЗС", 0, 5100.0, now - timedelta(hours=6)),
        ]

        with self.connection:
            for description, category_name, tx_type, amount, created_at in seed_transactions:
                self.connection.execute(
                    """
                    INSERT INTO transactions (user_id, category_id, type, amount, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        category_map[(category_name, tx_type)],
                        tx_type,
                        int(round(amount * 100)),
                        description,
                        created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
        self._recalculate_balance(user_id)

    def _recalculate_balance(self, user_id: int) -> None:
        row = self.connection.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN type = 1 THEN amount ELSE -amount END), 0) AS balance
            FROM transactions
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
        with self.connection:
            self.connection.execute(
                "UPDATE users SET balance = ? WHERE id = ?",
                (row["balance"], user_id),
            )

    def get_default_user(self) -> sqlite3.Row:
        return self.connection.execute(
            "SELECT * FROM users ORDER BY id LIMIT 1"
        ).fetchone()

    def get_categories(self, user_id: int, tx_type: int | None = None) -> list[sqlite3.Row]:
        query = """
            SELECT id, name, type
            FROM categories
            WHERE user_id = ? AND is_active = 1
        """
        params: list[int] = [user_id]
        if tx_type is not None:
            query += " AND type = ?"
            params.append(tx_type)
        query += " ORDER BY name"
        return self.connection.execute(query, params).fetchall()

    def get_transactions(self, user_id: int, limit: int = 12) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT
                t.id,
                t.description,
                t.type,
                t.amount / 100.0 AS amount,
                t.created_at,
                c.name AS category_name,
                t.category_id
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.user_id = ?
            ORDER BY datetime(t.created_at) DESC, t.id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    def get_transaction(self, transaction_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT
                t.id,
                t.user_id,
                t.category_id,
                t.type,
                t.amount / 100.0 AS amount,
                t.description,
                t.created_at,
                c.name AS category_name
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.id = ?
            """,
            (transaction_id,),
        ).fetchone()

    def save_transaction(
        self,
        user_id: int,
        transaction_id: int | None,
        category_id: int,
        tx_type: int,
        amount: float,
        description: str,
    ) -> None:
        amount_cents = int(round(amount * 100))
        with self.connection:
            if transaction_id is None:
                self.connection.execute(
                    """
                    INSERT INTO transactions (user_id, category_id, type, amount, description)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, category_id, tx_type, amount_cents, description),
                )
            else:
                self.connection.execute(
                    """
                    UPDATE transactions
                    SET category_id = ?, type = ?, amount = ?, description = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (category_id, tx_type, amount_cents, description, transaction_id, user_id),
                )
        self._recalculate_balance(user_id)

    def delete_transaction(self, user_id: int, transaction_id: int) -> None:
        with self.connection:
            self.connection.execute(
                "DELETE FROM transactions WHERE id = ? AND user_id = ?",
                (transaction_id, user_id),
            )
        self._recalculate_balance(user_id)

    def get_dashboard_summary(self, user_id: int) -> dict:
        user = self.connection.execute(
            "SELECT username, balance FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

        income_rows = self.connection.execute(
            """
            SELECT c.name, SUM(t.amount) / 100.0 AS total
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.user_id = ? AND t.type = 1
            GROUP BY c.name
            ORDER BY total DESC
            """,
            (user_id,),
        ).fetchall()

        expense_rows = self.connection.execute(
            """
            SELECT c.name, SUM(t.amount) / 100.0 AS total
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.user_id = ? AND t.type = 0
            GROUP BY c.name
            ORDER BY total DESC
            """,
            (user_id,),
        ).fetchall()

        totals_row = self.connection.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN type = 1 THEN amount ELSE 0 END), 0) / 100.0 AS income,
                COALESCE(SUM(CASE WHEN type = 0 THEN amount ELSE 0 END), 0) / 100.0 AS expense
            FROM transactions
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        return {
            "username": user["username"],
            "balance": user["balance"] / 100.0,
            "income_breakdown": [(row["name"], row["total"]) for row in income_rows],
            "expense_breakdown": [(row["name"], row["total"]) for row in expense_rows],
            "total_income": totals_row["income"],
            "total_expense": totals_row["expense"],
        }

    def get_weekly_series(self, user_id: int) -> list[dict]:
        rows = self.connection.execute(
            """
            SELECT
                strftime('%w', created_at) AS weekday,
                type,
                SUM(amount) / 100.0 AS total
            FROM transactions
            WHERE user_id = ?
            GROUP BY weekday, type
            """,
            (user_id,),
        ).fetchall()

        day_names = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
        grouped: dict[int, dict[int, float]] = defaultdict(lambda: {0: 0.0, 1: 0.0})
        for row in rows:
            grouped[int(row["weekday"])][row["type"]] = row["total"] or 0.0

        return [
            {
                "day": day_names[index],
                "income": grouped[index][1],
                "expense": grouped[index][0],
            }
            for index in range(1, 7)
        ] + [
            {
                "day": "Вс",
                "income": grouped[0][1],
                "expense": grouped[0][0],
            }
        ]


class FinanceDashboardApp(ctk.CTk):
    SIDEBAR_ITEMS = [
        ("Обзор", "▣"),
        ("Конверт", "⇆"),
        ("Доходы", "$"),
        ("Расходы", "↧"),
        ("Категории", "◎"),
        ("Настройки", "⚙"),
    ]

    INCOME_COLORS = ["#47D45A", "#18C6B9", "#1AB6AF", "#8E99A8"]
    EXPENSE_COLORS = ["#FF544D", "#FF8A00", "#FFC533", "#8E99A8"]

    def __init__(self) -> None:
        super().__init__()
        self.title("Finebank Dashboard")
        self.geometry("1440x860")
        self.minsize(1320, 760)
        self.configure(fg_color="#0B1220")

        self.db_path = Path(__file__).with_name("finance.db")
        self.repo = FinanceRepository(self.db_path)
        self.user = self.repo.get_default_user()

        self.header_font = ctk.CTkFont(family="Segoe UI", size=32, weight="bold")
        self.body_font = ctk.CTkFont(family="Segoe UI", size=16)
        self.small_font = ctk.CTkFont(family="Segoe UI", size=13)
        self.title_font = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")

        self.placeholder_icon = self._create_icon_placeholder((24, 24))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self.refresh_dashboard()

    def _create_icon_placeholder(self, size: tuple[int, int]) -> ctk.CTkImage | None:
        # light_image=None, dark_image=None # ЗАМЕНИТЕ НА ПУТЬ К ВАШЕМУ ФАЙЛУ
        if Image is None or ImageDraw is None:
            return None
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((1, 1, size[0] - 2, size[1] - 2), radius=6, outline="#1ED3A7", width=2)
        draw.line((6, size[1] // 2, size[0] - 6, size[1] // 2), fill="#1ED3A7", width=2)
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#11192B")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)

        brand = ctk.CTkLabel(
            self.sidebar,
            text="FINEBANK.IO",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#F6F7FB",
        )
        brand.grid(row=0, column=0, padx=22, pady=(20, 36), sticky="w")

        self.menu_buttons: list[ctk.CTkButton] = []
        for index, (title, icon_text) in enumerate(self.SIDEBAR_ITEMS, start=1):
            active = index == 1
            button = ctk.CTkButton(
                self.sidebar,
                text=f"{icon_text}  {title}",
                image=self.placeholder_icon if active else None,
                compound="left",
                anchor="w",
                height=46,
                corner_radius=10,
                fg_color="#1C584F" if active else "transparent",
                hover_color="#16323A",
                text_color="#32E1B5" if active else "#7F899A",
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold" if active else "normal"),
                command=lambda name=title: self._set_active_menu(name),
            )
            button.grid(row=index, column=0, padx=18, pady=8, sticky="ew")
            self.menu_buttons.append(button)

        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=8, column=0, padx=18, pady=22, sticky="ew")
        avatar = ctk.CTkLabel(
            footer,
            text="◕",
            width=36,
            height=36,
            fg_color="#1ED3A7",
            corner_radius=18,
            text_color="#0C1527",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        avatar.pack(side="left", padx=(0, 12))
        user_block = ctk.CTkFrame(footer, fg_color="transparent")
        user_block.pack(side="left", fill="x", expand=True)
        self.footer_name = ctk.CTkLabel(
            user_block,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color="#F2F4F8",
        )
        self.footer_name.pack(anchor="w")

    def _build_main_area(self) -> None:
        self.main = ctk.CTkFrame(self, fg_color="#0B1220", corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_top_cards()
        self._build_bottom_section()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self.main, fg_color="transparent")
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
        cards = ctk.CTkFrame(self.main, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", padx=22, pady=(8, 18))
        cards.grid_columnconfigure(1, weight=1)

        self.balance_card = ctk.CTkFrame(cards, width=330, height=220, corner_radius=18, fg_color="#202B3C")
        self.balance_card.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        self.balance_card.grid_propagate(False)

        balance_title = ctk.CTkLabel(
            self.balance_card,
            text="Общий баланс",
            font=self.body_font,
            text_color="#8E99A8",
        )
        balance_title.pack(anchor="w", padx=22, pady=(18, 10))

        self.balance_value_label = ctk.CTkLabel(
            self.balance_card,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=46, weight="bold"),
            text_color="#F8F9FB",
        )
        self.balance_value_label.pack(anchor="w", padx=22, pady=(0, 24))

        add_button = ctk.CTkButton(
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
        )
        add_button.pack(anchor="center")

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
        bottom = ctk.CTkFrame(self.main, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=22, pady=(0, 20))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_rowconfigure(0, weight=1)

        self.transactions_panel = ctk.CTkFrame(bottom, corner_radius=18, fg_color="#202B3C")
        self.transactions_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.transactions_panel.grid_columnconfigure(0, weight=1)
        self.transactions_panel.grid_rowconfigure(1, weight=1)

        tx_title = ctk.CTkLabel(
            self.transactions_panel,
            text="Недавние транзакции",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#F7F8FC",
        )
        tx_title.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        self._build_transaction_table()

        self.chart_panel = ctk.CTkFrame(bottom, corner_radius=18, fg_color="#202B3C")
        self.chart_panel.grid(row=0, column=1, sticky="nsew")
        self.chart_panel.grid_columnconfigure(0, weight=1)
        self.chart_panel.grid_rowconfigure(1, weight=1)

        chart_title = ctk.CTkLabel(
            self.chart_panel,
            text="График доходов и расходов",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#F7F8FC",
        )
        chart_title.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        self.weekly_total_label = ctk.CTkLabel(
            self.chart_panel,
            text="",
            font=self.small_font,
            text_color="#D8DEE8",
        )
        self.weekly_total_label.grid(row=0, column=0, sticky="e", padx=18, pady=(18, 10))

        self.bar_canvas = tk.Canvas(self.chart_panel, bg="#202B3C", highlightthickness=0)
        self.bar_canvas.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 8))
        self.bar_canvas.bind("<Configure>", lambda _: self._draw_weekly_chart())

        legend = ctk.CTkFrame(self.chart_panel, fg_color="transparent")
        legend.grid(row=2, column=0, pady=(0, 16))
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

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _legend_item(self, parent: ctk.CTkFrame, color: str, text: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        dot = ctk.CTkLabel(frame, text="■", text_color=color, font=ctk.CTkFont(size=14))
        dot.pack(side="left", padx=(0, 6))
        label = ctk.CTkLabel(frame, text=text, text_color="#D6DBE5", font=self.small_font)
        label.pack(side="left")
        return frame

    def _set_active_menu(self, selected: str) -> None:
        for button, (title, _) in zip(self.menu_buttons, self.SIDEBAR_ITEMS):
            is_active = title == selected
            button.configure(
                fg_color="#1C584F" if is_active else "transparent",
                text_color="#32E1B5" if is_active else "#7F899A",
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold" if is_active else "normal"),
            )

    def _on_add_transaction(self) -> None:
        return

    def refresh_dashboard(self) -> None:
        self.user = self.repo.get_default_user()
        summary = self.repo.get_dashboard_summary(self.user["id"])
        self.footer_name.configure(text=summary["username"])
        self.greeting_label.configure(text=f"Hello {summary['username']}")
        self.date_label.configure(text=datetime.now().strftime("%B %d, %Y"))
        self.balance_value_label.configure(text=self._format_currency(summary["balance"]))

        self._fill_transactions()
        self._draw_donut(
            self.income_canvas,
            "Доходы",
            summary["income_breakdown"],
            self.INCOME_COLORS,
        )
        self._draw_legend(self.income_legend, summary["income_breakdown"], self.INCOME_COLORS)
        self._draw_donut(
            self.expense_canvas,
            "Расходы",
            summary["expense_breakdown"],
            self.EXPENSE_COLORS,
        )
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

    def _populate_categories(self) -> None:
        tx_type = 1 if self.type_var.get() == "Доход" else 0
        categories = self.repo.get_categories(self.user["id"], tx_type=tx_type)
        if not categories:
            self.category_name_to_id = {}
            self.category_menu.configure(values=["Нет категорий"])
            self.category_var.set("Нет категорий")
            return

        names = [row["name"] for row in categories]
        self.category_name_to_id = {row["name"]: row["id"] for row in categories}
        self.category_menu.configure(values=names)
        if self.category_var.get() not in names:
            self.category_var.set(names[0])

    def _draw_legend(self, parent: ctk.CTkFrame, items: list[tuple[str, float]], colors: list[str]) -> None:
        for child in parent.winfo_children():
            child.destroy()

        display_items = items[:4] if items else [("Прочее", 1.0)]
        for index, (name, _) in enumerate(display_items):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(anchor="w", pady=3)
            dot = ctk.CTkLabel(row, text="●", text_color=colors[index % len(colors)], font=ctk.CTkFont(size=16))
            dot.pack(side="left", padx=(0, 8))
            label = ctk.CTkLabel(row, text=name, text_color="#EFF3FA", font=self.small_font)
            label.pack(side="left")

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
        if not hasattr(self, "bar_canvas"):
            return

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

    def _on_transaction_selected(self, _: object) -> None:
        selected = self.tree.selection()
        if not selected:
            return

        return

    @staticmethod
    def _format_currency(value: float) -> str:
        return f"${value:,.0f}"

    @staticmethod
    def _format_short_date(value: str) -> str:
        try:
            date_value = datetime.fromisoformat(value)
            return date_value.strftime("%d.%m, %H:%M")
        except ValueError:
            return value


if __name__ == "__main__":
    app = FinanceDashboardApp()
    app.mainloop()
