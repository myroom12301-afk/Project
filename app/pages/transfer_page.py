from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
from PIL import Image

from .base_page import BasePage

# Папка assets лежит рядом с корнем проекта
ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"


class TransferPage(BasePage):
    def __init__(self, master, controller) -> None:
        super().__init__(master, controller)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=24, fg_color="#202B3C")
        card.grid(row=0, column=0, padx=32, pady=32, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Пример вставки изображения",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#F7F8FC",
        ).pack(anchor="w", padx=28, pady=(28, 16))

        # ШАГ 1 — загружаем файл через Pillow
        pil_image = Image.open(ASSETS_DIR / "img.png")

        # ШАГ 2 — оборачиваем в CTkImage и задаём размер отображения
        # light_image и dark_image могут быть разными для светлой/тёмной темы,
        # но можно передать одно и то же изображение в оба параметра
        ctk_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(320, 220),        # (ширина, высота) в пикселях
        )

        # ШАГ 3 — отображаем через CTkLabel (text="" обязателен, иначе будет «CTkImage»)
        ctk.CTkLabel(
            card,
            image=ctk_image,
            text="",
        ).pack(pady=(0, 12))

        ctk.CTkLabel(
            card,
            text="img.png из папки assets",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#7D8798",
        ).pack(pady=(0, 28))