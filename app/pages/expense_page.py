from __future__ import annotations

from .transaction_list_page import EXPENSE, TransactionListPage


class ExpensePage(TransactionListPage):
    def __init__(self, master, controller) -> None:
        super().__init__(master, controller, tx_type=EXPENSE, title_key="nav.expense")