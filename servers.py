import sqlite3

DB_PATH = "finance.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON;")


# ---------------------------------------------------------------------------
# 1. init_db — создание схемы
# ---------------------------------------------------------------------------

def init_db():
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   VARCHAR NOT NULL,
            balance    INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name      VARCHAR NOT NULL,
            type      BOOLEAN NOT NULL,        -- 1 = доход, 0 = расход
            is_active BOOLEAN DEFAULT 1        -- soft delete flag
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL REFERENCES categories(id),
            type        BOOLEAN NOT NULL,      -- 1 = доход, 0 = расход
            amount      INTEGER NOT NULL,      -- в копейках
            description VARCHAR,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- индексы для быстрого поиска транзакций по пользователю и дате
        CREATE INDEX IF NOT EXISTS idx_transactions_user_id
            ON transactions(user_id);

        CREATE INDEX IF NOT EXISTS idx_transactions_created_at
            ON transactions(created_at);
    """)


# ---------------------------------------------------------------------------
# 2. create_user
# ---------------------------------------------------------------------------

def create_user(username: str) -> int:
    """
    Создаёт пользователя и возвращает его id.
    Raises ValueError при пустом имени.
    """
    if not username or not username.strip():
        raise ValueError("username не может быть пустым")

    with conn:
        cursor = conn.execute(
            "INSERT INTO users (username) VALUES (?);",
            (username.strip(),)
        )
        return cursor.lastrowid


# ---------------------------------------------------------------------------
# 3. add_category
# ---------------------------------------------------------------------------

def add_category(user_id: int, name: str, type: int) -> int:
    """    type: 1 — доход, 0 — расход.    """
    if type not in (0, 1):
        raise ValueError("type должен быть 0 (расход) или 1 (доход)")
    if not name or not name.strip():
        raise ValueError("name категории не может быть пустым")

    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?);",
                (user_id, name.strip(), type)
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Пользователь с id={user_id} не существует") from e


# ---------------------------------------------------------------------------
# 4. delete_category (soft delete)
# ---------------------------------------------------------------------------

def delete_category(category_id: int) -> bool:
    """
    Мягкое удаление категории — устанавливает is_active = 0.
    Возвращает True если запись найдена и обновлена, False иначе.
    """
    with conn:
        cursor = conn.execute(
            "UPDATE categories SET is_active = 0 WHERE id = ?;",
            (category_id,)
        )
        return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# 5. add_transaction
# ---------------------------------------------------------------------------

def add_transaction(user_id: int, category_id: int, type: int, amount: float, description: str = None):
    """
    Добавляет транзакцию и атомарно обновляет баланс пользователя.

    amount   — сумма в рублях/гривнах (например, 150.50); внутри конвертируется
               в копейки: 15050.
    type     — 1 увеличивает баланс, 0 — уменьшает.
    Возвращает id созданной транзакции.
    """
    if type not in (0, 1):
        raise ValueError("type должен быть 0 (расход) или 1 (доход)")
    if amount <= 0:
        raise ValueError("amount должен быть положительным числом")

    amount_coins = round(amount * 100)
    balance_delta = amount_coins if type == 1 else -amount_coins

    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO transactions (user_id, category_id, type, amount, description)
                VALUES (?, ?, ?, ?, ?);
                """,
                (user_id, category_id, type, amount_coins, description)
            )
            transaction_id = cursor.lastrowid

            conn.execute(
                "UPDATE users SET balance = balance + ? WHERE id = ?;",
                (balance_delta, user_id)
            )

            return transaction_id
    except sqlite3.IntegrityError as e:
        raise ValueError(
            f"Ошибка внешнего ключа (user_id={user_id}, category_id={category_id})"
        ) from e


# ---------------------------------------------------------------------------
# 6. get_user_transactions
# ---------------------------------------------------------------------------

def get_user_transactions(user_id: int, limit: int = 50):
    """
    Возвращает историю транзакций пользователя (новые — первыми).
    Суммы возвращаются в рублях (делятся на 100).
    JOIN с categories для получения названия категории.
    """
    with conn:
        rows = conn.execute(
            """
            SELECT
                t.id,
                t.type,
                t.amount / 100.0        AS amount,
                t.description,
                t.created_at,
                c.name                  AS category_name
            FROM transactions t
            LEFT JOIN categories c ON c.id = t.category_id
            WHERE t.user_id = ?
            ORDER BY t.created_at DESC
            LIMIT ?;
            """,
            (user_id, limit)
        ).fetchall()

    return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# 7. get_weekly_comparison
# ---------------------------------------------------------------------------

def get_weekly_comparison(user_id: int) -> dict:
    """
    Аналитика: сравнение текущей и прошлой недели.
    Неделя считается с понедельника (ISO).

    Возвращает словарь с ключами:
        current_week_income, current_week_expense,
        prev_week_income,    prev_week_expense
    Все суммы в рублях.
    """
    with conn:
        row = conn.execute(
            """
            SELECT
                -- доходы текущей недели (пн–вс по ISO)
                SUM(CASE
                    WHEN type = 1
                     AND DATE(created_at) >= DATE('now', 'weekday 0', '-6 days')
                    THEN amount ELSE 0 END) / 100.0  AS current_week_income,

                -- расходы текущей недели
                SUM(CASE
                    WHEN type = 0
                     AND DATE(created_at) >= DATE('now', 'weekday 0', '-6 days')
                    THEN amount ELSE 0 END) / 100.0  AS current_week_expense,

                -- доходы прошлой недели
                SUM(CASE
                    WHEN type = 1
                     AND DATE(created_at) >= DATE('now', 'weekday 0', '-13 days')
                     AND DATE(created_at) <  DATE('now', 'weekday 0', '-6 days')
                    THEN amount ELSE 0 END) / 100.0  AS prev_week_income,

                -- расходы прошлой недели
                SUM(CASE
                    WHEN type = 0
                     AND DATE(created_at) >= DATE('now', 'weekday 0', '-13 days')
                     AND DATE(created_at) <  DATE('now', 'weekday 0', '-6 days')
                    THEN amount ELSE 0 END) / 100.0  AS prev_week_expense

            FROM transactions
            WHERE user_id = ?;
            """,
            (user_id,)
        ).fetchone()

    return {
        "current_week_income":  row["current_week_income"]  or 0.0,
        "current_week_expense": row["current_week_expense"] or 0.0,
        "prev_week_income":     row["prev_week_income"]     or 0.0,
        "prev_week_expense":    row["prev_week_expense"]    or 0.0,
    } #Переделать эту часть при создании приложения


# ---------------------------------------------------------------------------
# 8. get_all_time_stats
# ---------------------------------------------------------------------------

def get_all_time_stats(user_id: int) -> dict:
    """
    Возвращает суммарный доход и суммарный расход пользователя за всё время.
    Суммы в рублях.
    """
    with conn:
        row = conn.execute(
            """
            SELECT
                SUM(CASE WHEN type = 1 THEN amount ELSE 0 END) / 100.0 AS total_income,
                SUM(CASE WHEN type = 0 THEN amount ELSE 0 END) / 100.0 AS total_expense
            FROM transactions
            WHERE user_id = ?;
            """,
            (user_id,)
        ).fetchone()

    return {
        "total_income":  row["total_income"]  or 0.0,
        "total_expense": row["total_expense"] or 0.0,
    } #Переделать эту часть при создании приложения