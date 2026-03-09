from __future__ import annotations

import sqlite3
from typing import Optional


DEFAULT_DB_PATH = "personal_money.db"


DDL_SQL = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    name TEXT NOT NULL,
    base_currency TEXT NOT NULL CHECK (length(base_currency) = 3),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('cash', 'card', 'bank', 'crypto', 'savings')),
    currency TEXT NOT NULL CHECK (length(currency) = 3),
    opening_balance NUMERIC NOT NULL DEFAULT 0 CHECK (opening_balance >= 0),
    current_balance NUMERIC NOT NULL DEFAULT 0,
    is_archived INTEGER NOT NULL DEFAULT 0 CHECK (is_archived IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('income', 'expense', 'transfer')),
    parent_id INTEGER,
    icon TEXT,
    color TEXT,
    is_archived INTEGER NOT NULL DEFAULT 0 CHECK (is_archived IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    UNIQUE (user_id, name, kind)
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    category_id INTEGER,
    type TEXT NOT NULL CHECK (type IN ('income', 'expense', 'transfer')),
    amount NUMERIC NOT NULL CHECK (amount > 0),
    currency TEXT NOT NULL CHECK (length(currency) = 3),
    transaction_date TEXT NOT NULL,
    description TEXT,
    merchant TEXT,
    status TEXT NOT NULL DEFAULT 'cleared' CHECK (status IN ('planned', 'cleared', 'reconciled')),
    transfer_group_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE RESTRICT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('weekly', 'monthly', 'yearly')),
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    amount_limit NUMERIC NOT NULL CHECK (amount_limit > 0),
    rollover INTEGER NOT NULL DEFAULT 0 CHECK (rollover IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE (user_id, category_id, period_start, period_end)
);

CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    target_amount NUMERIC NOT NULL CHECK (target_amount > 0),
    current_amount NUMERIC NOT NULL DEFAULT 0 CHECK (current_amount >= 0),
    target_date TEXT,
    linked_account_id INTEGER,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (linked_account_id) REFERENCES accounts(id) ON DELETE SET NULL
);

CREATE INDEX idx_accounts_user ON accounts(user_id);
CREATE INDEX idx_categories_user_kind_archived ON categories(user_id, kind, is_archived);
CREATE INDEX idx_transactions_user_date_desc ON transactions(user_id, transaction_date DESC);
CREATE INDEX idx_transactions_account_date_desc ON transactions(account_id, transaction_date DESC);
CREATE INDEX idx_transactions_category_date_desc ON transactions(category_id, transaction_date DESC);
CREATE INDEX idx_budgets_user_period ON budgets(user_id, period_start, period_end);
CREATE INDEX idx_goals_user_status ON goals(user_id, status);
"""


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def recreate_tables(db_path: str = DEFAULT_DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(DDL_SQL)


def add_user(name: str, base_currency: str, email: Optional[str] = None, db_path: str = DEFAULT_DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO users (email, name, base_currency) VALUES (?, ?, ?)",
            (email, name, base_currency.upper()),
        )
        return int(cur.lastrowid)


def add_account(
    user_id: int,
    name: str,
    account_type: str,
    currency: str,
    opening_balance: float = 0.0,
    current_balance: float = 0.0,
    is_archived: bool = False,
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO accounts (user_id, name, type, currency, opening_balance, current_balance, is_archived)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, account_type, currency.upper(), opening_balance, current_balance, int(is_archived)),
        )
        return int(cur.lastrowid)


def add_category(
    user_id: int,
    name: str,
    kind: str,
    parent_id: Optional[int] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
    is_archived: bool = False,
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO categories (user_id, name, kind, parent_id, icon, color, is_archived)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, kind, parent_id, icon, color, int(is_archived)),
        )
        return int(cur.lastrowid)


def add_transaction(
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
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO transactions (
                user_id, account_id, category_id, type, amount, currency,
                transaction_date, description, merchant, status, transfer_group_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    user_id: int,
    category_id: int,
    period_type: str,
    period_start: str,
    period_end: str,
    amount_limit: float,
    rollover: bool = False,
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO budgets (user_id, category_id, period_type, period_start, period_end, amount_limit, rollover)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, category_id, period_type, period_start, period_end, amount_limit, int(rollover)),
        )
        return int(cur.lastrowid)


def add_goal(
    user_id: int,
    name: str,
    target_amount: float,
    current_amount: float = 0.0,
    target_date: Optional[str] = None,
    linked_account_id: Optional[int] = None,
    status: str = "active",
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO goals (user_id, name, target_amount, current_amount, target_date, linked_account_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, target_amount, current_amount, target_date, linked_account_id, status),
        )
        return int(cur.lastrowid)
