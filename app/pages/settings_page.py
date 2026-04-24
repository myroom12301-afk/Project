from __future__ import annotations

from .placeholder_page import PlaceholderPage


class SettingsPage(PlaceholderPage):
    def __init__(self, master, controller) -> None:
        super().__init__(
            master,
            controller,
            title="Настройки",
            description="Отдельный файл страницы настроек. Здесь можно подключать пользовательские параметры и конфигурацию приложения.",
        )
