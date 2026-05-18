from __future__ import annotations

import io
import re
from pathlib import Path

import cairosvg
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

from .currencies import get_symbol
from .locale import locale, t
from .sidebar import SidebarMenu
from .repository import FinanceRepository
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
    SIDEBAR_ITEM_KEYS = {
        "Обзор":      "nav.overview",
        "Конверт":    "nav.transfer",
        "Доходы":     "nav.income",
        "Расходы":    "nav.expense",
        "Категории":  "nav.categories",
        "Настройки":  "nav.settings",
    }
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
        try:
            locale.set(self.user["language"] or "Русский")
        except Exception:
            pass
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
            display_names=[t(self.SIDEBAR_ITEM_KEYS[i]) for i in self.SIDEBAR_ITEMS],
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

    def apply_language(self, lang_name: str) -> None:
        locale.set(lang_name)
        self.sidebar.update_display_names([t(self.SIDEBAR_ITEM_KEYS[i]) for i in self.SIDEBAR_ITEMS])
        for page in self.pages.values():
            page.destroy()
        self.pages.clear()
        self._build_pages()
        self.show_page("Настройки")

    @property
    def currency_symbol(self) -> str:
        try:
            return get_symbol(self.user["currency"] or "USD")
        except Exception:
            return "$"

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
        icon_path = self.assets_dir / filename
        if not icon_path.exists():
            return None

        image_key = f"{filename}:{size[0]}x{size[1]}:{color}"
        cached = self.svg_images.get(image_key)
        if cached is not None:
            return cached

        svg_text = icon_path.read_text()
        svg_text = re.sub(r'stroke="(?!none)[^"]*"', f'stroke="{color}"', svg_text)
        svg_text = re.sub(r'fill="(?!none)[^"]*"', f'fill="{color}"', svg_text)

        png_bytes = cairosvg.svg2png(
            bytestring=svg_text.encode(),
            output_width=size[0],
            output_height=size[1],
        )
        pil_image = Image.open(io.BytesIO(png_bytes))
        tk_image = ImageTk.PhotoImage(pil_image)
        self.svg_images[image_key] = tk_image
        return tk_image
