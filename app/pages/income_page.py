from __future__ import annotations

from .placeholder_page import PlaceholderPage


class IncomePage(PlaceholderPage):
    def __init__(self, master, controller) -> None:
        super().__init__(
            master,
            controller,
            title="Доходы",
            description="Отдельный модуль для логики доходов. Сюда можно переносить формы создания, фильтры и аналитику по поступлениям.",
        )
