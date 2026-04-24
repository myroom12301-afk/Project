from __future__ import annotations

from .placeholder_page import PlaceholderPage


class TransferPage(PlaceholderPage):
    def __init__(self, master, controller) -> None:
        super().__init__(
            master,
            controller,
            title="Конверт",
            description="Страница вынесена в отдельный файл. Здесь можно подключать отдельную логику переводов или конвертации.",
        )
