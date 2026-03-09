from db_sqlite3 import DEFAULT_DB_PATH
from db_sqlite3 import add_account as sqlite_add_account
from db_sqlite3 import add_budget as sqlite_add_budget
from db_sqlite3 import add_category as sqlite_add_category
from db_sqlite3 import add_goal as sqlite_add_goal
from db_sqlite3 import add_transaction as sqlite_add_transaction
from db_sqlite3 import add_user as sqlite_add_user
from db_sqlite3 import recreate_tables


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    recreate_tables(db_path=db_path)


def add_user(name: str, base_currency: str, email: str | None = None, db_path: str = DEFAULT_DB_PATH) -> int:
    return sqlite_add_user(name=name, base_currency=base_currency, email=email, db_path=db_path)


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
    return sqlite_add_account(
        user_id=user_id,
        name=name,
        account_type=account_type,
        currency=currency,
        opening_balance=opening_balance,
        current_balance=current_balance,
        is_archived=is_archived,
        db_path=db_path,
    )


def add_category(
    user_id: int,
    name: str,
    kind: str,
    parent_id: int | None = None,
    icon: str | None = None,
    color: str | None = None,
    is_archived: bool = False,
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    return sqlite_add_category(
        user_id=user_id,
        name=name,
        kind=kind,
        parent_id=parent_id,
        icon=icon,
        color=color,
        is_archived=is_archived,
        db_path=db_path,
    )


def add_transaction(
    user_id: int,
    account_id: int,
    transaction_type: str,
    amount: float,
    currency: str,
    transaction_date: str,
    category_id: int | None = None,
    description: str | None = None,
    merchant: str | None = None,
    status: str = "cleared",
    transfer_group_id: str | None = None,
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    return sqlite_add_transaction(
        user_id=user_id,
        account_id=account_id,
        transaction_type=transaction_type,
        amount=amount,
        currency=currency,
        transaction_date=transaction_date,
        category_id=category_id,
        description=description,
        merchant=merchant,
        status=status,
        transfer_group_id=transfer_group_id,
        db_path=db_path,
    )


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
    return sqlite_add_budget(
        user_id=user_id,
        category_id=category_id,
        period_type=period_type,
        period_start=period_start,
        period_end=period_end,
        amount_limit=amount_limit,
        rollover=rollover,
        db_path=db_path,
    )


def add_goal(
    user_id: int,
    name: str,
    target_amount: float,
    current_amount: float = 0.0,
    target_date: str | None = None,
    linked_account_id: int | None = None,
    status: str = "active",
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    return sqlite_add_goal(
        user_id=user_id,
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=target_date,
        linked_account_id=linked_account_id,
        status=status,
        db_path=db_path,
    )


def seed_minimal_data(db_path: str = DEFAULT_DB_PATH) -> dict[str, int]:
    user_id = sqlite_add_user(
        name="Tanzir Rahman",
        base_currency="USD",
        email="tanzir@example.com",
        db_path=db_path,
    )
    account_id = sqlite_add_account(
        user_id=user_id,
        name="Main Card",
        account_type="card",
        currency="USD",
        opening_balance=0,
        current_balance=0,
        db_path=db_path,
    )
    income_category_id = sqlite_add_category(
        user_id=user_id,
        name="Salary",
        kind="income",
        db_path=db_path,
    )
    expense_category_id = sqlite_add_category(
        user_id=user_id,
        name="Food",
        kind="expense",
        db_path=db_path,
    )
    return {
        "user_id": user_id,
        "account_id": account_id,
        "income_category_id": income_category_id,
        "expense_category_id": expense_category_id,
    }
