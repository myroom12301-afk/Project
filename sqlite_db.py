from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


DEFAULT_DB_PATH = "personal_money.db"
DEFAULT_SCHEMA_PATH = "schema.sql"


class SQLiteDB:
    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_schema(self, schema_path: str = DEFAULT_SCHEMA_PATH) -> None:
        schema = Path(schema_path).read_text(encoding="utf-8")
        with self.connect() as conn:
            conn.executescript(schema)

    def add_user(self, name: str, base_currency: str, email: Optional[str] = None) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO users (email, name, base_currency)
                VALUES (?, ?, ?)
                """,
                (email, name, base_currency.upper()),
            )
            return int(cur.lastrowid)

    def add_account(
        self,
        user_id: int,
        name: str,
        account_type: str,
        currency: str,
        opening_balance: float = 0.0,
        current_balance: float = 0.0,
        is_archived: bool = False,
    ) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO accounts (user_id, name, type, currency, opening_balance, current_balance, is_archived)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    name,
                    account_type,
                    currency.upper(),
                    opening_balance,
                    current_balance,
                    int(is_archived),
                ),
            )
            return int(cur.lastrowid)

    def add_category(
        self,
        user_id: int,
        name: str,
        kind: str,
        parent_id: Optional[int] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        is_archived: bool = False,
    ) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO categories (user_id, name, kind, parent_id, icon, color, is_archived)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, name, kind, parent_id, icon, color, int(is_archived)),
            )
            return int(cur.lastrowid)

    def add_transaction(
        self,
        user_id: int,
        account_id: int,
        transaction_type: str,
        amount: float,
        currency: str,
        transaction_date: str,
        category_id: Optional[int] = None,
        description: Optional[str] = None,
        merchant: Optional[str] = None,
        status: str = "cleared",
        transfer_group_id: Optional[str] = None,
    ) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO transactions (
                    user_id, account_id, category_id, type, amount, currency,
                    transaction_date, description, merchant, status, transfer_group_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    account_id,
                    category_id,
                    transaction_type,
                    amount,
                    currency.upper(),
                    transaction_date,
                    description,
                    merchant,
                    status,
                    transfer_group_id,
                ),
            )
            return int(cur.lastrowid)

    def add_budget(
        self,
        user_id: int,
        category_id: int,
        period_type: str,
        period_start: str,
        period_end: str,
        amount_limit: float,
        rollover: bool = False,
    ) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO budgets (
                    user_id, category_id, period_type, period_start, period_end, amount_limit, rollover
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, category_id, period_type, period_start, period_end, amount_limit, int(rollover)),
            )
            return int(cur.lastrowid)

    def add_goal(
        self,
        user_id: int,
        name: str,
        target_amount: float,
        current_amount: float = 0.0,
        target_date: Optional[str] = None,
        linked_account_id: Optional[int] = None,
        status: str = "active",
    ) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO goals (
                    user_id, name, target_amount, current_amount, target_date, linked_account_id, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, name, target_amount, current_amount, target_date, linked_account_id, status),
            )
            return int(cur.lastrowid)


def seed_minimal_data(db: SQLiteDB) -> dict[str, int]:
    with db.connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (email, name, base_currency)
            VALUES (?, ?, ?)
            """,
            ("tanzir@example.com", "Tanzir Rahman", "USD"),
        )
        user_id = int(conn.execute("SELECT id FROM users WHERE email = ?", ("tanzir@example.com",)).fetchone()["id"])

        conn.execute(
            """
            INSERT OR IGNORE INTO accounts (user_id, name, type, currency, opening_balance, current_balance, is_archived)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (user_id, "Main Card", "card", "USD", 0, 0),
        )
        account_id = int(
            conn.execute(
                "SELECT id FROM accounts WHERE user_id = ? AND name = ? AND type = ?",
                (user_id, "Main Card", "card"),
            ).fetchone()["id"]
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO categories (user_id, name, kind, parent_id, icon, color, is_archived)
            VALUES (?, ?, ?, NULL, NULL, NULL, 0)
            """,
            (user_id, "Salary", "income"),
        )
        income_category_id = int(
            conn.execute(
                "SELECT id FROM categories WHERE user_id = ? AND name = ? AND kind = ?",
                (user_id, "Salary", "income"),
            ).fetchone()["id"]
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO categories (user_id, name, kind, parent_id, icon, color, is_archived)
            VALUES (?, ?, ?, NULL, NULL, NULL, 0)
            """,
            (user_id, "Food", "expense"),
        )
        expense_category_id = int(
            conn.execute(
                "SELECT id FROM categories WHERE user_id = ? AND name = ? AND kind = ?",
                (user_id, "Food", "expense"),
            ).fetchone()["id"]
        )

    return {
        "user_id": user_id,
        "account_id": account_id,
        "income_category_id": income_category_id,
        "expense_category_id": expense_category_id,
    }
