from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


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
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name       TEXT NOT NULL,
                type       INTEGER NOT NULL,
                is_active  INTEGER DEFAULT 1,
                is_default INTEGER DEFAULT 0
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
        # migrate: add is_default if it doesn't exist yet
        try:
            self.connection.execute("ALTER TABLE categories ADD COLUMN is_default INTEGER DEFAULT 0")
            self.connection.commit()
        except Exception:
            pass
        # migrate: add description column
        try:
            self.connection.execute("ALTER TABLE categories ADD COLUMN description TEXT DEFAULT ''")
            self.connection.commit()
        except Exception:
            pass
        # migrate: mark seed categories as default if none are marked yet
        unmarked = self.connection.execute(
            "SELECT COUNT(*) FROM categories WHERE is_default = 1"
        ).fetchone()[0]
        if unmarked == 0 and self.connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0] > 0:
            seed_names_expense = ("Магазины", "АЗС", "Аптека", "Прочее")
            seed_names_income = ("Зарплата", "Фриланс", "Кэшбек", "Прочее")
            with self.connection:
                self.connection.execute(
                    "UPDATE categories SET is_default=1 WHERE type=0 AND name IN ({})".format(
                        ",".join("?" * len(seed_names_expense))
                    ),
                    seed_names_expense,
                )
                self.connection.execute(
                    "UPDATE categories SET is_default=1 WHERE type=1 AND name IN ({})".format(
                        ",".join("?" * len(seed_names_income))
                    ),
                    seed_names_income,
                )

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
            self.connection.execute(
                "DELETE FROM sqlite_sequence WHERE name IN ('users', 'categories', 'transactions')"
            )

        with self.connection:
            user_id = self.connection.execute(
                "INSERT INTO users (username) VALUES (?)",
                ("Tanzir Rahman",),
            ).lastrowid

            categories = [
                (user_id, "Зарплата", 1, 1),
                (user_id, "Фриланс", 1, 1),
                (user_id, "Кэшбек", 1, 1),
                (user_id, "Прочее", 1, 1),
                (user_id, "Магазины", 0, 1),
                (user_id, "АЗС", 0, 1),
                (user_id, "Аптека", 0, 1),
                (user_id, "Прочее", 0, 1),
            ]
            self.connection.executemany(
                "INSERT INTO categories (user_id, name, type, is_default) VALUES (?, ?, ?, ?)",
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
            SELECT id, name, type, is_default, description
            FROM categories
            WHERE user_id = ? AND is_active = 1
        """
        params: list[int] = [user_id]
        if tx_type is not None:
            query += " AND type = ?"
            params.append(tx_type)
        query += " ORDER BY is_default DESC, name"
        return self.connection.execute(query, params).fetchall()

    def delete_category(self, category_id: int) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE categories SET is_active = 0 WHERE id = ?",
                (category_id,),
            )

    def add_category(self, user_id: int, name: str, tx_type: int, description: str = "") -> int:
        with self.connection:
            return self.connection.execute(
                "INSERT INTO categories (user_id, name, type, is_default, description) VALUES (?, ?, ?, 0, ?)",
                (user_id, name, tx_type, description),
            ).lastrowid

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
