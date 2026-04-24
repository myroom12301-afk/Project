from __future__ import annotations

from .placeholder_page import PlaceholderPage


class CategoriesPage(PlaceholderPage):
    def __init__(self, master, controller) -> None:
        super().__init__(
            master,
            controller,
            title="Категории",
            description="Отдельный файл страницы категорий. В него можно добавлять CRUD-логику категорий без перегрузки главного окна.",
        )
