from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
import tkinter as tk
try:
    import tksvg
except ImportError:
    tksvg = None

from .components.sidebar_menu import SidebarMenu
from .data.repository import FinanceRepository
from .pages.categories_page import CategoriesPage
from .pages.dashboard_page import DashboardPage
from .pages.expense_page import ExpensePage
from .pages.income_page import IncomePage
from .pages.settings_page import SettingsPage
from .pages.transfer_page import TransferPage


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FinanceDashboardApp(ctk.CTk):
    SIDEBAR_ITEMS = ["Обзор", "Конверт", "Доходы", "Расходы", "Категории", "Настройки"]
    SIDEBAR_ICON_FILES = {
        "Обзор": "gemini-svg.svg",
        "Конверт": "Group 12.svg",
        "Доходы": "Vector (1).svg",
        "Расходы": "fi-1.svg",
        "Категории": "fi-rr-interactive.svg",
        "Настройки": "Vector.svg",
    }

    def __init__(self) -> None:
        super().__init__()
        self.title("Finebank Dashboard")
        self.geometry("1440x860")
        self.minsize(1320, 760)
        self.configure(fg_color="#0B1220")

        self.repo = FinanceRepository(Path(__file__).resolve().parent.parent / "finance.db")
        self.user = self.repo.get_default_user()
        self.assets_dir = Path(__file__).resolve().parent.parent / "assets"
        self.svg_images: dict[str, object | None] = {}
        self.sidebar_icons = self._load_sidebar_icons()
        self.user_icon = self._load_icon("Vector (2).svg", size=(40, 40), color="#10D6B3")
        self.pages = {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = SidebarMenu(
            self,
            items=self.SIDEBAR_ITEMS,
            on_select=self.show_page,
            icons=self.sidebar_icons,
            user_icon=self.user_icon,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content = ctk.CTkFrame(self, fg_color="#0B1220", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self._build_pages()
        self.show_page("Обзор")

    def _build_pages(self) -> None:
        page_classes = {
            "Обзор": DashboardPage,
            "Конверт": TransferPage,
            "Доходы": IncomePage,
            "Расходы": ExpensePage,
            "Категории": CategoriesPage,
            "Настройки": SettingsPage,
        }

        for name, page_class in page_classes.items():
            page = page_class(self.content, self)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = page

    def refresh_user(self) -> None:
        self.user = self.repo.get_default_user()

    def show_page(self, page_name: str) -> None:
        page = self.pages[page_name]
        page.tkraise()
        self.sidebar.set_active(page_name)
        page.on_show()

    def _load_sidebar_icons(self) -> dict[str, dict[str, object | None]]:
        icons: dict[str, dict[str, object | None]] = {}
        for title, filename in self.SIDEBAR_ICON_FILES.items():
            icons[title] = {
                "inactive": self._load_icon(filename, size=(22, 22), color="#8B95A5"),
                "active": self._load_icon(filename, size=(22, 22), color="#22D7AF"),
            }
        return icons

    def _load_icon(self, filename: str, size: tuple[int, int], color: str) -> object | None:
        if tksvg is None:
            return None

        icon_path = self.assets_dir / filename
        if not icon_path.exists():
            return None

        image_key = f"{filename}:{size[0]}x{size[1]}:{color}"
        cached_image = self.svg_images.get(image_key)
        if cached_image is not None:
            return cached_image

        if not getattr(self, "_tksvg_loaded", False):
            tksvg.load(self)

        image = tk.PhotoImage(
            master=self,
            file=str(icon_path),
            format=f"svg -scaletowidth {size[0]}",
        )
        self.svg_images[image_key] = image
        return image
