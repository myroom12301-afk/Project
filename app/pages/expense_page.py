from __future__ import annotations

from .placeholder_page import PlaceholderPage


class ExpensePage(PlaceholderPage):
    def __init__(self, master, controller) -> None:
        super().__init__(
            master,
            controller,
            title="Расходы",
            description="Отдельный модуль для логики расходов. Здесь удобно держать таблицы, формы и аналитику именно по тратам.",
        )
