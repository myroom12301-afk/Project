from __future__ import annotations

from .transaction_list_page import INCOME, TransactionListPage


class IncomePage(TransactionListPage):
    def __init__(self, master, controller) -> None:
        super().__init__(master, controller, tx_type=INCOME, title="Доходы")
